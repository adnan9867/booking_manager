# Generated by Django 3.2.15 on 2022-12-20 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0027_auto_20221220_1825"),
    ]

    operations = [
        migrations.AddField(
            model_name="dispatchedappointment",
            name="end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dispatchedappointment",
            name="start_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
