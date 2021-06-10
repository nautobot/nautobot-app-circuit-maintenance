"""Views for Circuit Maintenance."""
from nautobot.core.views import generic
from nautobot.circuits.models import Provider
from nautobot_circuit_maintenance import filters, forms, models, tables


class CircuitMaintenanceListView(generic.ObjectListView):
    """View for listing the config circuitmaintenance feature definition."""

    queryset = models.CircuitMaintenance.objects.all()
    table = tables.CircuitMaintenanceTable
    filterset = filters.CircuitMaintenanceFilterSet
    filterset_form = forms.CircuitMaintenanceFilterForm
    action_buttons = ("add",)


class CircuitMaintenanceView(generic.ObjectView):
    """Detail view for specific circuit maintenances."""

    queryset = models.CircuitMaintenance.objects.all()

    def get_extra_context(self, request, instance):
        """Extend content of detailed view for Circuit Maintenance."""
        maintenance_note = models.Note.objects.filter(maintenance=instance)
        circuits = models.CircuitImpact.objects.filter(maintenance=instance)
        parsednotification = models.ParsedNotification.objects.filter(maintenance=instance)

        return {
            "circuits": circuits,
            "maintenance_note": maintenance_note,
            "parsednotification": parsednotification,
        }


class CircuitMaintenanceEditView(generic.ObjectEditView):
    """View for editting circuit maintenances."""

    queryset = models.CircuitMaintenance.objects.all()
    model_form = forms.CircuitMaintenanceForm


class CircuitMaintenanceDeleteView(generic.ObjectDeleteView):
    """View for deleting circuit maintenances."""

    queryset = models.CircuitMaintenance.objects.all()


class CircuitMaintenanceBulkImportView(generic.BulkImportView):
    """View for bulk of circuit maintenances."""

    queryset = models.CircuitMaintenance.objects.all()
    model_form = forms.CircuitMaintenanceCSVForm
    table = tables.CircuitMaintenanceTable


class CircuitMaintenanceBulkEditView(generic.BulkEditView):
    """View for bulk editing circuitmaintenance features."""

    queryset = models.CircuitMaintenance.objects.all()
    table = tables.CircuitMaintenanceTable
    form = forms.CircuitMaintenanceBulkEditForm


class CircuitMaintenanceBulkDeleteView(generic.BulkDeleteView):
    """View for bulk deleting circuitmaintenance features."""

    queryset = models.CircuitMaintenance.objects.all()
    table = tables.CircuitMaintenanceTable


class CircuitImpactListView(generic.ObjectListView):
    """View for listing all circuit impact."""

    table = tables.CircuitImpactTable
    queryset = models.CircuitImpact.objects.all()
    action_buttons = ("add",)


class CircuitImpactView(generic.ObjectView):
    """Detail view for specific Circuit Impact windows."""

    queryset = models.CircuitImpact.objects.all()


class CircuitImpactEditView(generic.ObjectEditView):
    """View for editting Circuit Impact."""

    queryset = models.CircuitImpact.objects.all()
    model_form = forms.CircuitImpactForm


class CircuitImpactDeleteView(generic.ObjectDeleteView):
    """View for deleting Circuit Impact."""

    queryset = models.CircuitImpact.objects.all()


class CircuitImpactBulkImportView(generic.BulkImportView):
    """View for bulk of circuit Impact."""

    queryset = models.CircuitImpact.objects.all()
    model_form = forms.CircuitImpactCSVForm
    table = tables.CircuitImpactTable


class CircuitImpactBulkEditView(generic.BulkEditView):
    """View for bulk editing circuit impact features."""

    queryset = models.CircuitImpact.objects.all()
    table = tables.CircuitImpactTable
    form = forms.CircuitImpactBulkEditForm


class CircuitImpactBulkDeleteView(generic.BulkDeleteView):
    """View for bulk deleting circuit impact features."""

    queryset = models.CircuitImpact.objects.all()
    table = tables.CircuitImpactTable


class NoteListView(generic.ObjectListView):
    """View for listing all notes."""

    table = tables.NoteTable
    queryset = models.Note.objects.all()
    action_buttons = ("add",)


class NoteEditView(generic.ObjectEditView):
    """View for editing a maintenance note."""

    queryset = models.Note.objects.all()
    model_form = forms.NoteForm


class NoteView(generic.ObjectView):
    """View for maintenance note."""

    queryset = models.Note.objects.all()


class NoteDeleteView(generic.ObjectDeleteView):
    """View for deleting maintenance note."""

    queryset = models.Note.objects.all()


class NoteBulkImportView(generic.BulkImportView):
    """View for bulk of Notes."""

    queryset = models.Note.objects.all()
    model_form = forms.NoteCSVForm
    table = tables.NoteTable


class NoteBulkEditView(generic.BulkEditView):
    """View for bulk editing Notes."""

    queryset = models.Note.objects.all()
    table = tables.NoteTable
    form = forms.NoteBulkEditForm


class NoteBulkDeleteView(generic.BulkDeleteView):
    """View for bulk deleting Notea."""

    queryset = models.Note.objects.all()
    table = tables.NoteTable


class RawNotificationView(generic.ObjectView):
    """Detail view for raw notifications."""

    queryset = models.RawNotification.objects.all()

    def get_extra_context(self, request, instance):
        """Extend content of detailed view for RawNotification."""
        if instance.parsed:
            parsed_notification = models.ParsedNotification.objects.filter(raw_notification=instance).last()
        else:
            parsed_notification = None
        return {"parsed_notification": parsed_notification}


class RawNotificationListView(generic.ObjectListView):
    """View for listing all raw notifications."""

    table = tables.RawNotificationTable
    queryset = models.RawNotification.objects.all()
    filterset = filters.RawNotificationFilterSet
    filterset_form = forms.RawNotificationFilterSetForm
    action_buttons = ()


class RawNotificationBulkDeleteView(generic.BulkDeleteView):
    """View for bulk deleting Circuit Maintenance Notifications entries."""

    queryset = models.RawNotification.objects.all()
    table = tables.RawNotificationTable


class RawNotificationDeleteView(generic.ObjectDeleteView):
    """View for deleting Raw Notification."""

    model = models.RawNotification
    queryset = models.RawNotification.objects.all()


class ParsedNotificationView(generic.ObjectView):
    """Detail view for parsed notifications."""

    queryset = models.ParsedNotification.objects.all()


class NotificationSourceListView(generic.ObjectListView):
    """View for Notification Source."""

    table = tables.NotificationSourceTable
    queryset = models.NotificationSource.objects.all()
    filterset = filters.NotificationSourceFilterSet
    filterset_form = forms.NotificationSourceFilterSetForm
    action_buttons = ("edit",)


class NotificationSourceView(generic.ObjectView):
    """View for NotificationSource."""

    queryset = models.NotificationSource.objects.all()

    def get_extra_context(self, request, instance):  # pylint: disable=unused-argument
        """Extend content of detailed view for NotificationSource."""
        return {
            "providers": Provider.objects.filter(pk__in=[provider.pk for provider in instance.providers.all()]),
        }


class NotificationSourceEditView(generic.ObjectEditView):
    """View for editting NotificationSource."""

    model = models.NotificationSource
    queryset = models.NotificationSource.objects.all()
    model_form = forms.NotificationSourceForm


class NotificationSourceBulkEditView(generic.BulkEditView):
    """View for bulk editing NotificationSource."""

    queryset = models.NotificationSource.objects.all()
    table = tables.NotificationSourceTable
    form = forms.NotificationSourceBulkEditForm
