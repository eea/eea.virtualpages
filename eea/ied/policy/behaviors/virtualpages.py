"""VirtualPages behavior factory."""

from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.interface import implementer

from eea.ied.policy.interfaces import IVirtualPagesBehavior


@implementer(IVirtualPagesBehavior)
@adapter(IDexterityContent)
class VirtualPages:
    """Stores the behavior's fields directly on the content object."""

    def __init__(self, context):
        self.context = context

    @property
    def virtual_pages_enabled(self):
        return bool(getattr(self.context, "virtual_pages_enabled", False))

    @virtual_pages_enabled.setter
    def virtual_pages_enabled(self, value):
        self.context.virtual_pages_enabled = bool(value)

    @property
    def virtual_id_parameter(self):
        return getattr(self.context, "virtual_id_parameter", None) or None

    @virtual_id_parameter.setter
    def virtual_id_parameter(self, value):
        self.context.virtual_id_parameter = value or None
