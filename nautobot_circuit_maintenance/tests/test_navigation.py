"""Tests for the Circuit Maintenance navigation menu."""

from django.urls import reverse
from nautobot.apps.testing import TestCase
from nautobot.apps.ui import NavigationIconChoices, NavigationWeightChoices

from nautobot_circuit_maintenance.navigation import menu_items


class NavigationMenuTestCase(TestCase):
    """Test the Circuit Maintenance navigation menu structure."""

    @classmethod
    def setUpTestData(cls):
        """Resolve the Circuits tab and its Circuit Maintenance group once for all tests."""
        cls.tab = next(tab for tab in menu_items if tab.name == "Circuits")
        cls.group = next(group for group in cls.tab.groups if group.name == "Circuit Maintenances")

    def test_single_tab(self):
        """The app contributes exactly one navigation tab: 'Circuits'."""
        self.assertEqual(len(menu_items), 1)
        self.assertEqual(menu_items[0].name, "Circuits")

    def test_tab_attributes(self):
        """The Circuits tab uses the standard Circuits icon and weight."""
        self.assertEqual(self.tab.icon, NavigationIconChoices.CIRCUITS)
        self.assertEqual(self.tab.weight, NavigationWeightChoices.CIRCUITS)

    def test_menu_group_name(self):
        """The navigation menu group is named 'Circuit Maintenances', not 'Circuit Maintenance App'."""
        group_names = [group.name for group in self.tab.groups]
        self.assertIn("Circuit Maintenances", group_names)
        self.assertNotIn("Circuit Maintenance App", group_names)

    def test_group_attributes(self):
        """The Circuit Maintenances group has the expected weight."""
        self.assertEqual(self.group.weight, 250)

    def test_menu_items(self):
        """The group exposes the expected items, in order, with correct links, weights, and permissions."""
        expected_items = [
            {
                "link": "plugins:nautobot_circuit_maintenance:circuitmaintenance_overview",
                "name": "Dashboard",
                "weight": 100,
                "permissions": {"nautobot_circuit_maintenance.view_circuitmaintenance"},
            },
            {
                "link": "plugins:nautobot_circuit_maintenance:circuitmaintenance_list",
                "name": "Maintenances",
                "weight": 200,
                "permissions": {"nautobot_circuit_maintenance.view_circuitmaintenance"},
            },
            {
                "link": "plugins:nautobot_circuit_maintenance:rawnotification_list",
                "name": "Notifications",
                "weight": 300,
                "permissions": {"nautobot_circuit_maintenance.view_circuitmaintenance"},
            },
            {
                "link": "plugins:nautobot_circuit_maintenance:notificationsource_list",
                "name": "Notification Sources",
                "weight": 400,
                "permissions": {"nautobot_circuit_maintenance.view_notificationsource"},
            },
        ]

        self.assertEqual(len(self.group.items), len(expected_items))
        for item, expected in zip(self.group.items, expected_items):
            with self.subTest(item=expected["name"]):
                # Nautobot resolves NavMenuItem.link to a URL path at app-load time,
                # so compare against the reversed route rather than the raw route name.
                self.assertEqual(item.link, reverse(expected["link"]))
                self.assertEqual(item.name, expected["name"])
                self.assertEqual(item.weight, expected["weight"])
                self.assertEqual(item.permissions, expected["permissions"])

    def test_maintenances_item_renamed(self):
        """The circuit maintenance list item is named 'Maintenances', not 'Circuit Maintenances'."""
        item_names = [item.name for item in self.group.items]
        self.assertIn("Maintenances", item_names)
        self.assertNotIn("Circuit Maintenances", item_names)
