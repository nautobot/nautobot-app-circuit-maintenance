"""Admin management content for this plugin."""

from django.contrib import admin
from .models import NotificationSource


@admin.register(NotificationSource)
class NotificationSourceAdmin(admin.ModelAdmin):
    """Admin capabilities for viewing and deleting NotificationSource records."""

    def has_add_permission(self, request):
        """No option to add NotificationSources via the admin - use nautobot_config.py definitions instead."""
        return False

    def has_change_permission(self, request, obj=None):
        """No option to change NotificationSources via the admin - use nautobot_config.py definitions instead."""
        return False
