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

    created_by = models.CharField(max_length=200)


