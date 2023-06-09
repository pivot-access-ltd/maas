# Generated by Django 1.11.11 on 2019-08-08 08:19

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import migrations
from django.db.models.aggregates import Count


def remove_duplicate_physical_interfaces(apps, schema_editor):
    Interface = apps.get_model("maasserver", "Interface")

    # Find duplicated physical interfaces and remove them, keeping only the
    # interface that has IP addresses or the latest physical interface.
    qs = Interface.objects.values("type", "mac_address")
    qs = qs.filter(type="physical")
    qs = qs.order_by()  # clear default ordering
    qs = qs.annotate(ids=ArrayAgg("id")).annotate(count=Count("id"))
    qs = qs.filter(count__gt=1)
    for entry in qs:
        nic_ids = list(sorted(entry["ids"]))
        has_ips = list(
            sorted(
                nic.id
                for nic in Interface.objects.filter(id__in=nic_ids)
                if nic.ip_addresses.all()
            )
        )
        if len(has_ips) == 0:
            # None of the physical interfaces have an IP address, remove
            # the older interfaces.
            Interface.objects.filter(id__in=nic_ids[:-1]).delete()
        elif len(has_ips) == 1:
            # Keep only the physical interface that has IP addresses.
            nic_ids.remove(has_ips[0])
            Interface.objects.filter(id__in=nic_ids).delete()
        else:
            # Remove those that have no IPs.
            no_ips = set(nic_ids) - set(has_ips)
            if no_ips:
                Interface.objects.filter(id__in=no_ips).delete()
            # Multiple have IP addresses. Remove the IP addresses from the
            # others and only keep the latest with IP addresses.
            for nic in Interface.objects.filter(id__in=has_ips[:-1]):
                nic.ip_addresses.all().delete()
                nic.delete()


class Migration(migrations.Migration):
    dependencies = [("maasserver", "0196_numa_model")]

    operations = [migrations.RunPython(remove_duplicate_physical_interfaces)]
