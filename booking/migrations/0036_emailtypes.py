# Generated by Django 3.2.15 on 2022-12-30 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0035_booking_is_cancelled'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('body', models.TextField()),
                ('email_type', models.CharField(choices=[('Confirmation', 'Confirmation'), ('Cancelled', 'Cancelled'), ('Modified', 'Modified')], max_length=30)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]