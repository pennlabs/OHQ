# Generated by Django 3.1 on 2020-08-22 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ohq", "0002_auto_20200816_1727"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="status",
            field=models.CharField(
                choices=[
                    ("ASKED", "Asked"),
                    ("WITHDRAWN", "Withdrawn"),
                    ("ACTIVE", "Active"),
                    ("REJECTED", "Rejected"),
                    ("ANSWERED", "Answered"),
                ],
                default="ASKED",
                max_length=9,
            ),
        ),
    ]
