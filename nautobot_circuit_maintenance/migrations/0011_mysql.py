# Generated by Django 3.1.14 on 2021-12-20 13:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_circuit_maintenance", "0010_rawnotification_stamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="title",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="rawnotification",
            name="raw",
            field=models.BinaryField(max_length=16384),
        ),
    ]
