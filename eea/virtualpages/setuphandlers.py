"""Install / uninstall handlers."""

from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


BEHAVIOR_NAME = "eea.virtualpages.virtualpages"


@implementer(INonInstallable)
class HiddenProfiles:
    """Hide internal profiles from the Plone add-ons control panel."""

    def getNonInstallableProfiles(self):
        return ["eea.virtualpages:uninstall"]

    def getNonInstallableProducts(self):
        return []


def _types_with_behavior():
    portal_types = api.portal.get_tool("portal_types")
    for fti in portal_types.objectValues():
        behaviors = list(getattr(fti, "behaviors", ()) or ())
        if BEHAVIOR_NAME in behaviors:
            yield fti, behaviors


def post_install(context):
    """No-op placeholder for future install steps."""


def post_uninstall(context):
    """Strip the VirtualPages behavior from every Dexterity FTI that has it
    so leftover content doesn't keep providing IVirtualPagesContainer after
    the package is gone."""
    for fti, behaviors in _types_with_behavior():
        fti.behaviors = tuple(b for b in behaviors if b != BEHAVIOR_NAME)
