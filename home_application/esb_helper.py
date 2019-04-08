# -*- coding: utf-8 -*-

import base64
import time
import requests
import json
import sys

from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
from common.log import logger

reload(sys)
sys.setdefaultencoding("utf8")


def run_fast_execute_script(biz_id, script_content, ip_list, username = "admin"):
    """
    快速执行脚本
    :param script_content: 脚本执行内容，str
    :param biz_id: 业务id
    :param ip_list: [{"ip":"10.0.0.10","bk_cloud_id":0}]
    :return: {"result": True, "data": "job_instance_id"}
    """
    
    url = BK_PAAS_HOST + '/api/c/compapi/v2/job/fast_execute_script/'
    execute_account = "root"
    param_content = ""
    script_timeout = 1000
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_biz_id": int(biz_id),
        "bk_username": username,
        "script_content": base64.b64encode(script_content),
        "ip_list": ip_list,
        "script_type": 1,
        "account": execute_account,
        "script_param": base64.b64encode(param_content),
        "script_timeout": script_timeout
    }
    response = requests.post(url, json.dumps(kwargs), verify = False)
    result = json.loads(response.content)

    if result["result"]:
        return {"result": True, "data": result["data"]["job_instance_id"]}

    else:
        return {"result": False, "data": result["message"]}


def run_execute_job(biz_id, job_id, ip_list, username="admin"):
    """
    快速执行脚本
    :param job_id: 作业模板id
    :param biz_id: 业务id
    :param ip_list: [{"ip":"10.0.0.10","bk_cloud_id":0}]
    :return: {"result": True, "data": "job_instance_id"}
    """

    url = BK_PAAS_HOST + '/api/c/compapi/v2/job/execute_job/'
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_token": "",
        "bk_username": username,
        "bk_biz_id": int(biz_id),
        "bk_job_id": int(job_id),
        "global_vars": [
            {
                "step_ids": [
                    4
                ],
                "ip_list": ip_list,
                "name": "id-201921816444771",
                "type": 2,
                "id": 2,
                "description": ""
            }
        ],
    }
    response = requests.post(url, json.dumps(kwargs), verify=False)
    result = json.loads(response.content)

    return result


def get_job_instance_log(biz_id, job_instance_id, username="admin", count=0):
    """
    获取脚本执行结果
    :param biz_id: 业务ID，
    :param job_instance_id: 作业实例id
    :param username: 执行用户
    :param count: 已重试的次数，直接调用不传
    :return: 脚本执行结果，
    list：[
    {
    "ip": '10.0.0.10',
     "log_content": '123',
     "bk_cloud_id": 0,
     "is_success": True
     }
     ]
    """
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "bk_biz_id": int(biz_id),
        "job_instance_id": int(job_instance_id)
    }
    url = BK_PAAS_HOST + "/api/c/compapi/v2/job/get_job_instance_log/"
    response = requests.post(url, json.dumps(kwargs), verify = False)
    result = json.loads(response.content)
    if not result["result"]:
        count += 1
        if count > 5:
            logger.error(result["message"])
            return []
        time.sleep(2)
        return get_job_instance_log(biz_id, job_instance_id, username, count)
    if result["data"][0]["is_finished"]:
        log_content = []
        for i in result["data"][0]["step_results"]:
            log_content += [{"ip": u["ip"], "log_content": u["log_content"], "bk_cloud_id": u["bk_cloud_id"], "is_success": i['ip_status'] == 9} for u in
                            i["ip_logs"]]
        return log_content
    else:
        count += 1
        if count > 5:
            return []
        time.sleep(2)
        return get_job_instance_log(biz_id, job_instance_id, username, count)
    
    return []

def run_script_and_get_log_content(biz_id, script, ip_list, username):
    """
    执行脚本，并返回执行结果
    """

    f_result = run_fast_execute_script(biz_id, script, ip_list, username)

    if f_result["result"]:
        job_instance_id = f_result["data"]
        result = get_job_instance_log(biz_id, job_instance_id, username)
        return result[0]["log_content"]

    else:
        return ""

def cc_search_host(biz_id, set_id, ip_list, username = "admin"):
    '''
    查询主机
    :param biz_id: 业务ID，int
    :param ips: 过滤ip
    :return: 查询主机结果
    '''
    url = BK_PAAS_HOST + "/api/c/compapi/v2/cc/search_host/"

    # region  请求json数据
  
    content = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "ip": {
            "data": ip_list,
            "exact": 1,
            "flag": "bk_host_innerip|bk_host_outerip"
        },
        "condition": [
        {
            "bk_obj_id": "host",
            "fields": ["bk_host_id","bk_host_name","bk_host_innerip"],
            "condition": []
        },
        {
            "bk_obj_id":"biz",
            "fields":["bk_biz_id","bk_biz_name"],
            "condition":[
                {
            	 	"field": "bk_biz_id",
                	"operator": "$eq",
                	"value": int(biz_id)
            	 }
            ]
        },
        {
            "bk_obj_id":"set",
            "fields":["bk_set_id","bk_set_name"],
            "condition":[
                {
            	 	"field": "bk_set_id",
                	"operator": "$eq",
                	"value": int(set_id)
            	 }
            ]
        }
        
    ],
    "page": {
        "start": 0,
        "limit": 10,
        "sort": "bk_host_id"
    },
    "pattern": ""
    }
    # endregion
    
    response = requests.post(url, json.dumps(content), verify=False)
    result = json.loads(response.content)

    return result


def cc_search_set(biz_id, username='admin'):
    '''
    查询集群
    :param biz_id: 业务ID，int
    :param ips: 过滤ip
    :return: 查询主机结果
    '''
    url = BK_PAAS_HOST + '/api/c/compapi/v2/cc/search_set/'
    search = {
    }
    content = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_token": "",
        "bk_username": username,
        "bk_biz_id": int(biz_id),
        "fields": [
            "bk_set_name",
            "bk_set_id"
        ],
        "condition": search,
        "page": {
            "start": 0,
            "limit": 100,
            "sort": "bk_set_name"
        }

    }
    response = requests.post(url, json.dumps(content), verify=False)
    result = json.loads(response.content)
    return result


def cc_search_biz(username='admin'):
    """
    查询业务
    """
    url = BK_PAAS_HOST + '/api/c/compapi/v2/cc/search_business/'

    #region 请求json数据
    content = {
        "bk_app_code" : APP_ID,
        "bk_app_secret" : APP_TOKEN,
        "bk_username" : username,
        "bk_supplier_id": 0,
        "fields" : [
            "bk_biz_id",
            "bk_biz_name"
        ],
        "condition" : {
            "bk_biz_name" : ""
        },
        "page" : {
            "start" : 0,
            "limit" : 100,
            "sort" :  ""
        }
        
    }
    #endregion

    response = requests.post(url, json.dumps(content), verify=False)
    result = json.loads(response.content)
    return result


def cc_get_job_detail(biz_id, job_id, username='admin'):
    """
    查询作业模板
    """
    url = BK_PAAS_HOST + '/api/c/compapi/v2/job/get_job_detail/'

    # region 请求json数据
    content = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "bk_biz_id": biz_id,
        "bk_job_id": job_id

    }
    # endregion

    response = requests.post(url, json.dumps(content), verify=False)
    result = json.loads(response.content)
    return result


def cc_fast_push_file(biz_id, file_target_path, file_source, target_ip_list, file_source_ip_list, username='admin'):
    """
    文件分发
    """
    url = BK_PAAS_HOST + '/api/c/compapi/v2/job/fast_push_file/'

    # region 请求json数据
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "bk_biz_id": int(biz_id),
        "file_target_path": file_target_path,
        "file_source": [
            {
                "files": file_source,
                "account": "root",
                "ip_list": file_source_ip_list
            }
        ],
        "ip_list": target_ip_list,
        "account": "root",
    }
    # endregion

    response = requests.post(url, json.dumps(kwargs), verify=False)
    result = json.loads(response.content)
    return result


def get_host_ip_list(ip):
    ip_list = []
    ip_list = ip.split(',')
    return ip_list