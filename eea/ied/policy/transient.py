"""Stand-ins for ZODB Connection / DB used by the virtual-page proxy.

A virtual proxy is a shallow copy of the template object. Persistent
machinery would otherwise try to register every attribute write against
the live ZODB connection (corrupting the template) or crash when the
connection is missing. The fakes here swallow every Connection and DB
method so writes succeed in memory and never reach storage, while the
serializer/intid code paths that reach for `connection.db().database_name`
keep working.
"""


def _noop(*args, **kwargs):
    return None


class TransientDB:
    """Fake ZODB DB stand-in with the attributes Plone code touches."""

    database_name = "transient"
    databases = {"transient": None}

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return _noop


_TRANSIENT_DB = TransientDB()


class TransientJar:
    """Fake ZODB Connection: every method is a silent no-op."""

    def db(self):
        return _TRANSIENT_DB

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return _noop

    def __bool__(self):
        return False
