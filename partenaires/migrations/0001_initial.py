# Generated by Django 5.2 on 2025-05-05 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Partenaire",
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
                ("nom", models.CharField(max_length=100)),
                (
                    "logo",
                    models.ImageField(
                        blank=True, null=True, upload_to="partenaires/logos/"
                    ),
                ),
                ("site_web", models.URLField(blank=True, null=True)),
            ],
        ),
    ]
