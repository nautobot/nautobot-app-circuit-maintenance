"""Test for Circuit Maintenance Forms."""

from django.contrib.contenttypes.models import ContentType
from nautobot.apps.forms import DynamicModelMultipleChoiceField
from nautobot.apps.testing import FormTestCases
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField

from nautobot_circuit_maintenance.forms import NotificationSourceForm
from nautobot_circuit_maintenance.models import NotificationSource


class NotificationSourceFormTestCase(FormTestCases.BaseFormTestCase):
    """Tests for NotificationSourceForm."""

    form_class = NotificationSourceForm

    def test_providers_uses_api_backed_multi_select(self):
        """The providers field should be API-backed so the edit form stays usable with many Providers."""
        self.assertIsInstance(NotificationSourceForm().fields["providers"], DynamicModelMultipleChoiceField)

    def test_custom_fields_are_editable(self):
        """Custom fields defined on NotificationSource should be editable on the form."""
        custom_field = CustomField.objects.create(
            type=CustomFieldTypeChoices.TYPE_TEXT,
            key="notification_source_test_field",
            label="Notification Source Test Field",
        )
        custom_field.content_types.set([ContentType.objects.get_for_model(NotificationSource)])

        self.assertIn(custom_field.add_prefix_to_cf_key(), NotificationSourceForm().fields)
