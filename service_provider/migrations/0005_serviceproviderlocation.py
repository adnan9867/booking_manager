# Generated by Django 3.2.15 on 2022-12-18 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("service_provider", "0004_todonote"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceProviderLocation",
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
                ("latitude", models.CharField(max_length=255)),
                ("longitude", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "service_provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_in_location",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
