"""Unit tests for eea.virtualpages.traversal reserved-name logic.

``_is_reserved`` decides whether a URL segment must fall through to
standard Plone publication (REST verbs, management views, ``@``/``++``
markers) instead of being treated as a virtual id. Pure function, no
Plone portal needed.
"""

import unittest

from eea.virtualpages.traversal import (
    HTTP_METHOD_PREFIXES,
    RESERVED_NAMES,
    _is_reserved,
)


class TestIsReserved(unittest.TestCase):
    """Tests for _is_reserved."""

    # --- Reserved: management / Plone views ---
    def test_reserved_management_names(self):
        for name in RESERVED_NAMES:
            self.assertTrue(_is_reserved(name), f"{name!r} should be reserved")

    def test_edit_is_reserved(self):
        self.assertTrue(_is_reserved("edit"))

    def test_add_is_reserved(self):
        self.assertTrue(_is_reserved("add"))

    def test_view_is_reserved(self):
        self.assertTrue(_is_reserved("view"))

    # --- Reserved: REST API / plone.restapi markers ---
    def test_at_prefixed_is_reserved(self):
        for name in ("@types", "@workflow", "@navigation", "@search"):
            self.assertTrue(_is_reserved(name), f"{name!r} should be reserved")

    def test_double_plus_prefixed_is_reserved(self):
        for name in ("++api++", "++skin++", "++resource++foo"):
            self.assertTrue(_is_reserved(name), f"{name!r} should be reserved")

    # --- Reserved: HTTP method view prefixes (GET_application_json_*) ---
    def test_http_method_prefixes_are_reserved(self):
        for prefix in HTTP_METHOD_PREFIXES:
            self.assertTrue(
                _is_reserved(f"{prefix}application_json_search"),
                f"{prefix}* should be reserved",
            )

    def test_get_prefix_is_reserved(self):
        self.assertTrue(_is_reserved("GET_application_json_@search"))

    def test_patch_prefix_is_reserved(self):
        self.assertTrue(_is_reserved("PATCH_application_json_content"))

    # --- Not reserved: ordinary virtual ids ---
    def test_ordinary_name_is_not_reserved(self):
        self.assertFalse(_is_reserved("anything-here"))

    def test_plain_word_is_not_reserved(self):
        self.assertFalse(_is_reserved("products"))

    def test_numeric_id_is_not_reserved(self):
        self.assertFalse(_is_reserved("12345"))

    def test_sku_like_id_is_not_reserved(self):
        self.assertFalse(_is_reserved("SKU-001"))

    def test_uppercase_word_is_not_reserved(self):
        # "VIEW" is not in RESERVED_NAMES (matching is exact, not lowercased)
        self.assertFalse(_is_reserved("VIEW"))

    def test_name_starting_with_at_inside_is_reserved(self):
        # only a leading "@" triggers reservation
        self.assertTrue(_is_reserved("@"))
        self.assertFalse(_is_reserved("email@host"))


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
