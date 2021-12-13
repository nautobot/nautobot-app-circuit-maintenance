# Generated by Django 3.1.10 on 2021-05-07 08:37

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_cryptography.fields
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("circuits", "0002_initial_part_2"),
        ("extras", "0004_populate_default_status_records"),
    ]

    operations = [
        migrations.CreateModel(
            name="CircuitMaintenance",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(default="", max_length=100, unique=True)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("description", models.TextField(blank=True, null=True)),
                ("status", models.CharField(blank=True, default="TENTATIVE", max_length=50, null=True)),
                ("ack", models.BooleanField(blank=True, default=False, null=True)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["start_time"],
            },
        ),
        migrations.CreateModel(
            name="RawNotification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("raw", models.CharField(unique=True, max_length=512)),
                ("subject", models.CharField(max_length=200)),
                ("sender", models.CharField(max_length=200)),
                ("source", models.CharField(blank=True, default="unknown", max_length=50, null=True)),
                ("parsed", models.BooleanField(blank=True, default=False, null=True)),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "provider",
                    models.ForeignKey(
                        default=None, on_delete=django.db.models.deletion.CASCADE, to="circuits.provider"
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
            },
        ),
        migrations.CreateModel(
            name="ParsedNotification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("json", models.JSONField()),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "maintenance",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nautobot_circuit_maintenance.circuitmaintenance",
                    ),
                ),
                (
                    "raw_notification",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nautobot_circuit_maintenance.rawnotification",
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
            },
        ),
        migrations.CreateModel(
            name="NotificationSource",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("_password", django_cryptography.fields.encrypt(models.CharField(max_length=100))),
                ("source_id", models.EmailField(max_length=100, unique=True)),
                ("url", models.CharField(max_length=200)),
                ("source_type", models.CharField(blank=True, default="unknown", max_length=50, null=True)),
                ("providers", models.ManyToManyField(blank=True, to="circuits.Provider")),
            ],
            options={
                "ordering": ["source_id"],
            },
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("title", models.CharField(max_length=200)),
                ("level", models.CharField(blank=True, default="INFO", max_length=50, null=True)),
                ("comment", models.TextField()),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "maintenance",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nautobot_circuit_maintenance.circuitmaintenance",
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
                "unique_together": {("maintenance", "title")},
            },
        ),
        migrations.CreateModel(
            name="CircuitImpact",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("impact", models.CharField(blank=True, default="OUTAGE", max_length=50, null=True)),
                ("circuit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="circuits.circuit")),
                (
                    "maintenance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nautobot_circuit_maintenance.circuitmaintenance",
                    ),
                ),
            ],
            options={
                "ordering": ["maintenance", "impact"],
                "unique_together": {("maintenance", "circuit")},
            },
        ),
    ]
