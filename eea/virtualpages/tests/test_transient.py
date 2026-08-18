"""Unit tests for eea.virtualpages.transient stand-ins.

TransientDB / TransientJar fake the ZODB Connection / DB so the virtual
proxy can be mutated in memory without writes leaking to the template.
Pure logic, no Plone portal needed.
"""

import unittest

from eea.virtualpages.transient import TransientDB, TransientJar


class TestTransientDB(unittest.TestCase):
    """Tests for TransientDB."""

    def test_database_name_attribute(self):
        self.assertEqual(TransientDB.database_name, "transient")

    def test_databases_attribute(self):
        self.assertEqual(TransientDB.databases, {"transient": None})

    def test_class_attributes_shared(self):
        # database_name / databases are class attributes, not per-instance
        db = TransientDB()
        self.assertEqual(db.database_name, "transient")

    def test_unknown_method_is_noop(self):
        """Arbitrary method calls return None (silent no-op)."""
        db = TransientDB()
        self.assertIsNone(db.some_random_storage_method())
        self.assertIsNone(db.add(None, None))

    def test_unknown_method_callable(self):
        """Attribute access returns a callable."""
        db = TransientDB()
        self.assertTrue(callable(db.whatever))

    def test_private_name_raises_attribute_error(self):
        """Underscore-prefixed names raise AttributeError (not swallowed)."""
        db = TransientDB()
        with self.assertRaises(AttributeError):
            db._p_jar


class TestTransientJar(unittest.TestCase):
    """Tests for TransientJar."""

    def test_db_returns_transient_db(self):
        jar = TransientJar()
        db = jar.db()
        self.assertIsInstance(db, TransientDB)
        self.assertEqual(db.database_name, "transient")

    def test_jar_is_falsy(self):
        """A transient jar must be falsy (so persistence machinery treats
        the proxy as 'not connected to storage')."""
        self.assertFalse(bool(TransientJar()))

    def test_unknown_method_is_noop(self):
        jar = TransientJar()
        self.assertIsNone(jar.register(None))
        self.assertIsNone(jar.add(None))

    def test_unknown_method_callable(self):
        self.assertTrue(callable(TransientJar().whatever))

    def test_private_name_raises_attribute_error(self):
        jar = TransientJar()
        with self.assertRaises(AttributeError):
            jar._p_oid

    def test_db_chain_reaches_database_name(self):
        """The code path `connection.db().database_name` used by intid /
        serializer machinery must keep working."""
        self.assertEqual(TransientJar().db().database_name, "transient")


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
