# Generated by Django 3.1.10 on 2021-06-09 04:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_circuit_maintenance", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notificationsource",
            options={"ordering": ["name"]},
        ),
        migrations.RemoveField(
            model_name="notificationsource",
            name="_password",
        ),
        migrations.RemoveField(
            model_name="notificationsource",
            name="source_id",
        ),
        migrations.RemoveField(
            model_name="notificationsource",
            name="source_type",
        ),
        migrations.RemoveField(
            model_name="notificationsource",
            name="url",
        ),
        migrations.AddField(
            model_name="notificationsource",
            name="name",
            field=models.CharField(default=None, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notificationsource",
            name="slug",
            field=models.SlugField(default=None, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="rawnotification",
            name="source",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
