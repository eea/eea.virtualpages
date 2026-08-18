"""ILockable adapter for virtual proxies.

Locking a virtual proxy makes no sense — it's transient. Worse, the
default `TTWLockable` reaches for `_p_jar.isReadOnly()` etc. and our
no-op jar can't supply real lock state, so the request crashes (you'll
hit it as soon as Plone's edit-form fires `lockOnEditBegins`).

Solution: redirect every lock operation to the real template. The
template is the only persistent object, so any acquired lock there
applies meaningfully. WebDAV / Plone edit-form behaviour is preserved.
"""

from Acquisition import aq_inner, aq_parent
from plone.locking.lockable import TTWLockable
from zope.component import adapter

from eea.virtualpages.interfaces import IVirtualPage


@adapter(IVirtualPage)
class VirtualPageLockable(TTWLockable):
    """Forward every wl_* call to the template object."""

    def __init__(self, context):
        # `aq_inner` strips any view-wrapping; `aq_parent` then yields
        # the real template (the proxy was built with `__of__(template)`).
        super().__init__(aq_parent(aq_inner(context)))
