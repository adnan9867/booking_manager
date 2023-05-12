# Generated by Django 3.2.15 on 2022-10-24 19:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("booking", "0003_extra"),
    ]

    operations = [
        migrations.CreateModel(
            name="BODContactInfo",
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
                ("first_name", models.CharField(max_length=48)),
                ("last_name", models.CharField(max_length=48)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=24)),
                (
                    "how_to_enter_on_premise",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="BODServiceLocation",
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
                ("street_address", models.CharField(max_length=128)),
                ("apt_suite", models.CharField(max_length=128)),
                ("city", models.CharField(max_length=48)),
                (
                    "state",
                    models.CharField(
                        choices=[("nyc", "NYC"), ("ca", "CA"), ("fl", "FL")],
                        max_length=48,
                    ),
                ),
                ("zip_code", models.IntegerField()),
                ("let_long", models.CharField(blank=True, max_length=56, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ServiceLocation",
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
                ("street_address", models.CharField(max_length=128)),
                ("apt_suite", models.CharField(max_length=128)),
                ("city", models.CharField(max_length=48)),
                (
                    "state",
                    models.CharField(
                        choices=[("nyc", "NYC"), ("ca", "CA"), ("fl", "FL")],
                        max_length=48,
                    ),
                ),
                ("zip_code", models.IntegerField()),
                ("let_long", models.CharField(blank=True, max_length=56, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Frequency",
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
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("once", "Once"),
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("biweekly", "Biweekly"),
                            ("monthly", "Monthly"),
                        ],
                        max_length=48,
                    ),
                ),
                ("title", models.CharField(max_length=256)),
                ("discount_percent", models.PositiveIntegerField(default=0)),
                ("discount_amount", models.PositiveIntegerField(default=0)),
                ("start_date", models.DateField()),
                ("recur_end_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.service",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookingOrderDetails",
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
                (
                    "type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Residential", "Residential"),
                            ("Commercial", "Commercial"),
                            ("Other", "Other"),
                        ],
                        max_length=24,
                        null=True,
                    ),
                ),
                ("start_time", models.CharField(max_length=24)),
                ("total_hours", models.FloatField(blank=True, null=True)),
                ("total_amount", models.FloatField(default=0.0)),
                (
                    "latest_reschedule",
                    models.IntegerField(
                        default=24, help_text="In hours. 0 means at any time."
                    ),
                ),
                (
                    "latest_cancel",
                    models.IntegerField(
                        default=24, help_text="In hours. 0 means at any time."
                    ),
                ),
                (
                    "additional_info",
                    models.TextField(
                        blank=True,
                        help_text="Any particular instructions. Or notes?",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("unscheduled", "Unscheduled"),
                            ("scheduled", "Scheduled"),
                            ("complete", "Complete"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="unscheduled",
                        max_length=48,
                    ),
                ),
                ("colour", models.CharField(default="#FFA500", max_length=124)),
                (
                    "bod_contact_info",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.bodcontactinfo",
                    ),
                ),
                (
                    "bod_service_location",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.bodservicelocation",
                    ),
                ),
                (
                    "frequency",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.frequency",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Booking",
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
                (
                    "type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Residential", "Residential"),
                            ("Commercial", "Commercial"),
                            ("Other", "Other"),
                        ],
                        max_length=24,
                        null=True,
                    ),
                ),
                ("start_time", models.CharField(max_length=24)),
                ("total_hours", models.FloatField(blank=True, null=True)),
                ("total_amount", models.FloatField(default=0.0)),
                (
                    "latest_reschedule",
                    models.IntegerField(
                        default=24, help_text="In hours. 0 means at any time."
                    ),
                ),
                (
                    "latest_cancel",
                    models.IntegerField(
                        default=24, help_text="In hours. 0 means at any time."
                    ),
                ),
                (
                    "additional_info",
                    models.TextField(
                        blank=True,
                        help_text="Any particular instructions. Or notes?",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("unscheduled", "Unscheduled"),
                            ("scheduled", "Scheduled"),
                            ("dispatched", "Dispatched"),
                            ("complete", "Complete"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=48,
                    ),
                ),
                ("notes", models.CharField(default="null", max_length=250)),
                ("notec", models.CharField(default="null", max_length=250)),
                ("appointment_date_time", models.DateTimeField()),
                (
                    "bod",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.bookingorderdetails",
                    ),
                ),
                (
                    "service_location",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.servicelocation",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]