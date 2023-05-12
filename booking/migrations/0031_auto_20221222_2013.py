# Generated by Django 3.2.15 on 2022-12-22 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0030_alter_stripeid_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserStripe",
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
                ("bod", models.CharField(default="0", max_length=148)),
                ("user", models.CharField(blank=True, max_length=250, null=True)),
                ("email", models.CharField(blank=True, max_length=250, null=True)),
                ("stripe_customer", models.CharField(max_length=148)),
            ],
        ),
        migrations.DeleteModel(
            name="StripeId",
        ),
    ]
