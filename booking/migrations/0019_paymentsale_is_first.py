# Generated by Django 3.2.15 on 2022-12-01 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0018_paymentsale_is_captured"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentsale",
            name="is_first",
            field=models.BooleanField(default=False),
        ),
    ]