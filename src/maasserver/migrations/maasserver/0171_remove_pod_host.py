# Generated by Django 1.11.11 on 2018-08-20 16:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("maasserver", "0170_add_subnet_allow_dns")]

    operations = [migrations.RemoveField(model_name="bmc", name="host")]
