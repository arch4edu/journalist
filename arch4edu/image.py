#!/bin/python3
import pygame
from arch4edu.weibo import display_arch

pygame.init()

class Report:

    def __init__(self, max_length=28):
        self.report = ['']
        self.max_length = max_length

    def append(self, text):
        if len(self.report[-1] + text) < self.max_length:
            self.report[-1] += text
        else:
            self.report.append(text)

    def newline(self):
        self.report.append('')
        self.report.append('')

    def __repr(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join(self.report).strip('\n')

def convert_to_image(text):
    font = pygame.font.SysFont('WenQuanYi Zen Hei', 64)
    ftext = font.render(text, True, (0, 0, 0), (255, 255, 255))
    pygame.image.save(ftext, "/tmp/weibot.jpg")

def to_image(events):

    report = Report()
    for arch in ['all', 'x86_64', 'all_arm', 'armv{6,7}h'] + supported_archs[1:]:
        new_event = [i for i in events if i[1] == arch and i[3] == 'new']
        update_event = [i for i in events if i[1] == arch and i[3] == 'update']
        if len(str(report)) == 0:
            report.append('今日')
        if len(new_event + update_event) > 0:
            report.append(display_arch(arch))
        if len(new_event):
            report.append('新增了')
            for i in new_event[:-1]:
                report.append(i[0] + '、')
            if len(update_event) > 0:
                report.append(new_event[-1][0] + '，')
            else:
                report.append(new_event[-1][0] + '。')
        if len(update_event):
            for i in update_event[:-1]:
                report.append(i[0])
                report.append('更新至')
                report.append(i[2] + '，')
            report.append(update_event[-1][0])
            report.append('更新至')
            report.append(update_event[-1][2])
            report.append('。')
        if len(new_event + update_event) > 0:
            report.newline()
