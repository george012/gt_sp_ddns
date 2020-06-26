# -*- coding: utf-8 -*-

import json
import urllib
import os
import time
from math import floor

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest

#   日志文件，可根据自己需求修改，必须 在本脚本目录下黄建 /logs 文件夹
gt_sp_log_path = os.path.dirname(os.path.abspath(__file__))+'/logs/run.log'
#   阿里云有权限管理域名的账号的AccessKey ID
gt_parmar_ak = 'AccessKey ID'
#   阿里云有权限管理域名的账号的AccessKey Secret
gt_parmar_ak_s = 'AccessKey Secret'
gt_parmar_data_format = 'json'

gt_parmar_domain_master = 'domain.com'
# 多个域名用 | 分割 例如：a.abc.com  b.abc.com  下列字符串传中应为“a|b”
gt_parmar_domain_second_heads = 'www'

# 循环运行读数/为了好记改分钟读数
gt_sleep_time = 60*10



# 写入文档
def gt_file_write(path, text):
    if os.path.exists(path):
        with open(path, mode='a', encoding='utf-8') as file:
            file.writelines(text)
            file.write('\n')
    else:
        with open(path, mode='w', encoding='utf-8') as file:
            file.writelines(text)
            file.write('\n')


def gt_file_write_and_clear(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(text)
        f.write('\n')

def gt_get_log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# log日志中新增条目
def gt_log_write_to_file(log_msg):
    gt_file_write(gt_sp_log_path, '%s  ----  %s' % (log_msg, gt_get_log_time()))


# 初始化log日志文件
def gt_log_setup_to_file():
    gt_file_write_and_clear(gt_sp_log_path, '%s  ----  %s' % ('初始化...', gt_get_log_time()))


def gt_get_my_ip():
    try:
        opener = urllib.request.urlopen('https://wtfismyip.com/text')
        strg = opener.read().decode('utf-8').replace('\n', '')
        return strg
    except:
        return None

# 浮点数保留小数点后几位格式化
# float_number 为浮点数
# digits 保留位数
def gt_float_formant(float_number, digits):
    # float_number *= 10 ** (digits + 2)
    return '{1:.{0}f}'.format(digits, floor(float_number) / 10 ** digits)


# 获取解析记录列表
def gt_get_domain_list_from_aliyum_return_recordId(gt_domain_second_head):
    client = AcsClient(gt_parmar_ak, gt_parmar_ak_s, 'cn-hangzhou')
    request = DescribeDomainRecordsRequest()
    request.set_accept_format(gt_parmar_data_format)

    request.set_DomainName(gt_parmar_domain_master)
    request.set_RRKeyWord(gt_domain_second_head)

    response = client.do_action_with_exception(request)
    # python2:  print(response)
    response_str = str(response, encoding='utf-8')
    resp_json = json.loads(response_str)

    reuren_dic = None
    for req_dic in resp_json["DomainRecords"]['Record']:
        cu_type = req_dic['Type']
        if cu_type == 'A':
            RecordiId = req_dic['RecordId']
            IP = req_dic['Value']
            reuren_dic = {'RecordiId': RecordiId, 'IP': IP}
            break

    return reuren_dic

def gt_update_dns_with_my_ip(my_ip, RecordiId, domain_second_heade):
    client = AcsClient(gt_parmar_ak, gt_parmar_ak_s, 'cn-hangzhou')

    request = UpdateDomainRecordRequest()
    request.set_accept_format(gt_parmar_data_format)
    request.set_Type('A')

    request.set_RR(domain_second_heade)
    request.set_Value(my_ip)
    request.set_RecordId(RecordiId)

    try:
        response = client.do_action_with_exception(request)
    except:
        return None

    # python2:  print(response)
    response_str = str(response, encoding='utf-8')
    resp_json = json.loads(response_str)
    re_id = resp_json['RecordId']
    if re_id == RecordiId:
        return 1
    else:
        return None

if __name__ == '__main__':

    while True:
        gt_log_setup_to_file()
        gt_log_write_to_file('--------------------\n[休眠结束开始新的轮回]\n--------------------\n')

        my_ip = gt_get_my_ip()
        if my_ip is None:
            gt_log_write_to_file('获取IP错误')
        else:
            s_d_h_arr = gt_parmar_domain_second_heads.split('|')

            for s_d_h in s_d_h_arr:
                rec = gt_get_domain_list_from_aliyum_return_recordId(s_d_h)
                rec_id = rec['RecordiId']
                rec_ip = rec['IP']
                if rec_ip == my_ip:
                    gt_log_write_to_file('IP 一致，不需要更改')
                else:
                    resp = gt_update_dns_with_my_ip(my_ip=my_ip, RecordiId=rec_id, domain_second_heade=s_d_h)
                    if resp is None:
                        gt_log_write_to_file('%s--错误--修改解析记录' % (s_d_h))
                    else:
                        gt_log_write_to_file('complate--- %s' % (s_d_h))
        # 休眠 10分钟

        gt_log_write_to_file('休眠 [%.2f] 分钟后继续' %(gt_sleep_time/60))
        time.sleep(gt_sleep_time)

