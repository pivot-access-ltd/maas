# Generated by Django 2.2.12 on 2021-02-09 15:41

from django.db import migrations, models
from django.db.models.expressions import RawSQL
from django.utils import timezone


def create_virtual_machines(apps, schema_editor):
    Node = apps.get_model("maasserver", "Node")
    VirtualMachine = apps.get_model("maasserver", "VirtualMachine")
    nodes_info = (
        Node.objects.filter(bmc__power_type="virsh")
        .annotate(
            identifier=RawSQL("instance_power_parameters->>'power_id'", ())
        )
        .values(
            "memory",
            "bmc_id",
            "identifier",
            machine_id=models.F("id"),
            unpinned_cores=models.F("cpu_count"),
        )
    )

    now = timezone.now()
    VirtualMachine.objects.bulk_create(
        VirtualMachine(**info, created=now, updated=now) for info in nodes_info
    )


class Migration(migrations.Migration):
    dependencies = [
        ("maasserver", "0222_replace_node_creation_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="virtualmachine",
            name="project",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(create_virtual_machines),
    ]
