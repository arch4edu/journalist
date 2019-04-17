#!/bin/python3
import os
import telegram
import config

bot = None
order = ['all', 'x86_64', 'all_arm', 'armv{6,7}h', 'armv6h', 'armv7h', 'aarch64']

def display_arch(arch):
    if arch == 'all':
        return 'all architectures'
    elif arch == 'all_arm':
        return 'all ARM architectures'
    return arch

def to_telegram(events):

    report = ''

    for arch in order:
        new_event = [i for i in events if i[1] == arch and i[3] == 'new']
        update_event = [i for i in events if i[1] == arch and i[3] == 'update']
        if len(new_event + update_event) > 0 and len(report) == 0:
            report = 'Today arch4edu '
        if len(new_event):
            report += 'added '
            for i in new_event[:-1]:
                report += i[0] + ', '
            if len(update_event) > 0:
                report += new_event[-1][0] + ' and '
            else:
                report += new_event[-1][0] + ' '
        if len(update_event):
            report += 'upgraded '
            for i in update_event[:-1]:
                report += i[0] + ', '
            report += update_event[-1][0] + ' '
        if len(new_event + update_event) > 0:
            report += 'for ' + display_arch(arch) + '; '
    report = report.strip()
    if len(report) > 0 and report[-1] == ';':
        report = report[:-1] + '.'
    return report

def setup_bot():
    global bot
    if bot is None:
        bot = telegram.Bot(token=config.telegram_token)

def send(report):
    os.environ['https_proxy'] = 'https://127.0.0.1:8123'
    if len(report) > 0:
        setup_bot()
        bot.send_message('@arch4edu', report)
    del os.environ['https_proxy']
