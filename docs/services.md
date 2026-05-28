# REST services on virtual pages

All registered for the `IVirtualPage` marker, which extends
`IDexterityContent` so they win over plone.restapi's defaults via
adapter specificity.

## `GET /<container>/<id>`

`VirtualPageGet` (subclass of `plone.restapi.services.content.get.ContentGet`).

Behaviour:
1. If `_v_virtual_missing` is truthy → `404 NotFound`.
2. Compute deterministic ETag from
   `template._p_serial + virtual_id + sorted(overrides)`.
3. If `If-None-Match` matches → `304 Not Modified`.
4. Set `ETag` response header.
5. Defer to standard `ContentGet.reply()` → standard payload, plus
   `is_virtual: true` and `virtual_id` injected by the custom
   serializer.

## `POST /<container>/<id>`

`VirtualPagePost` → `405 Method Not Allowed` with `Allow: GET, PATCH`.
Body explains: edit the template directly.

## `DELETE /<container>/<id>`

`VirtualPageDelete` → `405 Method Not Allowed` (same shape).

## `PATCH /<container>/<id>`

`VirtualPagePatch`:
* Reads `_v_virtual_overrides` from the proxy.
* Drops those fields from the JSON body (`request["BODY"]` rewritten).
* Forwards the request to the real template (`self.context = template`).
* Standard `ContentPatch.reply()` then applies the remaining fields
  persistently.

Example:
```bash
curl -X PATCH .../<container>/<id> \
  -d '{"title":"hacked","description":"writes","blocks":{"new":"data"}}'
# title: stripped (in overrides)
# description, blocks: applied to /<container>
```

## `GET /<container>/<id>/@types/<portal_type>`

`VirtualPageTypesGet`:
* Calls standard `TypesGet.reply()` to get the schema.
* Removes any field whose name is in `_v_virtual_overrides` from
  `properties`, `fieldsets[*].fields`, and `required`.
* Volto's edit form auto-skips them.

## `POST /<container>/<id>/@workflow` and `PATCH /@workflow`

`VirtualPageWorkflowBlock` → `405 Method Not Allowed` with
`Allow: GET`. GET `@workflow` keeps using the standard service and
returns the template's workflow state.

## Locking

`VirtualPageLockable` adapter forwards every `wl_*` operation to the
real template via `aq_parent(aq_inner(virtual))`. Lock attempts that
Plone's edit form fires (`lockOnEditBegins`) succeed without
corrupting the proxy. The template ends up locked, which is the
correct semantic.

## Things still routed to standard plone.restapi

Anything not listed above (`@navigation`, `@breadcrumbs`, `@inherit`,
`@history`, etc.) goes through the default services. They generally
work because the proxy looks like a legitimate `Document` to them.
