# Generated by Django 3.2.15 on 2022-11-23 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0011_bookingattachments_bookingproblem"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="notec",
            new_name="cleaner_notes",
        ),
        migrations.RenameField(
            model_name="booking",
            old_name="notes",
            new_name="customer_notes",
        ),
    ]
