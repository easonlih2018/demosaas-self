# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'hosts1'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^test/$', 'test'),
    (r'^modal/$', 'modal'),
    (r'^api/getJson/$', 'getJson'),
    (r'^api/getEchartsJson/$', 'getEchartsJson'),

    (r'^search_biz/$', 'search_biz'),
    (r'^search_set/$', 'search_set'),
    (r'^search_host/$', 'search_host'),
    (r'^fast_execute_script/$', 'fast_execute_script'),
    (r'^execute_job/$', 'execute_job'),
    (r'^job_detail/$', 'job_detail'),
    (r'^get_log_content/$', 'get_log_content'),
    (r'^fast_push_file/$', 'fast_push_file'),

    (r'^host1/$', 'host1'),
    (r'^host2/$', 'host2'),
    (r'^chart/$', 'chart'),
    (r'^hosts/$', 'hosts'),
    (r'^hosts1/$', 'hosts1'),

    (r'^search_biz_from_cmdb/$', 'search_biz_from_cmdb'),
    (r'^search_set_from_cmdb/$', 'search_set_from_cmdb'),
    (r'^search_host_from_cmdb/$', 'search_host_from_cmdb'),
    (r'^search_host_from_db/$', 'search_host_from_db'),
    (r'^create_host_to_db/$', 'create_host_to_db'),
    (r'^delete_host_from_db/$', 'delete_host_from_db'),
    (r'^update_host_remark/$', 'update_host_remark'),
    

    (r'^get_line_data/$', 'get_line_data'),
    (r'^get_histogram_data/$', 'get_histogram_data'),
    (r'^get_pie_data/$', 'get_pie_data'),
    (r'^get_mem_perf/$', 'get_mem_perf'),
    (r'^get_disk_perf/$', 'get_disk_perf'),
    (r'^get_avgload/$', 'get_avgload'),
    (r'^search_host_avgLoad/$', 'search_host_avgLoad'),
    (r'^show_performance/$', 'show_performance'),
    (r'^show_monitor/$', 'show_monitor'),
    
    

    (r'^test_celery/$', 'test_celery'),
    (r'^api/test/$', 'testapi'),
    
    

)
