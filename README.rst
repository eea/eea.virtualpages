eea.virtualpages
================

Generic virtual-pages traversal for Plone 6.

Editor enables the **Virtual Pages** behavior on any Dexterity content
type. Once on, every sub-name traversed under an instance of that type
resolves to a transient, read-only proxy of the instance itself — the
page acts as its own template.

Use case: dynamic detail pages such as ``/items/:id``,
``/products/:sku``, ``/records/:code``. One page edited normally in
Plone, infinite virtual children rendered by Volto without any frontend
route, middleware, or extra configuration.

Install
-------

1. Add ``eea.virtualpages`` to buildout ``develop`` and ``eggs``. Restart Zope.
2. Plone Site Setup → Add-ons → install **eea.virtualpages**.
3. Site Setup → Dexterity Content Types → choose a type (e.g. *Document*)
   → Behaviors → enable **Virtual Pages**.
4. Create the page (e.g. ``/items``). Edit blocks normally.
5. Browse ``/++api++/items/anything-here`` — returns the page's
   serialized content with id ``anything-here``. ``@navigation``,
   ``@breadcrumbs``, ``@inherit`` all work natively.

Notes
-----

* Real persistent children win over virtual traversal: if
  ``/items/about`` exists as a real object, that wins.
* Reserved names (``edit``, ``add``, ``@*``, ``++*``) fall through to
  standard publication so REST endpoints and management views keep working.
* The proxy is a transient shallow copy. PATCH writes are routed to the
  template; fields listed in ``event.overrides`` are stripped from the
  payload first.
* Marker interface ``IVirtualPage`` is applied to the proxy so views,
  blocks or serializers can detect virtual context.

Customizing virtual pages
-------------------------

Subscribe to ``IVirtualPageBuiltEvent`` to mutate the proxy on every
request (set title, description, custom attrs). Use
``event.set_field(name, value)`` so the field is registered as a
virtual override automatically (PATCH stripping + ``@types``
filtering). See ``events.py`` docstring or ``docs/subscribers.md``.

For ``data_query`` injection (used by data-connections blocks),
configure the **Virtual id parameter name** field on the container's
edit form — the bundled subscriber handles the rest.

Documentation
-------------

* ``docs/architecture.md`` — request lifecycle + design rationale.
* ``docs/subscribers.md`` — how to write subscribers, override semantics,
  404 hook, container detection patterns.
* ``docs/services.md`` — REST services on virtual proxies (GET, POST,
  DELETE, PATCH, ``@types``, ``@workflow``, locking).
* ``docs/caching.md`` — ETag mechanism, what invalidates the cache.
* ``FUTURE.md`` — deferred work (catalog enumeration, Volto helpers,
  permission scoping, multilingual, tests).
