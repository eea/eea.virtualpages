"""Content services for virtual pages.

* `VirtualPageGet`  — adds 404 hook (when `_v_virtual_missing` is set)
                      and ETag/If-None-Match support on top of the
                      standard ContentGet.
* `VirtualPagePost` / `VirtualPageDelete` — return 405 because writes
                      to a transient proxy are nonsensical; redirect
                      message points at the real template.
"""

from hashlib import sha1

from Acquisition import aq_base, aq_inner, aq_parent
from plone.restapi.services import Service
from plone.restapi.services.content.get import ContentGet


def _allow_header(response):
    response.setHeader("Allow", "GET, PATCH")


def _method_not_allowed(service, method):
    template_url = aq_parent(aq_inner(service.context)).absolute_url()
    service.request.response.setStatus(405)
    _allow_header(service.request.response)
    return {
        "error": {
            "type": "MethodNotAllowed",
            "message": (
                f"{method} is not allowed on a virtual page. "
                f"Edit the template directly: {template_url}"
            ),
        }
    }


def _compute_etag(virtual):
    """Deterministic ETag for a virtual proxy.

    Made of the template's ZODB serial (changes whenever the template
    is edited), the virtual id, and the sorted overrides set (changes
    when subscriber logic changes which fields are virtualized).
    """
    base = aq_base(virtual)
    template = aq_parent(aq_inner(virtual))
    template_serial = getattr(aq_base(template), "_p_serial", b"") or b""
    overrides = getattr(base, "_v_virtual_overrides", ()) or ()
    parts = [
        template_serial.hex() if isinstance(template_serial, bytes)
        else str(template_serial),
        getattr(base, "id", ""),
        ",".join(sorted(overrides)),
    ]
    digest = sha1("|".join(parts).encode("utf-8")).hexdigest()
    return f'"{digest}"'


class VirtualPageGet(ContentGet):
    """GET on a virtual proxy: 404 hook + ETag."""

    def reply(self):
        # 404 hook — subscribers can mark a proxy as "no real
        # underlying entity" (e.g. unknown id in external DB).
        if getattr(aq_base(self.context), "_v_virtual_missing", False):
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": "Virtual page not found.",
            }

        # ETag / 304 short-circuit.
        etag = _compute_etag(self.context)
        if self.request.getHeader("If-None-Match") == etag:
            self.request.response.setStatus(304)
            return None
        self.request.response.setHeader("ETag", etag)

        return super().reply()


class VirtualPagePost(Service):
    """POST on a virtual page: 405."""

    def reply(self):
        return _method_not_allowed(self, "POST")


class VirtualPageDelete(Service):
    """DELETE on a virtual page: 405."""

    def reply(self):
        return _method_not_allowed(self, "DELETE")
