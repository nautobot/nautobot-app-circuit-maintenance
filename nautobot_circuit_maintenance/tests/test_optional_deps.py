"""Tests for optional dependencies."""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from nautobot_circuit_maintenance import views
from nautobot_circuit_maintenance.handle_notifications.sources import Source


class TestOptionalDependencies(TestCase):
    """Test behavior when optional dependencies are missing."""

    def test_gmail_source_init_missing_deps(self):
        """Test Source.init raises ValueError for Gmail source when deps are missing."""
        # Mock settings to include a Gmail source
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.settings") as mock_settings:
            mock_settings.PLUGINS_CONFIG = {
                "nautobot_circuit_maintenance": {
                    "notification_sources": [
                        {
                            "name": "gmail_source",
                            "url": "https://accounts.google.com/o/oauth2/auth",
                            "account": "test@example.com",
                            "credentials_file": "dummy.json",
                        }
                    ]
                }
            }

            # Patch GMAIL_CLIENT_PRESENT to False
            with patch("nautobot_circuit_maintenance.handle_notifications.sources.GMAIL_CLIENT_PRESENT", False):
                with self.assertRaisesMessage(ValueError, "You must install 'google-api-python-client'"):
                    Source.init("gmail_source")

    def test_views_google_auth_missing_deps(self):
        """Test google_authorize view redirects when deps are missing."""
        # Patch google_auth_oauthlib in views to None
        with patch("nautobot_circuit_maintenance.views.google_auth_oauthlib", None):
            request = MagicMock()
            request.user.is_authenticated = True

            # We need to mock reverse to avoid NoReverseMatch if URLconf isn't fully loaded or if we just want to check the redirect
            with patch("nautobot_circuit_maintenance.views.reverse") as mock_reverse:
                mock_reverse.return_value = "/mock/redirect"

                response = views.google_authorize(request, "some_source")

                # Verify it redirects
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/mock/redirect")

    def test_views_google_callback_missing_deps(self):
        """Test google_oauth2callback view redirects when deps are missing."""
        # Patch google_auth_oauthlib in views to None
        with patch("nautobot_circuit_maintenance.views.google_auth_oauthlib", None):
            request = MagicMock()
            request.user.is_authenticated = True

            with patch("nautobot_circuit_maintenance.views.reverse") as mock_reverse:
                mock_reverse.return_value = "/mock/redirect"

                response = views.google_oauth2callback(request)

                # Verify it redirects
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/mock/redirect")
