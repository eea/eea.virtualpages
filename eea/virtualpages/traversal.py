"""Virtual-pages traversal.

When the `eea.virtualpages.virtualpages` behavior is enabled on a content
object AND its `virtual_pages_enabled` flag is True, any sub-name
traversed under it resolves to a transient proxy of the object itself.

Subclasses Dexterity's own publishTraverse so WebDAV, views (edit, add,
@*, ++*) and standard sub-object lookup keep working unchanged.
"""

from copy import copy

from Acquisition import aq_base
from plone.dexterity.browser.traversal import DexterityPublishTraverse
from zExceptions import NotFound

from eea.virtualpages.transient import TransientJar

from zope.component import adapter
from zope.event import notify
from zope.interface import alsoProvides, implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserRequest

from eea.virtualpages.events import VirtualPageBuiltEvent
from eea.virtualpages.interfaces import (
    IVirtualPage,
    IVirtualPagesBehavior,
    IVirtualPagesContainer,
)


# Names that must NOT be intercepted: REST API verbs, Plone management views,
# add/edit etc. Standard publication handles them.
RESERVED_NAMES = frozenset({"edit", "add", "delete", "view", "manage", "manage_main"})

# plone.restapi services are registered as views named like
# `GET_application_json_*`. They must always go through standard publishing.
HTTP_METHOD_PREFIXES = (
    "GET_",
    "POST_",
    "PUT_",
    "PATCH_",
    "DELETE_",
    "OPTIONS_",
    "HEAD_",
)


def _is_reserved(name):
    return (
        name in RESERVED_NAMES
        or name.startswith("@")
        or name.startswith("++")
        or name.startswith(HTTP_METHOD_PREFIXES)
    )


def _build_virtual(template, name, request):
    """Transient (non-persistent) shallow copy of `template` with id/name
    overridden, wrapped in `template` so its URL becomes
    `<template_url>/<name>`. Fires VirtualPageBuiltEvent so subscribers
    can mutate the proxy (title, description, blocks, …)."""
    virtual = copy(aq_base(template))

    # Swap the live ZODB connection for a no-op jar so subscribers can
    # mutate attributes (title, description, …) without writes leaking
    # back to the template via the persistence machinery.
    if hasattr(virtual, "_p_jar"):
        try:
            virtual._p_jar = TransientJar()
        except Exception:
            pass

    virtual.is_virtual = True
    virtual.id = name
    virtual.title = f"{virtual.title} - {name}"
    virtual.__name__ = name
    alsoProvides(virtual, IVirtualPage)

    wrapped = virtual.__of__(template)
    event = VirtualPageBuiltEvent(template, wrapped, name, request)
    notify(event)

    not_found = getattr(virtual, "_v_not_found", False)
    if not_found:
        raise NotFound()

    # Stash the set of fields that we (or subscribers) virtualized; the
    # PATCH service uses it to strip those fields from incoming writes.
    # `id` is always virtualized. Volatile (`_v_`) prefix avoids triggering
    # ZODB persistence registration on this transient proxy.
    virtual._v_virtual_overrides = frozenset(
        {
            "id",
            "title",
            "virtual_pages_enabled",
            "virtual_id_parameter",
        }
        | event.overrides
    )
    return wrapped


@implementer(IPublishTraverse)
@adapter(IVirtualPagesContainer, IBrowserRequest)
class VirtualPagesTraverse(DexterityPublishTraverse):
    """Resolve `<context>/<name>` to a virtual proxy of `<context>` when
    enabled; otherwise behave exactly like the standard Dexterity
    traverser (WebDAV, edit forms, REST endpoints all keep working)."""

    def publishTraverse(self, request, name):
        # Already inside a virtual proxy → never recurse, fall through.
        if IVirtualPage.providedBy(self.context):
            return super().publishTraverse(request, name)

        behavior = IVirtualPagesBehavior(self.context, None)
        enabled = bool(
            behavior is not None and getattr(behavior, "virtual_pages_enabled", False)
        )

        # Per-instance toggle off → standard publishing.
        if not enabled:
            return super().publishTraverse(request, name)

        # Reserved names always go through standard publishing.
        if _is_reserved(name):
            return super().publishTraverse(request, name)

        # Real persistent child wins over the virtual mapping.
        real = getattr(self.context, "get", lambda _: None)(name)
        if real is not None:
            return real

        return _build_virtual(self.context, name, request)
