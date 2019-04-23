#!/bin/python3
import os
import sys
import datetime
import logging
from copy import deepcopy as copy
import sqlite3
from arch4edu import telegram, weibo, twitter
from nicelogger import enable_pretty_logging
import config

supported_archs = ['x86_64', 'armv6h', 'armv7h', 'aarch64']
db = sqlite3.connect('file:%s?mode=ro' % config.pkginfo_db, uri=True)
today = datetime.datetime.now().date()
recent_threshold = today - datetime.timedelta(days=7)
logger = logging.getLogger()
enable_pretty_logging('DEBUG')

def get_last_update(pkgname, arch):
    records = [i[0] for i in db.execute('''
        select mtime from pkginfo where pkgname = '%s' and forarch = '%s' order by mtime desc limit 2
        ''' % (pkgname, arch))]
    if len(records) < 2:
        return None
    else:
        return records[1]

def merge_events(events):
    by_packages = sorted(list(set([(i[0], i[2], i[3]) for i in events])))
    result = []
    for i in by_packages:
        archs = [(i[0], j, i[1], i[2]) in events for j in supported_archs]
        if not False in archs:
            result.append((i[0], 'all', i[1], i[2]))
        elif archs.count(True) == 1:
            result.append((i[0], supported_archs[archs.index(True)], i[1], i[2]))
        elif not False in archs[1:]:
            result.append((i[0], 'all_arm', i[1], i[2]))
        elif not archs[0] and archs[1] and archs[2]:
            result.append((i[0], 'armv{6,7}h', i[1], i[2]))
        elif archs[0] and archs[1] and archs[2]:
            result.append((i[0], supported_archs[0], i[1], i[2]))
            result.append((i[0], 'armv{6,7}h', i[1], i[2]))
        else:
            for j in range(len(archs)):
                if archs[j]:
                    result.append((i[0], supported_archs[j], i[1], i[2]))
    by_verions = set([i[1:] for i in result])
    result2 = []
    for i in by_verions:
        packages = [j for j in result if j[1:] == i]
        packages.sort(key=lambda i:(len(i[0]), i[0]))
        if len(packages) == 1:
            result2.append(packages[0] + (pkgstats.search(packages[0][0]).count, ))
        else:
            groups = []
            for j in packages:
                fit = False
                for k in range(len(groups)):
                    if fit_group(j, groups[k]):
                        groups[k].append(j)
                        fit = True
                        break
                if not fit:
                    groups.append([j])
            for j in groups:
                if len(j) == 1:
                    result2.append(j[0] + (pkgstats.search(j[0][0]).count, ))
                    continue
                l, r = find_pattern([k[0] for k in j])
                if r == 0:
                    package = '%s{%s}' % (j[0][0][:l], ','.join(sorted([k[0][l:] for k in j])))
                else:
                    package = '%s{%s}%s' % (j[0][0][:l], ','.join(sorted([k[0][l:-r] for k in j])), j[0][0][-r:])
                if package == '{,kaldi}openfst':
                    print(j, l, r)
                    sys.exit()
                result2.append((package, j[0][1], j[0][2], j[0][3], sum([pkgstats.search(k[0]).count for k in j])))
            if len(groups) > 1:
                logger.debug(groups)
    return sorted(result2)

def find_pattern(packages):
    i = packages[0]
    try:
        l = 0
        while not False in [i[l] == j[l] for j in packages]:
            l += 1
    except:
        pass
    try:
        r = 1
        while not False in [i[-r] == j[-r] for j in packages]:
            r += 1
    except:
        pass
    finally:
        r -= 1
    return l, r

def fit_group(package, group):
    packages = [i[0] for i in group]
    packages.append(package[0])
    l, r = find_pattern(packages)
    if l > 3 or l + r > min([len(i) for i in packages]) / 2:
        return True
    return False

def limited_report(convert_to_report, events, limit=140):
    _events = copy(events)
    by_pkgstats = copy(events)
    by_pkgstats.sort(key=lambda i:(-len(i[3]), i[4]))
    report = convert_to_report(_events)
    while len(report) > limit:
        logger.warning(by_pkgstats[0])
        _events.remove(by_pkgstats[0])
        del by_pkgstats[0]
        report = convert_to_report(_events)
    return report

if __name__ == '__main__':
    sys.path.append('./pkgstats')
    import pkgstats
    pkgstats.djangorm.migrate()

    print(today)

    records = sorted([i for i in db.execute('''
        select pkgname, forarch, pkgver
        from pkginfo where pkgrepo = 'arch4edu' and mtime > %s and forarch != 'any'
        ''' % today.strftime('%s'))])

    i = 0
    while i < len(records) - 1:
        k = i
        while k < len(records) - 1 and records[k + 1][0] == records[k][0] and records[k + 1][1] == records[k][1]:
            k += 1
        if k != i:
            records = records[:i] + records[k:]
            i += 1
        else:
            i = k + 1

    events = []
    for i in records:
        last_update = get_last_update(i[0], i[1])
        if last_update is None:
            logger.info((i, 'is a new package.'))
            events.append(i + ('new', ))
        elif last_update > int(recent_threshold.strftime('%s')):
            logger.debug((i, 'has been updated recently.'))
        else:
            logger.info((i, 'has been updated.'))
            events.append(i + ('update', ))

    events = merge_events(events)

    report = telegram.to_telegram(events)
    print(report)
    if len(sys.argv) > 1 and sys.argv[1] == 'post':
        telegram.send(report)

    report = limited_report(weibo.to_weibo, events, 121)
    print(len(report), report)
    if len(sys.argv) > 1 and sys.argv[1] == 'post':
        weibo.send(report)

    report = limited_report(twitter.to_twitter, events, 280)
    print(len(report), report)
    if len(sys.argv) > 1 and sys.argv[1] == 'post':
        twitter.send(report)
