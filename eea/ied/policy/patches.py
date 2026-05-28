"""Monkey patches for plone.rest.

plone.rest wraps every traversed object in `RESTWrapper`. Its
`publishTraverse` instantiates `DefaultPublishTraverse` directly, which
bypasses any `IPublishTraverse` adapter registered for the context
interface. That breaks our virtual-pages traversal under `++api++`.

We patch `RESTWrapper.publishTraverse` to first consult the registered
`IPublishTraverse` adapter when the wrapped context carries the
`IVirtualPagesContainer` marker. For all other contexts the original
behaviour is preserved.
"""

from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse

from eea.ied.policy.interfaces import IVirtualPagesContainer


def install():
    from plone.rest.traverse import RESTWrapper

    if getattr(RESTWrapper.publishTraverse, "_eea_ied_patched", False):
        return

    original = RESTWrapper.publishTraverse

    def publishTraverse(self, request, name):
        if IVirtualPagesContainer.providedBy(self.context):
            adapter = queryMultiAdapter(
                (self.context, request), IPublishTraverse
            )
            if adapter is not None:
                try:
                    obj = adapter.publishTraverse(request, name)
                except (KeyError, AttributeError):
                    obj = None
                if obj is not None:
                    return RESTWrapper(obj, request)
        return original(self, request, name)

    publishTraverse._eea_ied_patched = True
    RESTWrapper.publishTraverse = publishTraverse
