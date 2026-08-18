"""Unit tests for eea.virtualpages setup handlers.

These cover HiddenProfiles, the utility that hides the uninstall profile
from the Plone add-ons control panel. Pure logic, no Plone portal needed.
"""

import unittest

from eea.virtualpages.setuphandlers import HiddenProfiles


class TestHiddenProfiles(unittest.TestCase):
    """Test HiddenProfiles."""

    def setUp(self):
        self.hidden = HiddenProfiles()

    def test_uninstall_profile_is_hidden(self):
        """The uninstall profile must be hidden from the add-ons list."""
        profiles = self.hidden.getNonInstallableProfiles()
        self.assertIn("eea.virtualpages:uninstall", profiles)

    def test_default_profile_is_not_hidden(self):
        """The default profile must remain installable."""
        profiles = self.hidden.getNonInstallableProfiles()
        self.assertNotIn("eea.virtualpages:default", profiles)

    def test_profiles_are_strings(self):
        """Every hidden profile entry must be a string."""
        for profile in self.hidden.getNonInstallableProfiles():
            self.assertIsInstance(profile, str)

    def test_non_installable_profiles_returns_list(self):
        """getNonInstallableProfiles returns a list."""
        self.assertIsInstance(self.hidden.getNonInstallableProfiles(), list)

    def test_non_installable_products_returns_empty_list(self):
        """getNonInstallableProducts returns an empty list."""
        products = self.hidden.getNonInstallableProducts()
        self.assertIsInstance(products, list)
        self.assertEqual(products, [])


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
