# Generated by Django 3.2 on 2022-10-19 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Company",
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
                ("title", models.CharField(max_length=48)),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, upload_to="company_logo"),
                ),
                ("street_address", models.CharField(max_length=128)),
                ("city", models.CharField(max_length=48)),
                ("zip_code", models.IntegerField()),
                ("state", models.CharField(max_length=48)),
                ("phone", models.CharField(max_length=24)),
                ("email", models.EmailField(max_length=254)),
                (
                    "company_timezone",
                    models.CharField(blank=True, max_length=48, null=True),
                ),
                ("website", models.CharField(blank=True, max_length=48, null=True)),
                ("facebook", models.CharField(blank=True, max_length=128, null=True)),
                ("linkedin", models.CharField(blank=True, max_length=128, null=True)),
                ("twitter", models.CharField(blank=True, max_length=128, null=True)),
                ("instagram", models.CharField(blank=True, max_length=128, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tax",
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
                ("name", models.CharField(default="State Tax", max_length=64)),
                ("tax_code", models.CharField(max_length=64, unique=True)),
                ("tax_code_short", models.CharField(max_length=24)),
                (
                    "tax_code_number",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                ("tax_rate", models.PositiveIntegerField()),
                (
                    "additional_info",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.company",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Service",
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
                ("name", models.CharField(max_length=128)),
                (
                    "slug",
                    models.SlugField(
                        help_text="URI slug for this service page",
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("Draft", "Draft"), ("Published", "Published")],
                        default="Draft",
                        max_length=24,
                    ),
                ),
                (
                    "image_1",
                    models.ImageField(
                        blank=True, null=True, upload_to="service_image1"
                    ),
                ),
                (
                    "image_2",
                    models.ImageField(
                        blank=True, null=True, upload_to="service_image1"
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("Regular", "Regular"), ("Quote", "Quote")],
                        default="Regular",
                        max_length=24,
                    ),
                ),
                ("colour", models.CharField(default="#FFA500", max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking.company",
                    ),
                ),
                (
                    "tax",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="booking.tax",
                    ),
                ),
            ],
        ),
    ]