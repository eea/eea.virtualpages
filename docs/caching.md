# Caching

## ETag

`VirtualPageGet` emits a deterministic `ETag` on every successful GET:

```
sha1( hex(template._p_serial) | virtual_id | "field1,field2,..." )
```

* `template._p_serial` is the ZODB transaction id of the template's
  last persistent change. Editing blocks on the template bumps it →
  ETag changes for every virtual page derived from it.
* `virtual_id` is the URL segment (`/<container>/<id>`).
* `field1,field2,...` is the sorted list from
  `_v_virtual_overrides`. If subscriber logic changes which fields
  are virtualized (e.g. you start overriding `description`), every
  ETag flips.

The proxy's `_p_serial` is the template's serial because we built it
with `copy(aq_base(template))`. No extra bookkeeping required.

## If-None-Match → 304

```bash
ETAG='"abc123..."'
curl -is -H "If-None-Match: $ETAG" .../<container>/<id>
# HTTP/1.1 304 Not Modified
```

Empty body, no further work, no subscriber re-run on the server side
either (we short-circuit before `super().reply()`).

## What invalidates a cached response

| Action                                   | ETag changes? |
|------------------------------------------|---------------|
| Edit the template (any block, title, …)  | YES           |
| Subscriber adds/removes a field override | YES           |
| Same id, same template, same code        | NO            |
| Different id (`/<container>/A` vs `/B`)  | YES           |

## What does NOT invalidate

External data your subscriber fetches (e.g. discodata SQL row).
`_p_serial` only knows about the Plone object. If the row changes but
nothing else does, the cached ETag stays the same and clients get
stale data.

Workarounds:
* Add a freshness component to the ETag — e.g. include
  `data["last_updated"]` from the external row in the override set or
  in a custom header consumed by the subscriber.
* Set `Cache-Control: no-cache` from the subscriber for sensitive
  routes.
* Use a short max-age via plone.app.caching ruleset.

## CDN / varnish

The ETag header is standard HTTP — varnish, CloudFront, browsers all
honour it. To enable CDN caching you'll typically add a cache-control
directive in the response too (Plone's `plone.app.caching` ruleset
`plone.content.dynamic` covers the standard content GET; check whether
it intercepts our subclass).
