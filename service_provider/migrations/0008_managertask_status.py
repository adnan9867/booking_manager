# Generated by Django 3.2.15 on 2023-01-18 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_provider', '0007_managertask'),
    ]

    operations = [
        migrations.AddField(
            model_name='managertask',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]
