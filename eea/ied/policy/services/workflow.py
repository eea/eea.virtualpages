"""@workflow blocker for virtual pages.

GET @workflow returns the template's workflow state, which is the right
answer (every virtual proxy shares it). POST/PATCH @workflow would try
to transition a transient object — silently lost or, worse, applied to
the wrong context. Block both methods.
"""

from Acquisition import aq_inner, aq_parent
from plone.restapi.services import Service


class VirtualPageWorkflowBlock(Service):
    """Reject workflow mutations on a virtual page."""

    def reply(self):
        method = self.request.get("REQUEST_METHOD", "POST")
        template_url = aq_parent(aq_inner(self.context)).absolute_url()
        self.request.response.setStatus(405)
        self.request.response.setHeader("Allow", "GET")
        return {
            "error": {
                "type": "MethodNotAllowed",
                "message": (
                    f"{method} @workflow is not allowed on a virtual "
                    f"page. Transition the template directly: "
                    f"{template_url}/@workflow"
                ),
            }
        }
