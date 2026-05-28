"""PATCH service for virtual pages.

Virtual proxies are transient — writes to them never persist (and would
crash on `_p_jar=None`). For PATCH requests we instead apply the write
to the real template, after stripping any fields that subscribers
virtualized for this proxy.
"""

import json

from Acquisition import aq_base, aq_inner, aq_parent
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch


class VirtualPagePatch(ContentPatch):
    """Forward virtual-page PATCH writes to the underlying template."""

    def reply(self):
        virtual = self.context
        template = aq_parent(aq_inner(virtual))

        overrides = getattr(
            aq_base(virtual), "_v_virtual_overrides", frozenset()
        )
        if overrides:
            try:
                data = json_body(self.request)
            except Exception:
                data = None
            if isinstance(data, dict):
                stripped = {
                    k: v for k, v in data.items() if k not in overrides
                }
                self.request["BODY"] = json.dumps(stripped).encode("utf-8")

        # Apply the write to the real persistent template.
        self.context = template
        return super().reply()
