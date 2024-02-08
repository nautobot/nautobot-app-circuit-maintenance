"""GraphQL tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from nautobot.circuits.models import Circuit
from nautobot.circuits.models import CircuitType
from nautobot.circuits.models import Provider
from nautobot.core.graphql import execute_query
from nautobot.core.testing.utils import create_test_user
from nautobot.extras.models import Status

from nautobot_circuit_maintenance.models import CircuitImpact
from nautobot_circuit_maintenance.models import CircuitMaintenance

# Use the proper swappable User model
User = get_user_model()


class GraphQLTestCase(TestCase):
    """GraphQL tests."""

    def setUp(self):
        """Prepare GraphQL test setup."""
        self.user = create_test_user("graphql_testuser")

        providers = Provider.objects.bulk_create(
            (
                Provider(name="Provider 3"),
                Provider(name="Provider 4"),
            )
        )

        circuit_types = CircuitType.objects.bulk_create(
            (
                CircuitType(name="Circuit Type 3"),
                CircuitType(name="Circuit Type 4"),
            )
        )

        status = Status.objects.get(name="Active")

        circuits = Circuit.objects.bulk_create(
            (
                Circuit(cid="Circuit 4", provider=providers[0], circuit_type=circuit_types[0], status=status),
                Circuit(cid="Circuit 5", provider=providers[1], circuit_type=circuit_types[1], status=status),
                Circuit(cid="Circuit 6", provider=providers[1], circuit_type=circuit_types[0], status=status),
                Circuit(cid="Circuit 7", provider=providers[1], circuit_type=circuit_types[0], status=status),
                Circuit(cid="Circuit 8", provider=providers[1], circuit_type=circuit_types[0], status=status),
            )
        )

        maintenances = CircuitMaintenance.objects.bulk_create(
            (
                CircuitMaintenance(
                    name="UT-TEST-3", start_time="2020-10-04 10:00:00Z", end_time="2020-10-04 12:00:00Z"
                ),
                CircuitMaintenance(
                    name="UT-TEST-4", start_time="2020-10-05 10:00:00Z", end_time="2020-10-05 12:00:00Z"
                ),
            )
        )

        CircuitImpact.objects.bulk_create(
            (
                CircuitImpact(maintenance=maintenances[0], circuit=circuits[0]),
                CircuitImpact(maintenance=maintenances[1], circuit=circuits[0], impact="NO-IMPACT"),
            )
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_execute_query_circuit_maintenance(self):
        "Test basic query for Circuit Maintenances."
        query = "{ query: circuit_maintenances {name} }"
        resp = execute_query(query, user=self.user).to_dict()
        self.assertFalse(resp["data"].get("errors"))
        self.assertEqual(len(resp["data"]["query"]), 2)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_execute_query_with_variable_circuit_maintenance(self):
        "Test filtered query for Circuit Maintenances."
        query = "query ($name: [String!]) { circuit_maintenances(name:$name) {name} }"
        resp = execute_query(query, user=self.user, variables={"name": "UT-TEST-3"}).to_dict()
        self.assertFalse(resp.get("errors"))
        self.assertEqual(len(resp["data"]["circuit_maintenances"]), 1)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_execute_query_circuit_impact(self):
        "Test basic query for Circuit Impacts."
        query = "{ query: circuit_impacts {impact} }"
        resp = execute_query(query, user=self.user).to_dict()
        self.assertFalse(resp["data"].get("errors"))
        self.assertEqual(len(resp["data"]["query"]), 2)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_execute_query_with_variable_circuit_impact(self):
        "Test filtered query for Circuit Impacts."
        query = "query ($impact: String) { circuit_impacts(impact:[$impact]) {impact} }"
        resp = execute_query(query, user=self.user, variables={"impact": "OUTAGE"}).to_dict()
        self.assertFalse(resp.get("errors"))
        self.assertEqual(len(resp["data"]["circuit_impacts"]), 1)
