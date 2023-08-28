# Generated by Django 3.2.20 on 2023-08-10 12:45

from django.db import migrations, models
import nautobot.core.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0096_remove_slugs"),
        ("nautobot_circuit_maintenance", "0011_mysql"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notificationsource",
            name="slug",
        ),
        migrations.AlterField(
            model_name="circuitimpact",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="circuitimpact",
            name="impact",
            field=models.CharField(default="OUTAGE", max_length=50),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="ack",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="status",
            field=models.CharField(default="TENTATIVE", max_length=50),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterField(
            model_name="note",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="note",
            name="level",
            field=models.CharField(default="INFO", max_length=50),
        ),
        migrations.AlterField(
            model_name="notificationsource",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="parsednotification",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="rawnotification",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="rawnotification",
            name="parsed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="rawnotification",
            name="sender",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
