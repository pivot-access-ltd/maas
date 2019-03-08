# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-03-07 08:41
from __future__ import unicode_literals

from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    dependencies = [
        ('maasserver', '0184_add_ephemeral_deploy_setting_to_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='VMFS',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('maasserver.filesystemgroup',),
        ),
        migrations.AlterField(
            model_name='filesystem',
            name='fstype',
            field=models.CharField(choices=[('ext2', 'ext2'), ('ext4', 'ext4'), ('xfs', 'xfs'), ('fat32', 'fat32'), ('vfat', 'vfat'), ('lvm-pv', 'lvm'), ('raid', 'raid'), ('raid-spare', 'raid-spare'), ('bcache-cache', 'bcache-cache'), ('bcache-backing', 'bcache-backing'), ('swap', 'swap'), ('ramfs', 'ramfs'), ('tmpfs', 'tmpfs'), ('btrfs', 'btrfs'), ('zfsroot', 'zfsroot'), ('vmfs6', 'vmfs6')], default='ext4', max_length=20),
        ),
        migrations.AlterField(
            model_name='filesystemgroup',
            name='group_type',
            field=models.CharField(choices=[('raid-0', 'RAID 0'), ('raid-1', 'RAID 1'), ('raid-5', 'RAID 5'), ('raid-6', 'RAID 6'), ('raid-10', 'RAID 10'), ('lvm-vg', 'LVM VG'), ('bcache', 'Bcache'), ('vmfs6', 'VMFS6')], max_length=20),
        ),
    ]
