# Generated by Django 3.2.15 on 2022-11-23 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0012_auto_20221123_1923"),
    ]

    operations = [
        migrations.AddField(
            model_name="stripeid",
            name="email",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
