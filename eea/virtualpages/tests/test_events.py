"""Unit tests for eea.virtualpages.events.

VirtualPageBuiltEvent.set_field must both set the attribute on the
proxy AND register the field name in `overrides` so the PATCH / @types
services strip it from incoming writes / schemas. Pure logic with a
dummy proxy object; no Plone portal needed.
"""

import types
import unittest

from eea.virtualpages.events import VirtualPageBuiltEvent


def _make_event(virtual=None, name="anything-here"):
    """Build an event with throwaway dummies for container / request."""
    if virtual is None:
        virtual = types.SimpleNamespace(title="Template")
    return VirtualPageBuiltEvent(
        container=types.SimpleNamespace(id="items"),
        virtual=virtual,
        name=name,
        request=object(),
    )


class TestVirtualPageBuiltEvent(unittest.TestCase):
    """Tests for VirtualPageBuiltEvent."""

    def test_attributes_assigned_in_init(self):
        virtual = types.SimpleNamespace(title="Template")
        event = _make_event(virtual=virtual, name="about")
        self.assertIs(event.virtual, virtual)
        self.assertEqual(event.name, "about")
        self.assertEqual(event.container.id, "items")
        self.assertIsNotNone(event.request)

    def test_overrides_starts_empty(self):
        event = _make_event()
        self.assertEqual(event.overrides, set())

    def test_set_field_sets_attribute_on_virtual(self):
        virtual = types.SimpleNamespace(title="Template")
        event = _make_event(virtual=virtual)
        event.set_field("title", "About")
        self.assertEqual(virtual.title, "About")

    def test_set_field_registers_override(self):
        event = _make_event()
        event.set_field("title", "About")
        self.assertIn("title", event.overrides)

    def test_set_field_accumulates_overrides(self):
        event = _make_event()
        event.set_field("title", "About")
        event.set_field("description", "Some description")
        event.set_field("blocks", {"a": 1})
        self.assertEqual(event.overrides, {"title", "description", "blocks"})

    def test_set_field_does_not_double_register(self):
        event = _make_event()
        event.set_field("title", "A")
        event.set_field("title", "B")
        self.assertEqual(event.overrides, {"title"})

    def test_set_field_value_overwritten_on_virtual(self):
        virtual = types.SimpleNamespace(title="Template")
        event = _make_event(virtual=virtual)
        event.set_field("title", "A")
        event.set_field("title", "B")
        self.assertEqual(virtual.title, "B")

    def test_set_field_creates_new_attribute(self):
        virtual = types.SimpleNamespace()
        event = _make_event(virtual=virtual)
        event.set_field("custom_attr", 42)
        self.assertEqual(virtual.custom_attr, 42)


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
