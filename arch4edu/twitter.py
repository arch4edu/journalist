#!/bin/python3
import smtplib
from mailutils import assemble_mail
import arch4edu.telegram
import config

smtp = None

to_twitter = arch4edu.telegram.to_telegram

def setup_smtp():
    global smtp
    if smtp is None:
        smtp = smtplib.SMTP_SSL('smtp.ym.163.com', 994)
        smtp.login(config.twitter_ifttt_email, config.twitter_ifttt_password)

def send(report):
    setup_smtp()
    smtp.send_message(assemble_mail('#arch4edu', 'trigger@applet.ifttt.com', config.twitter_ifttt_email, text=report))
