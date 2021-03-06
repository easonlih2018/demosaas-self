# -*- coding: utf-8 -*-
from django.db import models

class Hosts(models.Model):
    bk_host_id = models.IntegerField()
    bk_host_name = models.CharField(max_length=200)
    bk_host_innerip = models.CharField(max_length=200)
    bk_host_outerip = models.CharField(max_length=200)
    bk_cloud_id = models.IntegerField()
    bk_cloud_name = models.CharField(max_length=200)
    bk_os_name = models.CharField(max_length=200)
    bk_os_version = models.CharField(max_length=100)
    bk_os_bit = models.CharField(max_length=100)
    bk_cpu_mhz = models.CharField(max_length=50)
    bk_cpu_module = models.CharField(max_length=200)
    bk_mac = models.CharField(max_length=100)
    bk_cpu = models.CharField(max_length=20)
    bk_disk = models.CharField(max_length=20)
    bk_mem = models.CharField(max_length=20)
    bk_os_type = models.CharField(max_length=20)

    bk_biz_id = models.IntegerField(default=0)
    created_by = models.CharField(max_length=200)
    remark = models.CharField(max_length=500)


class HostPerf(models.Model):

    bk_host_id = models.IntegerField()
    when_created = models.DateTimeField(auto_now_add=True)
    avgload = models.FloatField()
    cpu_usage = models.FloatField()
    mem_usage = models.FloatField()
    disk_usage = models.FloatField()

class Script(models.Model):

    name = models.CharField(max_length=200)
    version = models.IntegerField()
    remark = models.CharField(max_length=500)
    resouce = models.IntegerField()
    category = models.IntegerField()
    content = models.CharField(max_length=1000)
    when_created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200)


class HostScriptResult(models.Model):

    host_id = models.IntegerField()
    script_id = models.IntegerField()
    execute_result = models.CharField(max_length=2000)
