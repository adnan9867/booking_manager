# Generated by Django 3.2.15 on 2022-12-19 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0026_invoice_payroll"),
        ("service_provider", "0005_serviceproviderlocation"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceproviderlocation",
            name="booking",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="booking_in_location",
                to="booking.booking",
            ),
        ),
        migrations.AddField(
            model_name="serviceproviderlocation",
            name="check_in",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="serviceproviderlocation",
            name="check_out",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="serviceproviderlocation",
            name="total_hours",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
