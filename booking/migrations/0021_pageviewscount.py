# Generated by Django 3.2.15 on 2022-12-07 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "booking",
            "0020_alloweduser_chatroom_cleanybranches_messageinfo_spoperatinghour",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="PageViewsCount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]