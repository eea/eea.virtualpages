# FUTURE work

Items deliberately deferred. Not blockers.

## Catalog / sitemap enumeration

Virtual pages aren't in `portal_catalog` so `@search`, sitemaps and
navigation don't see them. Add an `IVirtualPagesEnumerator` adapter
so subscribers can declare "for container X, the valid ids are Y" and
a custom sitemap walker yields virtual URLs alongside real content.

## Volto frontend helper addon

* `useVirtualPage()` React hook reading `is_virtual` + `virtual_id`
  from the content payload (already exposed by `VirtualPageSerializer`).
* Edit-mode banner: "Editing the template — changes apply to all
  virtual pages."
* Block wrapper that hides itself when on the real template (or vice
  versa).
* Toolbar tweak that points the Edit button at the template URL.

## Permission scoping per virtual id

Today the proxy inherits the template's View permission. Sometimes
you need per-id ACL (facility A only viewable by company A). Add an
`IVirtualPagePermissionChecker` interface; default impl returns True;
subscribers/adapters can decide per request.

## plone.app.multilingual

Container under a translated subtree (e.g. `/en/items` vs `/de/items`)
not tested. Likely needs marker copying when traversing into a
language root, plus translation fallback rules for the proxy's
content negotiation.

## Tests

PloneTestCase harness covering:
* Behavior toggle on/off.
* Traversal builds proxy with correct id/url/markers.
* PATCH strips `overrides` and writes to template.
* `@types` filters fields.
* `@workflow` POST → 405.
* Lock on virtual hits the template.
* `VirtualPageBuiltEvent` fires; `event.set_field` registers override.
* ETag changes when template is edited.
* `_v_virtual_missing` → 404.
* Anti-recursion (proxy under proxy).
