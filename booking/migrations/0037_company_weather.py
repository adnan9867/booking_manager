# Generated by Django 3.2.15 on 2022-12-30 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0036_emailtypes'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='weather',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
