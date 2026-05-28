# Subscribers

Mutate the virtual proxy at request time without touching the template.

## Registration

Subscribe to `IVirtualPageBuiltEvent` from `eea.ied.policy.events`.

```python
# my_addon/subscribers.py
from zope.component import adapter
from eea.ied.policy.events import IVirtualPageBuiltEvent


@adapter(IVirtualPageBuiltEvent)
def enrich_my_container(event):
    if event.container.id != "my-container":
        return
    data = lookup(event.name)
    if data is None:
        # GET service will return 404; PATCH/POST/DELETE still 405.
        event.virtual._v_virtual_missing = True
        return
    event.set_field("title", data["name"])
    event.set_field("description", data["address"])
    # Volatile attributes available to custom blocks/serializers.
    event.virtual._v_my_data = data
```

```xml
<!-- my_addon/configure.zcml -->
<subscriber handler=".subscribers.enrich_my_container" />
```

## `event.set_field(name, value)`

Sets the attribute on the proxy AND registers `name` in
`event.overrides`. Using this instead of `event.virtual.X = Y` is
strongly recommended — overrides drive:

* PATCH stripping — incoming writes for those fields are discarded
  before applying the rest to the template.
* `@types` filtering — Volto's edit form hides the field.

If you set a field directly without registering it, a Volto user
saving the edit form will silently overwrite the template with the
virtualized value. Subtle template corruption.

## Volatile vs persistent attributes

* `_v_*` (e.g. `_v_my_data`, `_v_virtual_missing`) — never trigger
  ZODB registration. Always safe to set on the proxy.
* `_p_*` — reserved by ZODB. Don't touch.
* Anything else — goes through the no-op `TransientJar`. Safe but
  treat the proxy as throwaway.

## Container detection patterns

```python
# By id (simple, fragile if renamed)
if event.container.id != "facility":
    return

# By absolute path (also fragile)
if event.container.absolute_url_path() != "/site/facility":
    return

# By marker interface (best — survives renames)
from my_addon.interfaces import IFacilityContainer
if not IFacilityContainer.providedBy(event.container):
    return

# By behavior + setting
behavior = IVirtualPagesBehavior(event.container, None)
if behavior is None or behavior.virtual_id_parameter != "facilityLocalId":
    return
```

## 404 hook

```python
event.virtual._v_virtual_missing = True
```

GET on the virtual page returns:

```json
HTTP/1.1 404 Not Found
{"type": "NotFound", "message": "Virtual page not found."}
```

## Inspecting overrides downstream

Custom views, serializers, or another subscriber can read:

```python
from Acquisition import aq_base
overrides = getattr(aq_base(virtual), "_v_virtual_overrides", frozenset())
```

Note: `_v_virtual_overrides` is set AFTER all subscribers run, in
`_build_virtual`. Subscribers see only `event.overrides` (a `set`).
