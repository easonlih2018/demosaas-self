# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HostPerf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bk_host_id', models.IntegerField()),
                ('when_created', models.DateTimeField(auto_now_add=True)),
                ('avgload', models.FloatField()),
                ('cpu_usage', models.FloatField()),
                ('mem_usage', models.FloatField()),
                ('disk_usage', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Hosts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bk_host_id', models.IntegerField()),
                ('bk_host_name', models.CharField(max_length=200)),
                ('bk_host_innerip', models.CharField(max_length=200)),
                ('bk_host_outerip', models.CharField(max_length=200)),
                ('bk_cloud_id', models.IntegerField()),
                ('bk_cloud_name', models.CharField(max_length=200)),
                ('bk_os_name', models.CharField(max_length=200)),
                ('bk_os_version', models.CharField(max_length=100)),
                ('bk_os_bit', models.CharField(max_length=100)),
                ('bk_cpu_mhz', models.CharField(max_length=50)),
                ('bk_cpu_module', models.CharField(max_length=200)),
                ('bk_mac', models.CharField(max_length=100)),
                ('bk_cpu', models.CharField(max_length=20)),
                ('bk_disk', models.CharField(max_length=20)),
                ('bk_mem', models.CharField(max_length=20)),
                ('bk_os_type', models.CharField(max_length=20)),
                ('bk_biz_id', models.IntegerField(default=0)),
                ('created_by', models.CharField(max_length=200)),
                ('remark', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('version', models.IntegerField()),
                ('remark', models.CharField(max_length=500)),
                ('resouce', models.IntegerField()),
                ('category', models.IntegerField()),
                ('content', models.CharField(max_length=1000)),
                ('when_created', models.DateTimeField()),
                ('created_by', models.CharField(max_length=200)),
            ],
        ),
    ]
