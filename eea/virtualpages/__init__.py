"""Virtual pages for Plone Dexterity content."""

from zope.i18nmessageid import MessageFactory

EEAMessageFactory = MessageFactory("eea")


def initialize(context):
    """Zope product init hook — apply runtime patches once."""
    from eea.virtualpages import patches

    patches.install()
