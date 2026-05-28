"""eea.ied.policy package."""

from zope.i18nmessageid import MessageFactory

EEAIEDMessageFactory = MessageFactory("eea")


def initialize(context):
    """Zope product init hook — apply runtime patches once."""
    from eea.ied.policy import patches

    patches.install()
