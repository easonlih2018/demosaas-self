# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime
import json

import requests
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.http import JsonResponse

from common.log import logger
from models import *
from esb_helper import *


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    return x + y

@periodic_task(run_every=crontab(minute='*', hour='*', day_of_week="*"))
def periodic_run_task():
    """
    执行定时任务
    """
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务开始执行，当前时间：{}".format(now))
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务执行结束，当前时间：{}".format(now))


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    # now = datetime.datetime.now()
    # logger.error(u"celery 定时任务执行中，当前时间：{}".format(now))
    # 调用定时任务
    # async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))

    hosts = Hosts.objects.all()
    script = """#!/bin/bash

    MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
    DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
    CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
    DATE=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "$DATE|$MEMORY|$DISK|$CPU"
    """
    for host in hosts:
        ip_list = [{"ip":host.bk_host_innerip, "bk_cloud_id": host.bk_cloud_id}]
        log_content = run_script_and_get_log_content(host.bk_biz_id, script, ip_list, host.created_by)
        host_perf = log_content.split("|")

        perform = {
            "mem_usage": host_perf[1].strip("%"),
            "disk_usage": host_perf[2].strip("%"),
            "cpu_usage": host_perf[3].strip("%"),
        }
        hostPerf = HostPerf()
        hostPerf.bk_host_id = host.bk_host_id
        hostPerf.avgload = 0
        host_perf.cpu_usage = perform["cpu_usage"]
        host_perf.mem_usage = perform["mem_usage"]
        host_perf.disk_usage = perform["disk_usage"]

        hostPerf.save()

                




