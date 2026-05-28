# Architecture

## What this addon does

Turns any Plone Dexterity page into a "template" that responds at
infinite virtual sub-URLs. `/folder` stays a normal page; `/folder/<id>`
returns a transient proxy of `/folder` with the `id` segment as its id
and any per-request mutations subscribers apply.

## Lifecycle of a request

```
URL: /<container>/<id>[/sub-path]

  ZPublisher
       │
       ▼
  /<container>  ── real Plone object, has IVirtualPagesContainer marker
       │
       ▼  publishTraverse(<id>)
  VirtualPagesTraverse  (eea.ied.policy.traversal)
       │
       ├── reserved name?  ──► standard publishing (DexterityPublishTraverse)
       ├── real child?     ──► return that child
       │
       ▼  _build_virtual(template, id, request)
  copy(aq_base(template))
   ├── virtual.id = <id>
   ├── virtual.title = "<template.title> - <id>"   (default; subscribers may override)
   ├── alsoProvides(virtual, IVirtualPage)
   ├── virtual._p_jar = TransientJar()             (no-op ZODB connection)
   └── virtual.__of__(template)                    (acquisition wrapper)
       │
       ▼ notify(VirtualPageBuiltEvent)
  Subscribers (eea.ied.policy.subscribers + your own)
   ├── inject_virtual_id_param   → updates `data_query`
   ├── enrich_<your-container>   → set title, description, custom attrs
   ├── event.set_field(name, v)  → mutate + register override
   └── event.virtual._v_virtual_missing = True   → triggers 404 in GET
       │
       ▼
  virtual._v_virtual_overrides = frozenset(...)   (id, title, virtual_pages_*, … + subscriber overrides)
       │
       ▼
  REST service dispatch:
   ├── GET     → VirtualPageGet (404 hook + ETag + standard payload)
   ├── PATCH   → VirtualPagePatch (strip overrides, write to template)
   ├── POST    → 405
   ├── DELETE  → 405
   ├── @types  → VirtualPageTypesGet (filter overrides from schema)
   └── @workflow POST/PATCH → 405
       │
       ▼
  Serializer:
   └── VirtualPageSerializer adds is_virtual + virtual_id keys
       │
       ▼
  HTTP response
```

## Why a transient shallow copy

* Editor wants ONE place to edit blocks → single template.
* Each request gets a unique `id` → cannot reuse the persistent
  template object directly (the URL/serialized id would always be the
  template's).
* Acquisition + a non-persistent shallow copy gives a fully
  Plone-aware object with the right URL, navigation context, and view
  dispatch — without polluting ZODB.

## Why the fake jar

Persistent objects call `_p_jar.register(self)` on every non-`_v_*`,
non-`_p_*` attribute write. With `_p_jar = None` that crash on the
first subscriber that sets `virtual.title = ...`. `TransientJar`
silently swallows every Connection method. `_v_virtual_missing` and
`_v_virtual_overrides` use the volatile `_v_` prefix so they bypass
persistence entirely (faster + correct).

## Why we patch plone.rest

`RESTWrapper.publishTraverse` instantiates `DefaultPublishTraverse`
directly, bypassing every registered `IPublishTraverse` adapter. Under
`/++api++/<container>/<id>` our adapter would never fire. The patch in
`patches.py` consults the IPublishTraverse adapter when the wrapped
context provides `IVirtualPagesContainer` — minimal scope, no other
codepaths affected.
