"""Subscribers for virtual-page enrichment."""

import logging
import json

from Acquisition import aq_base

from zope.component import adapter, queryMultiAdapter

from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement

from eea.virtualpages.events import IVirtualPageBuiltEvent
from eea.virtualpages.interfaces import IVirtualPagesBehavior

logger = logging.getLogger("eea.virtualpages.subscribers")

DATA_QUERY_OPERATION = "plone.app.querystring.operation.selection.is"


@adapter(IVirtualPageBuiltEvent)
def inject_virtual_id_param(event):
    """Inject the virtual page id into the proxy's `data_query` field.

    Reads `virtual_id_parameter` from the container's VirtualPages
    behavior. If set, the proxy's `data_query` is rewritten so the named
    parameter has `v=[event.name]`. Existing entry with the same `i` is
    replaced; other entries are kept.

    Requires the `eea.restapi.parameters` behavior (provides
    `data_query`) on the same content type.
    """
    behavior = IVirtualPagesBehavior(event.container, None)
    if behavior is None:
        return
    param_name = getattr(behavior, "virtual_id_parameter", None)
    if not param_name:
        return

    current = list(getattr(event.virtual, "data_query", None) or [])
    rebuilt = [e for e in current if e.get("i") != param_name]
    rebuilt.append(
        {
            "i": param_name,
            "o": DATA_QUERY_OPERATION,
            "v": [event.name],
        }
    )
    event.set_field("data_query", rebuilt)


@adapter(IVirtualPageBuiltEvent)
def facility_inject_site_inspire_id(event):

    def build_data_query(data_query, connector_data):
        rows = connector_data.get("data", {}).get("results") or []
        if not rows:
            event.virtual._v_not_found = True
            return data_query

        # results may be column-oriented dict or row list — adjust to your shape
        row = (
            rows[0]
            if isinstance(rows, list)
            else {k: v[0] for k, v in rows.items() if v}
        )
        site_id = row.get("siteInspireID")
        if not site_id:
            return data_query

        rebuilt = [e for e in data_query if e.get("i") != "siteInspireID"]
        rebuilt.append(
            {
                "i": "siteInspireID",
                "o": "plone.app.querystring.operation.selection.is",
                "v": [site_id],
            }
        )
        return rebuilt

    try:
        virtual = event.virtual
        aq_virtual = aq_base(virtual)
        container = event.container
        request = event.request

        if request.method != "GET":
            return

        stack = request.get("TraversalRequestNameStack") or []

        # skip when more segments remain (expanders, @workflow, @types, etc.)
        if any(s.startswith("@") or s.startswith("++") for s in stack):
            return

        data_query = getattr(aq_virtual, "data_query", None) or []
        if not data_query or container.id != "facility":
            return

        connector_data = getattr(aq_virtual, "connector_data", None)
        if connector_data:
            rebuilt = build_data_query(data_query, connector_data)
            event.set_field("data_query", rebuilt)

        connector = queryMultiAdapter(
            (virtual, request), IExpandableElement, name="connector-data"
        )
        if connector is None:
            return

        try:
            result = connector(expand=True)
        except Exception:
            logger.exception("facility_inject_site_inspire_id connector failed")

        connector_data = result.get("connector-data", None)

        if connector_data:
            body = json_body(request)
            rebuilt = build_data_query(data_query, connector_data)
            body["data_query"] = rebuilt
            event.set_field("data_query", rebuilt)
            aq_virtual.connector_data = connector_data
            request["BODY"] = json.dumps(body)
    except Exception:
        logger.exception("facility_inject_site_inspire_id failed")
