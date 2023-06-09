# Generated by Django 3.2.12 on 2023-01-18 16:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("metadataserver", "0033_remove_nodekey_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="script",
            name="packages",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="script",
            name="parameters",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="script",
            name="results",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="scriptresult",
            name="parameters",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
