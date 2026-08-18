"""ISerializeToJson for virtual pages.

Wraps the standard plone.restapi serializer so the JSON payload carries
two extra top-level keys:

* `is_virtual` (always `True` for proxies)
* `virtual_id` (the URL segment used to build the proxy)

Frontends can detect the virtual context without sniffing the URL.
"""

from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from zope.component import adapter
from zope.interface import Interface, implementer
from plone.restapi.interfaces import ISerializeToJson

from eea.virtualpages.interfaces import IVirtualPage


@implementer(ISerializeToJson)
@adapter(IVirtualPage, Interface)
class VirtualPageSerializer(SerializeFolderToJson):
    """Annotate the standard serializer output with virtual flags."""

    def __call__(self, version=None, include_items=True):
        result = super().__call__(version=version, include_items=include_items)
        if isinstance(result, dict):
            result["is_virtual"] = True
            result["virtual_id"] = self.context.id
        return result
