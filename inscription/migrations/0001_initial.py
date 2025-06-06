# Generated by Django 5.0.14 on 2025-05-08 07:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0002_department_remove_userprofile_department_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Formation",
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
                ("titre", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("duree", models.CharField(max_length=50)),
                ("prerequis", models.TextField(blank=True)),
                ("objectifs", models.TextField()),
                ("date_session", models.DateField()),
                ("lieu", models.CharField(max_length=200)),
                ("capacite", models.PositiveIntegerField()),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("planifiee", "Planifiée"),
                            ("en_cours", "En cours"),
                            ("terminee", "Terminée"),
                            ("annulee", "Annulée"),
                        ],
                        default="planifiee",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="formations_creees",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="formations",
                        to="accounts.department",
                        verbose_name="Département",
                    ),
                ),
            ],
            options={
                "verbose_name": "Formation",
                "verbose_name_plural": "Formations",
                "ordering": ["-date_session"],
            },
        ),
        migrations.CreateModel(
            name="Inscription",
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
                ("prenom", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("telephone", models.CharField(max_length=20)),
                ("commentaire", models.TextField(blank=True)),
                (
                    "tracking_code",
                    models.CharField(editable=False, max_length=12, unique=True),
                ),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("en_attente", "En attente"),
                            ("validee", "Validée"),
                            ("refusee", "Refusée"),
                            ("annulee", "Annulée"),
                        ],
                        default="en_attente",
                        max_length=20,
                    ),
                ),
                ("date_inscription", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "formation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inscriptions",
                        to="inscription.formation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Inscription",
                "verbose_name_plural": "Inscriptions",
                "ordering": ["-date_inscription"],
            },
        ),
        migrations.CreateModel(
            name="Utilisateur",
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
                ("telephone", models.CharField(blank=True, max_length=15, null=True)),
                ("adresse", models.TextField(blank=True, null=True)),
                ("date_naissance", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RechercheFormation",
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
                ("terme_recherche", models.CharField(max_length=255)),
                ("date_recherche", models.DateTimeField(auto_now_add=True)),
                (
                    "utilisateur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inscription.utilisateur",
                    ),
                ),
            ],
        ),
    ]
