# Generated by Django 3.2.15 on 2023-02-01 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0043_auto_20230201_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingnotifications',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='booking.booking'),
        ),
    ]