# Generated by Django 3.2.19 on 2023-08-08 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nautobot_circuit_maintenance", "0011_mysql"),
    ]

    operations = [
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
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="circuitmaintenance",
            name="status",
            field=models.CharField(default="TENTATIVE", max_length=50),
        ),
        migrations.AlterField(
            model_name="note",
            name="level",
            field=models.CharField(default="INFO", max_length=50),
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
