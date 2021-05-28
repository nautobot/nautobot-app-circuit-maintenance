"""Fields for Circuit Maintenance."""
from django.core import validators
from django.db import models
from django.forms.fields import URLField as FormURLField


class CustomURLFormField(FormURLField):
    """URL form field that accepts URLs that start with imap:// only until more support for more types are added."""

    default_validators = [validators.URLValidator(schemes=["imap"])]


class CustomURLField(models.URLField):
    """URL field that accepts URLs that start with imap:// only until more support for more types are added."""

    default_validators = [validators.URLValidator(schemes=["imap"])]

    def formfield(self, **kwargs):
        """Overwrite of the formfield validation."""
        return super().formfield(
            **{"form_class": CustomURLFormField, "error_messages": {"invalid": "Only IMAP scheme is supported."}}
        )
