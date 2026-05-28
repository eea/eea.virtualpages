"""Events fired during virtual-page traversal.

Subscribers can mutate the proxy before it reaches the publisher: tweak
title, description, blocks, set extra attributes, fetch external data,
etc. Standard zope.event/zope.component subscriber registration.

Example:

    from zope.component import adapter
    from eea.ied.policy.events import IVirtualPageBuiltEvent

    @adapter(IVirtualPageBuiltEvent)
    def enrich_page(event):
        if event.container.id != "my-container":
            return
        data = lookup(event.name)
        if data is None:
            # Tell the GET service to return 404 instead of the bare
            # template.
            event.virtual._v_virtual_missing = True
            return
        event.set_field("title", data["name"])
        event.set_field("description", data["address"])
"""

from zope.interface import Attribute, Interface, implementer


class IVirtualPageBuiltEvent(Interface):
    """A virtual page proxy has just been built and is about to be served."""

    container = Attribute(
        "The IVirtualPagesContainer the request traversed."
    )
    virtual = Attribute(
        "The transient proxy object (provides IVirtualPage)."
    )
    name = Attribute("The URL segment used as the virtual id.")
    request = Attribute("The current request.")


@implementer(IVirtualPageBuiltEvent)
class VirtualPageBuiltEvent:
    def __init__(self, container, virtual, name, request):
        self.container = container
        self.virtual = virtual
        self.name = name
        self.request = request
        # Subscribers that mutate fields on the proxy should add the
        # field name here. PATCH requests on the virtual page strip
        # these fields from the payload before applying the write to
        # the real template, so virtualized values aren't persisted.
        # The custom @types service strips them from the schema too.
        self.overrides = set()

    def set_field(self, name, value):
        """Set a field on the proxy AND register it in `overrides`.

        Use this in subscribers instead of `event.virtual.X = Y` —
        forgetting `event.overrides.add("X")` would let a PATCH from
        Volto silently overwrite the template with the virtualized
        value.
        """
        setattr(self.virtual, name, value)
        self.overrides.add(name)
