# Generated by Django 3.2.15 on 2023-02-12 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0045_alter_customersupportcollection_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtypes',
            name='email_type',
            field=models.CharField(choices=[('Confirmation', 'Confirmation'), ('Cancelled', 'Cancelled'), ('Modified', 'Modified'), ('Reminder', 'Reminder')], max_length=30),
        ),
    ]
