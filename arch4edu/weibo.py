#!/bin/python3
from weibo import Client
from arch4edu.telegram import order
import config
client = Client(config.weibo_appid, config.weibo_app_secret, config.weibo_redirect_url, username=config.weibo_username, password=config.weibo_password)

url = 'http://t.cn/EXw71o1'

def display_arch(arch):
    if arch == 'all':
        return '全平台'
    elif arch == 'all_arm':
        return '全ARM平台'
    return arch + '平台'

def to_weibo(events):

    report = ''
    for arch in order:
        new_event = [i for i in events if i[1] == arch and i[3] == 'new']
        update_event = [i for i in events if i[1] == arch and i[3] == 'update']
        if len(new_event + update_event) > 0 and len(report) == 0:
            report = '今日arch4edu中'
        if len(new_event + update_event) > 0:
            report += display_arch(arch)
        if len(new_event):
            report += '新增了'
            for i in new_event[:-1]:
                report += i[0] + '、'
            if len(update_event) > 0:
                report += new_event[-1][0] + '，'
            else:
                report += new_event[-1][0] + '。'
        if len(update_event):
            report += '更新了'
            for i in update_event[:-1]:
                report += i[0] + '、'
            report += update_event[-1][0] + '。'
    return report

def send(report):
    client.post('statuses/share', status=report+url)
