"""Interfaces for eea.virtualpages."""

from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from eea.virtualpages import EEAMessageFactory as _


class IEeaVirtualPagesLayer(IDefaultBrowserLayer):
    """Marker browser layer for eea.virtualpages."""


class IVirtualPagesContainer(IDexterityContent):
    """Marker auto-applied to instances whose type has the VirtualPages
    behavior enabled. Extends IDexterityContent so our adapter wins over
    plone.dexterity's default IPublishTraverse adapter via specificity."""


class IVirtualPage(IDexterityContent):
    """Marker for the transient proxy returned by the traverser. Use to
    detect virtual context in views, blocks, REST serializers. Extends
    IDexterityContent so adapters/services registered for the marker win
    over generic Dexterity / IContentish registrations via specificity."""


@provider(IFormFieldProvider)
class IVirtualPagesBehavior(model.Schema):
    """Per-instance toggle for virtual sub-page traversal.

    When `virtual_pages_enabled` is True, any sub-name traversed under
    this object resolves to a transient proxy of the object itself. The
    object is its own template.
    """

    fieldset(
        "virtualpages",
        label=_("Virtual Pages"),
        fields=["virtual_pages_enabled", "virtual_id_parameter"],
    )

    virtual_pages_enabled = schema.Bool(
        title=_("Activate virtual pages"),
        description=_(
            "When on, any /<this-page>/<id> resolves to a virtual copy "
            "of this page with the sub-name as id."
        ),
        required=False,
        default=False,
    )

    virtual_id_parameter = schema.TextLine(
        title=_("Virtual id parameter name"),
        description=_(
            "Name of the data_query parameter to populate with the "
            "virtual page id (e.g. `localId`). Requires the "
            "'eea.restapi.parameters' (data connections) behavior on "
            "this content type. Leave empty to disable."
        ),
        required=False,
    )


@provider(IFormFieldProvider)
class IFileField(model.Schema):
    """Optional file field for content types."""

    file = NamedBlobFile(
        title=_("File"),
        required=False,
    )
