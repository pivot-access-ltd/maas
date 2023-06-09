# Generated by Django 3.2.12 on 2023-02-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maasserver", "0293_drop_verbose_regex_validator"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bootsource",
            name="keyring_data",
            field=models.BinaryField(
                blank=True,
                editable=True,
                help_text="The GPG keyring for this BootSource, as a binary blob.",
            ),
        ),
    ]
