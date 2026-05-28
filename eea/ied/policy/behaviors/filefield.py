"""File field behavior factory."""

from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.interface import implementer

from eea.ied.policy.interfaces import IFileField


@implementer(IFileField)
@adapter(IDexterityContent)
class FileField:
    """Stores the behavior's fields directly on the content object."""

    def __init__(self, context):
        self.context = context

    @property
    def file(self):
        return getattr(self.context, 'file', None)

    @file.setter
    def file(self, value):
        self.context.file = value
