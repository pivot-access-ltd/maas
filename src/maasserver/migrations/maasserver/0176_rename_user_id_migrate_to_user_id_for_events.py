# Generated by Django 1.11.11 on 2018-09-20 10:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("maasserver", "0175_copy_user_id_and_node_system_id_for_events")
    ]

    operations = [
        migrations.RemoveField(model_name="event", name="user"),
        migrations.RenameField(
            model_name="event", old_name="user_id_migrate", new_name="user_id"
        ),
    ]
