"""Views for Circuit Maintenance."""

import datetime
import logging

import google_auth_oauthlib
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from nautobot.apps.views import (
    NautobotUIViewSet,
    ObjectBulkDestroyViewMixin,
    ObjectDestroyViewMixin,
    ObjectDetailViewMixin,
    ObjectListView,
    ObjectListViewMixin,
    ObjectView,
)
from nautobot.circuits.models import Circuit
from rest_framework.decorators import action
from rest_framework.response import Response

from nautobot_circuit_maintenance import filters, forms, models, tables
from nautobot_circuit_maintenance.api import serializers
from nautobot_circuit_maintenance.handle_notifications.sources import RedirectAuthorize, Source

logger = logging.getLogger(__name__)


class CircuitMaintenanceOverview(ObjectListView):  # pylint: disable=too-many-locals
    """View for an overview dashboard of summary view.

    This view provides a summary about the environment of circuit maintenances that have been recorded. Getting stats
    that provide a view into the upcoming maintenances and some metrics related to maintenances. This provides devices
    that are going to be impacted in the next n_days depending on configuration. This is based on circuit termination
    information.
    """

    action_buttons = ("export",)
    filterset = filters.CircuitMaintenanceFilterSet
    filterset_form = forms.CircuitMaintenanceFilterForm
    table = tables.CircuitMaintenanceTable
    template_name = "nautobot_circuit_maintenance/circuit_maintenance_overview.html"
    queryset = models.CircuitMaintenance.objects.all()  # Needs to remain all objects, otherwise other calcs will fail.
    today = datetime.date.today()
    extra_content = None

    def extra_context(self):
        """Extra content method on."""
        # add global aggregations to extra context.
        n_days = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {}).get("dashboard_n_days")
        maintenance_in_upcoming_days = self.get_maintenances_next_n_days(start_date=self.today, n_days=n_days)

        # Get historical matrix for number of maintenances, includes calculating the average number per month
        historical_matrix = self._get_historical_matrix(start_date=self.today)

        ###############################################################
        # Get Average duration for the maintenances
        ###############################################################
        total_duration_in_minutes = 0

        for ckt_maint in self.queryset.all():
            duration = ckt_maint.end_time - ckt_maint.start_time
            total_duration_in_minutes += round(duration.total_seconds() / 60.0, 0)

        circuit_maint_count = models.CircuitMaintenance.objects.count()

        # Check for a greater than 0 number of maintenance objects
        if circuit_maint_count > 0:
            average_maintenance_duration = str(round(total_duration_in_minutes / circuit_maint_count, 2)) + " minutes"
        else:
            average_maintenance_duration = "No maintenances found."

        # Get count of upcoming maintenances
        future_maintenance_count = self.calculate_future_maintenances(start_date=self.today)

        circuit_object_count = Circuit.objects.count()
        if circuit_object_count > 0:
            circuit_count_ratio = round(
                len(self.get_maintenances_next_n_days(start_date=self.today, n_days=n_days)) / circuit_object_count,
                2,
            )
        else:
            circuit_count_ratio = 0

        # Build up a dictionary of metrics to pass into the loop within the template
        metric_values = {
            "Upcoming Maintenances": len(maintenance_in_upcoming_days),
            "Historical - 7 Day": len(historical_matrix["past_7_days_maintenance"]),
            "Historical - 30 Days": len(historical_matrix["past_30_days_maintenance"]),
            "Historical - 365 Days": len(historical_matrix["past_365_days_maintenance"]),
            "Average Duration of Maintenances": average_maintenance_duration,
            "Future Maintenances": future_maintenance_count,
            "Average Number of Maintenances Per Month": round(self.get_maintenances_per_month(), 1),
            "Future Maintenance to Circuit Ratio": circuit_count_ratio,
        }

        # Build out the extra content, but this does require that there is a method of `extra_content` to be created.
        # If this method is not defined, and returning the extra_content value, then the data will not be passed to the
        # template.
        self.extra_content = {
            "upcoming_maintenances": maintenance_in_upcoming_days,
            "circuit_maint_metric_data": metric_values,
            "n_days": n_days,
        }

        return self.extra_content

    def get_maintenances_next_n_days(self, start_date: datetime.date, n_days: int):
        """Gets maintenances in the next n number of days.

        Args:
            start_date (datetime.date): Date to start the search.
            n_days (int): Number of days up coming

        Returns:
            List: List of maintenances that are up coming
        """
        start_date_midnight = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date_midnight = start_date_midnight + datetime.timedelta(days=n_days)
        maintenances = self.queryset.filter(start_time__gte=start_date_midnight, start_time__lte=end_date_midnight)

        return list(maintenances)

    def get_maintenance_past_n_days(self, start_date: datetime.date, n_days: int):
        """Gets maintenances in the past n number of days.

        Args:
            start_date (datetime.date): Date to start the search.
            n_days (int): Should be a negative number for the number of days.
        """
        start_date_midnight = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date_midnight = start_date_midnight + datetime.timedelta(days=n_days)
        maintenances = self.queryset.filter(start_time__gte=end_date_midnight, start_time__lte=start_date_midnight)

        return list(maintenances)

    def _get_historical_matrix(self, start_date: datetime.date):
        """Gets the historical matrix of the past maintenances.

        Args:
            start_date (datetime.date): Date to start the search.

        Returns:
            dict: A dictionary that represents the historical matrix maintenance record data.

            {
                "7 Days": count of past 7 days of maintenance,
                "30 Days": count of past 30 days of maintenance,
                "365 Days": count of past 30 days of maintenances
            }
        """
        # TODO: Move to a generic function set up, since this is something that should be exposed via the Capacity
        #       Metrics app when enabled.
        return_dict = {
            "past_7_days_maintenance": self.get_maintenance_past_n_days(start_date=start_date, n_days=-7),
            "past_30_days_maintenance": self.get_maintenance_past_n_days(start_date=start_date, n_days=-30),
            "past_365_days_maintenance": self.get_maintenance_past_n_days(start_date=start_date, n_days=-365),
        }
        return return_dict

    def calculate_future_maintenances(self, start_date: datetime.date):
        """Method to calculate future maintenances.

        Args:
            start_date (datetime.date): Date to start the search.

        Returns:
            int: Count of future maintenances
        """
        count = self.queryset.filter(
            start_time__gte=datetime.datetime.combine(start_date, datetime.datetime.min.time())
        ).count()

        return count

    @staticmethod
    def total_months(datetime_obj):
        """Method to return the total months."""
        return datetime_obj.month + 12 * datetime_obj.year

    def get_maintenances_per_month(self):
        """Calculates the number of circuit maintenances per month.

        Returns:
            float: Average maintenances per month
        """
        ordered_ckt_maintenance = models.CircuitMaintenance.objects.order_by("start_time")
        if ordered_ckt_maintenance.count() < 2:
            return 0

        end = ordered_ckt_maintenance.last().start_time
        start = ordered_ckt_maintenance.first().start_time
        # Get the number of years between the first and last date, multiply that by 12
        # Then get the differences in months. Then add 1 to account for the current month.
        delta_months = (end.year - start.year) * 12 + end.month - start.month + 1

        return self.queryset.count() / delta_months


class CircuitMaintenanceUIViewSet(NautobotUIViewSet):
    """UIViewSet for CircuitMaintenance."""

    bulk_update_form_class = forms.CircuitMaintenanceBulkEditForm
    filterset_class = filters.CircuitMaintenanceFilterSet
    filterset_form_class = forms.CircuitMaintenanceFilterForm
    form_class = forms.CircuitMaintenanceForm
    queryset = models.CircuitMaintenance.objects.order_by("-start_time")
    serializer_class = serializers.CircuitMaintenanceSerializer
    table_class = tables.CircuitMaintenanceTable
    action_buttons = ("add", "export")

    def get_extra_context(self, request, instance=None):
        """Extend content of detailed view for Circuit Maintenance."""
        if instance is None:
            return {}

        maintenance_note = models.Note.objects.filter(maintenance=instance)
        circuits = models.CircuitImpact.objects.filter(maintenance=instance)
        parsednotification = models.ParsedNotification.objects.filter(maintenance=instance).order_by(
            "-raw_notification__stamp"
        )

        return {
            "circuits": circuits,
            "maintenance_note": maintenance_note,
            "parsednotification": parsednotification,
        }

    @action(detail=False, methods=["get"], url_path="job", url_name="job")
    def run_job(self, request):
        """Trigger the Job to look for new Circuit Maintenances."""
        return redirect(
            reverse(
                "extras:job_run_by_class_path",
                kwargs={
                    "class_path": "nautobot_circuit_maintenance.handle_notifications.handler.HandleCircuitMaintenanceNotifications"
                },
            )
        )


class CircuitImpactUIViewSet(NautobotUIViewSet):
    """UIViewSet for CircuitImpact."""

    bulk_update_form_class = forms.CircuitImpactBulkEditForm
    filterset_class = filters.CircuitImpactFilterSet
    filterset_form_class = forms.CircuitImpactFilterForm
    form_class = forms.CircuitImpactForm
    queryset = models.CircuitImpact.objects.all()
    serializer_class = serializers.CircuitImpactSerializer
    table_class = tables.CircuitImpactTable
    action_buttons = ("add", "export")


class NoteUIViewSet(NautobotUIViewSet):
    """UIViewSet for Note."""

    bulk_update_form_class = forms.NoteBulkEditForm
    filterset_class = filters.NoteFilterSet
    filterset_form_class = forms.NoteFilterForm
    form_class = forms.NoteForm
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer
    table_class = tables.NoteTable
    action_buttons = ("add", "export")


class RawNotificationUIViewSet(
    ObjectDetailViewMixin,
    ObjectListViewMixin,
    ObjectDestroyViewMixin,
    ObjectBulkDestroyViewMixin,
):
    """UIViewSet for RawNotification."""

    # pylint: disable=abstract-method

    filterset_class = filters.RawNotificationFilterSet
    filterset_form_class = forms.RawNotificationFilterForm
    queryset = models.RawNotification.objects.all()
    serializer_class = serializers.RawNotificationSerializer
    table_class = tables.RawNotificationTable
    action_buttons = ("export",)

    def get_extra_context(self, request, instance=None):
        """Extend content of detailed view for RawNotification."""
        context = super().get_extra_context(request, instance)
        if self.action == "retrieve":
            if instance.parsed:
                parsed_notification = models.ParsedNotification.objects.filter(raw_notification=instance).last()
            else:
                parsed_notification = None
            try:
                if isinstance(instance.raw, bytes):
                    raw_repr = instance.raw.decode("utf-8", "strict")
                else:
                    raw_repr = instance.raw.tobytes().decode("utf-8", "strict")
            except UnicodeDecodeError as exc:
                raw_repr = "Raw content was not able to be decoded with utf-8"
                logger.warning("%s: %s", raw_repr, exc)

            context.update({"parsed_notification": parsed_notification, "raw_repr": raw_repr})

        return context


class ParsedNotificationView(ObjectView):
    """Detail view for parsed notifications."""

    queryset = models.ParsedNotification.objects.all()


class NotificationSourceUIViewSet(NautobotUIViewSet):
    """UIViewSet for NotificationSource."""

    bulk_update_form_class = forms.NotificationSourceBulkEditForm
    filterset_class = filters.NotificationSourceFilterSet
    filterset_form_class = forms.NotificationSourceFilterSetForm
    form_class = forms.NotificationSourceForm
    queryset = models.NotificationSource.objects.all()
    serializer_class = serializers.NotificationSourceSerializer
    table_class = tables.NotificationSourceTable
    action_buttons = ("edit", "export")

    def get_extra_context(self, request, instance=None):
        """Extend content of detailed view for NotificationSource."""
        context = super().get_extra_context(request, instance)

        if self.action == "retrieve":
            providers_qs = instance.providers.all()
            try:
                source = Source.init(name=instance.name)
                context.update(
                    {
                        "providers": providers_qs,
                        "account": source.get_account_id(),
                        "source_type": source.__class__.__name__,
                        "authentication_message": None,
                    }
                )

            except ValueError as exc:
                msg = f"Failed to initialize source: {exc}"
                logger.warning(msg, exc_info=True, extra={"object": instance})
                context.update(
                    {
                        "providers": providers_qs,
                        "account": None,
                        "source_type": None,
                        "authentication_message": msg,
                    }
                )
        return context

    @action(
        detail=True,
        methods=["get"],
        url_path="validate",
        url_name="validate",
        custom_view_base_action="view",
        custom_view_additional_permissions=["nautobot_circuit_maintenance.view_notificationsource"],
    )
    def validate_source(self, request, pk=None):  # pylint: disable=unused-argument
        """Validate NotificationSource authentication."""
        instance = self.get_object()
        context = super().get_extra_context(request, instance)
        return_url = request.GET.get("return_url")

        try:
            source = Source.init(name=instance.name)
        except ValueError as exc:
            message = f"FAILED: {exc}"
            if return_url:
                messages.error(request, message)
                return redirect(return_url)
            context["authentication_message"] = message
            return Response(context, status=200)

        try:
            is_authenticated, mess_auth = source.test_authentication()
            message = "SUCCESS" if is_authenticated else "FAILED"
            message += f": {mess_auth}"
        except ValueError as exc:
            message = f"FAILED: {exc}"
        except RedirectAuthorize as exc:
            try:
                return redirect(
                    reverse(
                        f"plugins:nautobot_circuit_maintenance:{str(exc.url_name)}",
                        kwargs={"name": exc.source_name},
                    )
                )
            except NoReverseMatch:
                message = "FAILED: Redirect required but target URL could not be resolved."

        if return_url:
            if message.startswith("SUCCESS"):
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect(return_url)

        context.update(
            {
                "authentication_message": message,
                "providers": instance.providers.all(),
                "account": source.get_account_id(),
                "source_type": source.__class__.__name__,
                "active_tab": "main",
            }
        )
        return Response(context, status=200)


def google_authorize(request, name):
    """View to start the Google OAuth authorization flow."""
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    notification_source = models.NotificationSource.objects.get(name=name)
    source = Source.init(name=notification_source.name)
    request.session["CLIENT_SECRETS_FILE"] = source.credentials_file
    request.session["SCOPES"] = source.SCOPES + source.extra_scopes
    request.session["SOURCE_NAME"] = name

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        request.session["CLIENT_SECRETS_FILE"], scopes=request.session["SCOPES"]
    )
    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the Google Cloud Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.

    flow.redirect_uri = (
        request.scheme
        + "://"
        + request.get_host()
        + reverse("plugins:nautobot_circuit_maintenance:google_oauth2callback")
    )
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
        # With "consent" as prompt option, we are going to ask for consent to authorize that the Application
        # that has been created in the API Console can read emails. The default option only asks about it one
        # time for different client usages, so if the Nautobot server was not the first one, it won't have the
        # necessary "refresh_token" in the response, that is used to automatically renew the token when expired,
        # without asking the user for login every time.
        prompt="consent",
    )
    # Store the state so the callback can verify the auth server response.
    request.session["state"] = state

    return redirect(authorization_url)


def google_oauth2callback(request):
    """View to receive the callback from Google OAuth authorization flow."""
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = request.session.get("state")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        request.session.get("CLIENT_SECRETS_FILE"), scopes=request.session.get("SCOPES"), state=state
    )

    flow.redirect_uri = (
        request.scheme
        + "://"
        + request.get_host()
        + reverse("plugins:nautobot_circuit_maintenance:google_oauth2callback")
    )
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    credentials = flow.credentials
    source_name = request.session.get("SOURCE_NAME")

    try:
        notification_source = models.NotificationSource.objects.get(name=source_name)
        notification_source.token = credentials
        notification_source.save()
    except models.NotificationSource.DoesNotExist:
        logger.warning("Google OAuth callback for %s is not matching any existing NotificationSource", source_name)

    return redirect(
        reverse(
            "plugins:nautobot_circuit_maintenance:notificationsource_validate",
            kwargs={"name": source_name},
        )
    )
