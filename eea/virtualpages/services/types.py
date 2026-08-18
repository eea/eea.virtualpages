"""@types service for virtual pages.

Hides fields listed in `_v_virtual_overrides` from the schema returned by
`/<container>/<id>/@types/<portal_type>`. Volto's edit form uses this
schema to decide which fields to render — filtering out virtualized
fields makes them disappear from the UI.
"""

from Acquisition import aq_base
from plone.restapi.services.types.get import TypesGet


class VirtualPageTypesGet(TypesGet):
    """TypesGet variant that strips virtualized fields from the schema."""

    def reply(self):
        result = super().reply()
        if not isinstance(result, dict):
            return result

        overrides = getattr(aq_base(self.context), "_v_virtual_overrides", None)
        if not overrides:
            return result

        # Drop properties.
        properties = result.get("properties")
        if isinstance(properties, dict):
            for field in overrides:
                properties.pop(field, None)

        # Drop entries from each fieldset's `fields` list.
        for fieldset in result.get("fieldsets") or []:
            fields = fieldset.get("fields")
            if isinstance(fields, list):
                fieldset["fields"] = [f for f in fields if f not in overrides]

        # Drop from `required` list if present.
        required = result.get("required")
        if isinstance(required, list):
            result["required"] = [f for f in required if f not in overrides]

        return result
