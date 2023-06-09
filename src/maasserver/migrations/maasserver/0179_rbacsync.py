# Generated by Django 1.11.11 on 2018-10-04 14:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("maasserver", "0178_break_apart_linked_bmcs")]

    operations = [
        migrations.CreateModel(
            name="RBACSync",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("full", "full"),
                            ("add", "add"),
                            ("update", "update"),
                            ("remove", "remove"),
                        ],
                        default="full",
                        editable=False,
                        help_text="Action that should occur on the RBAC service.",
                        max_length=6,
                    ),
                ),
                (
                    "resource_type",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Resource type that as been added/updated/removed.",
                        max_length=255,
                    ),
                ),
                (
                    "resource_id",
                    models.IntegerField(
                        blank=True,
                        editable=False,
                        help_text="Resource ID that has been added/updated/removed.",
                        null=True,
                    ),
                ),
                (
                    "resource_name",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Resource name that has been added/updated/removed.",
                        max_length=255,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="A brief explanation what changed.",
                        max_length=255,
                    ),
                ),
            ],
        )
    ]
