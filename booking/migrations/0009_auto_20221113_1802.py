# Generated by Django 3.2.15 on 2022-11-13 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0008_alter_stripeid_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("unscheduled", "Unscheduled"),
                    ("scheduled", "Scheduled"),
                    ("dispatched", "Dispatched"),
                    ("complete", "Complete"),
                    ("cancelled", "Cancelled"),
                ],
                default="unscheduled",
                max_length=48,
            ),
        ),
        migrations.AlterField(
            model_name="frequency",
            name="type",
            field=models.CharField(
                choices=[
                    ("once", "Once"),
                    ("weekly", "Weekly"),
                    ("biweekly", "Biweekly"),
                    ("monthly", "Monthly"),
                ],
                max_length=48,
            ),
        ),
    ]
