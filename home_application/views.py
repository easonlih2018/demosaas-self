# -*- coding: utf-8 -*-
import json

import requests
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from account.decorators import login_exempt
from common.mymako import render_mako_context
from common.mymako import render_json
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
from home_application.esb_helper import *
from models import Hosts, HostPerf, Script, HostScriptResult
from django.db.models import Q
from celery_tasks import execute_task

#region 作业


def hostlist(request):
    """
    主机列表
    """
    return render_mako_context(request, '/home_application/host-list.html')


def scripts(request):
    """
    脚本列表
    """
    return render_mako_context(request, '/home_application/scripts.html')


def search_script(request):
    search_filter = json.loads(request.body)

    filter_objects = Script.objects.all()
    if "name" in search_filter and search_filter["name"] != "":
        filter_objects = filter_objects.filter(Q(name__icontains = search_filter["name"]))

    if "created_by" in search_filter and search_filter["created_by"] != "":
        filter_objects = filter_objects.filter(Q(created_by__icontains = search_filter["created_by"]))

    if "category" in search_filter and search_filter["category"] != "0":
        filter_objects = filter_objects.filter(category = search_filter["category"])

    if "source" in search_filter and search_filter["source"] != "0":
        filter_objects = filter_objects.filter(resouce = search_filter["source"])

    if "start_time" in search_filter and search_filter["start_time"] != "":
        d_start_time = datetime.fromtimestamp(float(search_filter["start_time"]) / 1000)
        filter_objects = filter_objects.filter(when_created__gt = d_start_time)

    if "end_time" in search_filter and search_filter["end_time"] != "":
        d_end_time = datetime.fromtimestamp(float(search_filter["end_time"]) / 1000)
        filter_objects = filter_objects.filter(when_created__lt = d_end_time)

    dbresults = list(filter_objects.values())
    result = []
    for dbresult in dbresults:
        script = {
            "id" : dbresult["id"],
            "name" : dbresult["name"],
            "source" : dbresult["resouce"],
            "source_name" : get_source_name(dbresult["resouce"]),
            "category" : dbresult["category"],
            "category_name" : get_category_name(dbresult["category"]),
            "content" : dbresult["content"],
            "when_created" : dbresult["when_created"].strftime("%Y-%m-%d %H:%M:%S"),
            "created_by" : dbresult["created_by"]
        }
        result.append(script)
    return render_json({"result":True, "data" : result})

def execute_script(request):
    content = json.loads(request.body)
    biz_id = content["biz_id"]
    ip_list = [
        {"ip": content["host"]["bk_host_innerip"], "bk_cloud_id": content["host"]["bk_cloud_id"]}
    ]
    script = content["script"]["content"]

    result = run_script_and_get_log_content(biz_id, script, ip_list, request.user.username)

    script_id = content["script"]["id"]
    host_id = content["host"]["bk_host_id"]

    script_result = HostScriptResult()

    script_result.script_id = script_id
    script_result.host_id = host_id
    script_result.execute_result = result

    script_result.save()

    return render_json({"result": True, "message": "ok"})

def search_host_execute_result(request):
    content = json.loads(request.body)
    host_id = content["host_id"]
    host_execute_result = ""
    result = HostScriptResult.objects.filter(host_id=host_id).order_by("id").reverse()
    if result.count() > 0:
        host_execute_result= result[0].execute_result
    else:
        host_execute_result= "无执行历史"

    return  render_json({"result": True, "data": host_execute_result})

def create_script(request):

    request_content = json.loads(request.body)
    script = Script()
    script.name = request_content["name"]
    script.resouce = request_content["source"]
    script.category = request_content["category"]
    script.content = request_content["content"]
    script.remark = request_content["remark"]
    script.version = 1
    script.created_by = request.user.username

    script.save()
    return render_json({"result" : True, "message" : "ok"})

def delete_script(request):

    content = json.loads(request.body)
    id = content["id"]

    Script.objects.filter(id = id).delete()

    return render_json({"result" : True, "message" : "ok"})

def update_script(request):

    content = json.loads(request.body)
    id = content["id"]
    name = content["name"]
    category = content["category"]
    source = content["source"]
    script_content = content["content"]
    remark = content["remark"]

    script = Script.objects.get(id = id)

    script.name = name
    script.category = category
    script.resouce = source
    script.content = script_content
    script.remark = remark
    script.version = script.version + 1
    script.save()

    return render_json({"result" : True, "message" : "ok"})

def get_script_by_id(request):

    content = json.loads(request.body)
    id = content["id"]
    script = Script.objects.filter(id = id).values()
    if len(script) > 0:
        result = {
            "id" : script[0]["id"],
            "name" : script[0]["name"],
            "source" : script[0]["resouce"],
            "category" : script[0]["category"],
            "content" : script[0]["content"],
            "remark" : script[0]["remark"]
        }
        return render_json({"result":True, "data":result})

    return render_json({"result" : True, "message" : "failed"})

def get_category_name(category_id):

    categorys = {
        1: "shell",
        2: "bat",
        3: "perl",
        4: "python",
        5: "powershell"
    }

    return categorys[category_id]


def get_source_name(source_id):
    sources = {
        1: "手工录入",
        2: "脚本克隆",
        3: "本地脚本"
    }
    return sources[source_id]



# endregion


def home(request):
    """
    首页
    """
    id = request.GET.get('id')
    return render_mako_context(request, '/home_application/home.html',{ "id":id})


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def test(request):
    """
    测试
    """
    return render_mako_context(request, '/home_application/test.html')

def modal(request):
    """
    测试
    """
    return render_mako_context(request, '/home_application/modal.html')

def host1(request):
    """
    host1
    """
    return render_mako_context(request, '/home_application/demo/host1.html')

def host2(request):
    """
    host2
    """
    return render_mako_context(request, '/home_application/demo/host2.html')

def chart(request):
    """
    chart
    """
    return render_mako_context(request, '/home_application/demo/chart.html')

def hosts(request):

    return render_mako_context(request, '/home_application/hosts.html')

def hosts1(request):

    return render_mako_context(request, '/home_application/hosts1.html')

#region API

def testapi(request):
    return render_json({"username":"admin","result":"ok"})

def search_biz_from_cmdb(request):
    
    result = cc_search_biz(request.user.username)

    bizs = []
    if result["result"]:
        for r_biz in result["data"]["info"]:
            biz = {
                "bk_biz_id" : r_biz["bk_biz_id"],
                "bk_biz_name" : r_biz["bk_biz_name"]
            }

            bizs.append(biz)

    return render_json({"result" : True, "data" : bizs})

def search_set_from_cmdb(request):
    content = json.loads(request.body)
    set_id = content["biz_id"]
    result = cc_search_set(set_id, request.user.username)
    sets = []
    if result["result"]:
        for r_set in result["data"]["info"]:
            set = {
                "bk_set_id" : r_set["bk_set_id"],
                "bk_set_name" : r_set["bk_set_name"]
            }

            sets.append(set)
    return render_json({"result" : True, "data" : sets})

def search_host_from_cmdb(request):
    
    content = json.loads(request.body)
    bk_biz_id = ""
    ip_list = []
    bk_set_id = ""
    if "bk_biz_id" not in content:
        return render_json({"result" : False, "message" : "bk_biz_id not exists"})
    bk_biz_id = content["bk_biz_id"]
    if "bk_set_id" in content:
         bk_set_id = content["bk_set_id"]
    if "ip_list" in content:
        ip_list = content["ip_list"].split()
    result = []
    if bk_set_id == "":
        result = cc_search_host_with_biz(bk_biz_id, ip_list,request.user.username)
    else:
        result = cc_search_host(bk_biz_id, bk_set_id, ip_list,request.user.username)
    monitorHosts = Hosts.objects.filter(bk_biz_id = bk_biz_id)

    hosts = []
    if result["result"]:
        for r_host in result["data"]["info"]:
            host = {
                "bk_host_id": r_host["host"]["bk_host_id"],
                "bk_host_name": r_host["host"]["bk_host_name"],
                "bk_host_innerip": r_host["host"]["bk_host_innerip"],              
                "bk_host_outerip": r_host["host"]["bk_host_outerip"],
                "bk_cloud_id": r_host["host"]["bk_cloud_id"][0]["bk_inst_id"],
                "bk_cloud_name": r_host["host"]["bk_cloud_id"][0]["bk_inst_name"],
                "bk_os_name": r_host["host"]["bk_os_name"],
                "bk_os_version": r_host["host"]["bk_os_version"],
                "bk_os_bit": r_host["host"]["bk_os_bit"],
                "bk_cpu_mhz": r_host["host"]["bk_cpu_mhz"],
                "bk_cpu_module": r_host["host"]["bk_cpu_module"],
                "bk_cpu": r_host["host"]["bk_cpu"],
                "bk_mac": r_host["host"]["bk_mac"],
                "bk_disk": r_host["host"]["bk_disk"],
                "bk_mem": r_host["host"]["bk_mem"],
                "bk_os_type": r_host["host"]["bk_os_type"],

                "mem_usage" : "-",
                "disk_usage" : "-",
                "cpu_usage" : "-",

                "is_monitored" : False
            }
            for monitorHost in monitorHosts:
                if monitorHost.bk_host_id == host["bk_host_id"]:
                    host["is_monitored"] = True
            hosts.append(host)
    return render_json({"result" : True, "data": hosts})

#region 操作数据库
def search_host_from_db(request):
    '''
    根据IP查询db中的主机
    '''
    content = json.loads(request.body)
    filter_hosts = []
    if "ip_filter" in content:
        ip_filter = content["ip_filter"]
        if ip_filter != "":
            filter_hosts = Hosts.objects.filter( Q(bk_host_innerip__icontains = ip_filter) | Q(bk_host_outerip__icontains = ip_filter))
        else:
            filter_hosts = Hosts.objects.all()
    else:
        filter_hosts = Hosts.objects.all()

    result = list(filter_hosts.values())
    return render_json({"result":True, "data": result})

def create_host_to_db(request):
    
    content = json.loads(request.body)["host"]
    host = Hosts()
    host.bk_host_id = content.get("bk_host_id", 0)
    host.bk_host_name = content.get("bk_host_name", "")
    host.bk_host_innerip = content.get("bk_host_innerip", "")
    host.bk_host_outerip = content.get("bk_host_outerip", "")
    host.bk_cloud_id = content.get("bk_cloud_id", 0)
    host.bk_cloud_name = content.get("bk_cloud_name", "")
    host.bk_os_name = content.get("bk_os_name", "")
    host.bk_os_version = content.get("bk_os_version", "")
    host.bk_os_bit = content.get("bk_os_bit", "")
    host.bk_cpu_mhz = content.get("bk_cpu_mhz", "")
    host.bk_cpu_module = content.get("bk_cpu_module", "")
    host.bk_cpu = content.get("bk_cpu", "")
    host.bk_mac = content.get("bk_mac", "")
    host.bk_disk = content.get("bk_disk", "")
    host.bk_mem = content.get("bk_mem", "")
    host.bk_os_type = content.get("bk_os_type", "")

    host.bk_biz_id = content.get("bk_biz_id", "")
    host.created_by = request.user.username

    if Hosts.objects.filter(bk_host_id = host.bk_host_id).count() == 0:
         host.save()
   

    return render_json({"result" : True, "message" : "ok"})

def delete_host_from_db(request):

    content = json.loads(request.body)
    bk_host_id = ""
    if "bk_host_id" in content:
        bk_host_id = content["bk_host_id"]
    
    if bk_host_id != "":
        Hosts.objects.filter(bk_host_id = bk_host_id).delete()
        return render_json({"result" : True, "message":"ok"})
    
    return render_json({"result" : False, "message":"bk_host_id 没有值"})

def show_performance(request):

    content = request.body
    content = json.loads(content)
    ip_list = content["ip_list"]
    bk_biz_id = content["bk_biz_id"]
    script_content = """#!/bin/bash

    MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
    DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
    CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
    DATE=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "$DATE|$MEMORY|$DISK|$CPU"
    """

    result = run_fast_execute_script(bk_biz_id, script_content, ip_list, request.user.username)

    if result["result"]:
        result = get_job_instance_log(bk_biz_id, result["data"])
        log_result = result[0]["log_content"].strip().split("|")
        perform = {
            "mem_usage": log_result[1].strip("%"),
            "disk_usage": log_result[2].strip("%"),
            "cpu_usage": log_result[3].strip("%"),
        }
    else:
        perform = {"error": result["data"]}
    return JsonResponse(perform)

def show_monitor(request):

    
    content = json.loads(request.body)
    bk_host_id = content["bk_host_id"]
    date_filter = datetime.now() - timedelta(hours=1)
    host_perfs = HostPerf.objects.filter(bk_host_id = bk_host_id, when_created__gt = date_filter)
    rows = []
    for host_perf in host_perfs:
        row = {
            "time" : host_perf.when_created.strftime("%Y-%m-%d %H:%M:%S"),
            "mem_usage" : host_perf.mem_usage,
            "disk_usage" : host_perf.disk_usage,
            "cpu_usage" : host_perf.cpu_usage
        }
        rows.append(row)

    columns = ['time', 'mem_usage', 'disk_usage', 'cpu_usage']
    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})


def update_host_remark(request):
    content = json.loads(request.body)
    bk_host_id = content["bk_host_id"]
    remark = content["remark"]

    hosts = Hosts.objects.filter(bk_host_id = bk_host_id).update(remark = remark)

    return render_json({"result" : True})
    
def get_disk_perf(request):

    content = json.loads(request.body)
    biz_id = content["biz_id"]
    ip_list = content["ip_list"]
    script_content = '''#!/bin/bash
    df -h
    '''

    log_result = run_script_and_get_log_content(biz_id, script_content, ip_list, request.user.username)
    log_contents = log_result.split('\n')
    del log_contents[0]
    perfs = []
    for log_content in log_contents:
        logs = log_content.split()
        if len(logs) > 5:
            perf = {
                        "Filesystem" : logs[0],
                        "Size" : logs[1],
                        "Used" : logs[2],
                        "Avail" : logs[3],
                        "UsePecent" : logs[4],
                        "MountedOn" : logs[5]
                    }
            perfs.append(perf)
    return render_json(perfs)

def get_mem_perf(request):
    content = json.loads(request.body)
    biz_id = content["biz_id"]
    ip_list = content["ip_list"]
    script_content = '''#!/bin/bash
    free -m
    '''

    log_result = run_script_and_get_log_content(biz_id, script_content, ip_list, request.user.username)

    log_contents = log_result.split('\n')
    
    perfs = []
    logs = log_contents[1].split()
    if len(logs) > 6:
        perfs = {
                    "columns" : ["name","value"],
                    "rows" :  [
                        { "name": "used" ,"value": logs[2]},
                        { "name": "free" ,"value": logs[3]},
                        { "name": "shared" ,"value": logs[4]},
                        { "name": "buff/cache" ,"value": logs[5]},
                        { "name": "available","value": logs[6]}
                    ]
                }
                
    return render_json(perfs)


def get_avgload(request):

    content = json.loads(request.body)
    bk_host_id = content["bk_host_id"]
    date_filter = datetime.now()-timedelta(hours=1)
    host_avgloads = HostPerf.objects.filter(bk_host_id = bk_host_id, when_created__gt = date_filter)
    rows = []
    for host_avgload in host_avgloads:
        row = {
            "time" : host_avgload.when_created.strftime("%Y-%m-%d %H:%M:%S"),
            "avgload" : host_avgload.avgload
        }
        rows.append(row)

    columns = ['time', 'avgload']
    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})

def search_host_avgLoad(request):

    content = json.loads(request.body)
    bk_host_id = content["bk_host_id"]
    start_time = content["start_time"]
    end_time = content["end_time"]

    d_start_time = datetime.fromtimestamp(float(start_time) / 1000)
    d_end_time = datetime.fromtimestamp(float(end_time) / 1000)

    host_avgloads = HostPerf.objects.filter(bk_host_id = bk_host_id, when_created__gt = d_start_time, when_created__lt = d_end_time)
    rows = []
    for host_avgload in host_avgloads:
        row = {
            "time" : host_avgload.when_created.strftime("%Y-%m-%d %H:%M:%S"),
            "avgload" : host_avgload.avgload
        }
        rows.append(row)

    columns = ['time', 'avgload']
    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})


#endregion

#region chart data

def get_line_data(request):

    columns = ['time', 'cpu', 'men', 'disk']
    rows = [
        {'time': '1月1日',  'cpu': 89.3, 'men': 96.4, 'disk':88},
        {'time': '1月2日',  'cpu': 79.3, 'men': 88.4, 'disk': 78},
        {'time': '1月3日',  'cpu': 88.3, 'men': 78.4, 'disk': 84},
        {'time': '1月4日', 'cpu': 78.3, 'men': 63.4, 'disk': 76},
        {'time': '1月5日',  'cpu': 74.3, 'men': 94.4, 'disk': 79},
        {'time': '1月6日',  'cpu': 85.3, 'men': 87.4, 'disk': 98}
    ]

    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})

def get_histogram_data(request):

    columns = ['time', 'cpu', 'men', 'disk']
    rows = [
        {'time': '1月1日',  'cpu': 89.3, 'men': 96.4, 'disk':88},
        {'time': '1月2日',  'cpu': 79.3, 'men': 88.4, 'disk': 78},
        {'time': '1月3日',  'cpu': 88.3, 'men': 78.4, 'disk': 84},
        {'time': '1月4日', 'cpu': 78.3, 'men': 63.4, 'disk': 76},
        {'time': '1月5日',  'cpu': 74.3, 'men': 94.4, 'disk': 79},
        {'time': '1月6日',  'cpu': 85.3, 'men': 87.4, 'disk': 98}
    ]

    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})

def get_pie_data(request):

    columns = ["name" , "value"]
    rows = [
        {'name': 'name1',  'value': 5},
        {'name': 'name2',  'value': 20},
        {'name': 'name3',  'value': 20},
        {'name': 'name4',  'value': 25},
        {'name': 'name5',  'value': 15},
        {'name': 'name6',  'value': 15}
    ]

    return render_json({"result" : True, "data" : {"columns": columns, "rows": rows}})

#endregion 

def test_celery(request):

    execute_task()

    return render_json({"result" : True})

#endregion


#region 示例方法
def getJson(request):
    data = [
        {'time': '1月1日',  'cpu': 89.3, 'men': 96.4, 'disk':88},
        {'time': '1月2日',  'cpu': 79.3, 'men': 88.4, 'disk': 78},
        {'time': '1月3日',  'cpu': 88.3, 'men': 78.4, 'disk': 84},
        {'time': '1月4日', 'cpu': 78.3, 'men': 63.4, 'disk': 76},
        {'time': '1月5日',  'cpu': 74.3, 'men': 94.4, 'disk': 79},
        {'time': '1月6日',  'cpu': 85.3, 'men': 87.4, 'disk': 98}
    ]
    return render_json({"result": True,"data": data})
# 返回echarts 图标拼接格式数据
# series 下面的type 表示需要渲染哪种图表类型
# line:折线图   bar:柱状图
def getEchartsJson(request):
    data ={
        "xAxis": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "series": [
            {
                "name": "cpu",
                "type": "line",
                "data": [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
            },
            {
                "name": "men",
                "type": "line",
                "data": [3.6, 6.9, 8.0, 21.4, 23.7, 78.7, 165.6, 152.2, 68.7, 28.8, 7.0, 8.3]
            },
            {
                "name": "disk",
                "type": "bar",
                "data": [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
            }
        ]
    }
    return render_json({"result": True,"data": data})
# 该方法一般不作修改
def search_biz(request):
    data = cc_search_biz(request.user.username)
    return JsonResponse(data)


def search_set(request):
    """
    传递参数
    :param 业务id   biz_id
    :param request:
    :return:
    """
    biz_id = request.GET.get('biz_id')
    data = cc_search_set(biz_id)
    return JsonResponse(data)


def search_host(request):
    """
    :param request:
    传递参数
    :param 业务id   biz_id,
    biz_id,ip_list = ['10.92.190.214','10.92.190.215']
    get请求获取的ip_list，转换成列表，请调用get_host_ip_list
    :return:
    """
    biz_id = request.GET.get('biz_id')
    ip_list = []
    if 'ip' in request.GET:
        ip = request.GET.get('ip')
        ip_list = get_host_ip_list(ip)
    data = cc_search_host(biz_id,ip_list)
    return JsonResponse(data)


def fast_execute_script(request):
    """
    :param request:
    传递参数
    :param 业务id   biz_id,
         ip_list = [
            {
                "bk_cloud_id": 0,
                "ip": "10.92.190.214"
            }
            {
                "bk_cloud_id": 0,
                "ip": "10.92.190.215"
            }
        ]
    :return:
    """
    biz_id = request.GET.get('biz_id')
    script_content = """
         df -h
    """
    ip_list = [
        {
            "bk_cloud_id": 0,
            "ip": "192.168.240.43"
        }
    ]
    data = run_fast_execute_script(biz_id,script_content,ip_list,request.user.username)
    return JsonResponse(data)


def execute_job(request):
    """
    :param request:
    传递参数
    :param 业务id       biz_id,
    :param 作业模板id    job_id,
    :param ip列表     ip_list = [
            {
                "bk_cloud_id": 0,
                "ip": "10.92.190.214"
            }
            {
                "bk_cloud_id": 0,
                "ip": "10.92.190.215"
            }
        ]
    :return:
    """
    biz_id = request.GET.get('biz_id')
    job_id = request.GET.get('job_id')
    ip_list = [
        {
            "bk_cloud_id": 0,
            "ip": "192.168.240.43"
        }
    ]
    data = run_execute_job(biz_id, job_id, ip_list,request.user.username)
    return JsonResponse(data)


def get_log_content(request):
    """
        :param request:
        传递参数
        :param 业务id       biz_id,
        :param 作业实例id    instance_id,
        :return:
        """
    biz_id = request.GET.get('biz_id')
    job_instance_id = request.GET.get('instance_id')
    result = get_job_instance_log(biz_id, job_instance_id,request.user.username)
    data = {
        "data": result
    }
    return JsonResponse(data)


def job_detail(request):
    """
        :param request:
        传递参数
        :param 业务id       biz_id,
        :param 作业实例id    instance_id,
        :return:
        """
    biz_id = request.GET.get('biz_id')
    job_id = request.GET.get('job_id')
    data = cc_get_job_detail(biz_id, job_id, request.user.username)
    return JsonResponse(data)


def fast_push_file(request):
    biz_id = request.GET.get('biz_id')
    file_target_path = "/tmp/"
    target_ip_list = [{
      "bk_cloud_id": 0,
      "ip": "192.168.240.52"
    },
        {
      "bk_cloud_id": 0,
      "ip": "192.168.240.55"
    }
    ]
    file_source_ip_list = [{
            "bk_cloud_id": 0,
            "ip": "192.168.240.43"
        }
    ]
    file_source = ["/tmp/test12.txt","/tmp/test123.txt"]
    data = cc_fast_push_file(biz_id, file_target_path, file_source, target_ip_list, file_source_ip_list,request.user.username)
    return JsonResponse(data)

#endregion