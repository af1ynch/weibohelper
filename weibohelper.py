# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
import requests
from lxml import etree
import os
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class MailHelper(object):

    # 这个类实现发送邮件的功能

    def __init__(self):

        self.mail_host = "xxxxxx"     # 设置邮箱服务器
        self.mail_user = "xxxxx"     # 用户名
        self.mail_pass_w = "xxxx"    # 密码
        self.mail_postfix = "xxxx"  # 发件箱的后缀

    def send_mail(self, to_list, sub, _content):
        me = "twitterHelper" + "<" + self.mail_user + "@" + self.mail_postfix + ">"  # 发件人
        msg = MIMEText(_content, _subtype='plain', _charset='utf-8')  # 邮件内容
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)
        try:
            server = smtplib.SMTP()     # 开启邮箱服务
            server.connect(self.mail_host)
            server.login(self.mail_user, self.mail_pass_w)
            server.sendmail(me, to_list, msg.as_string())
            server.close()
            return True
        except Exception, e:
            print str(e)
            return False


class WeiBoHelper(object):

    # 此类实现爬取微博第一条内容

    def __init__(self):
        self.url = 'xxxxxxxxxxxxxxxxxx'  # 要爬取的微博地址
        self.url_login = 'https://login.weibo.cn/login/'
        self.new_url = self.url_login

    def getsource(self):
        html = requests.get(self.url).content
        return html

    def get_data(self, html):

        # 爬取模拟登录微博时要提交的表单数据

        selector = etree.HTML(html)
        password = selector.xpath('//input[@type="password"]/@name')[0]
        vk = selector.xpath('//input[@name="vk"]/@value')[0]
        action = selector.xpath('//form[@method="post"]/@action')[0]
        cap_id = selector.xpath('//input[@name="capId"]/@value')[0]
        img = selector.xpath('//img/@src')[0]   # 获取验证码图片
        print img
        code = raw_input()  # 输入验证码
        self.new_url = self.url_login + action
        _data = {
            'mobile': 'xxxxxxxxxxxxx',  # 新浪微博用户名
            password: 'xxxxxxxxxxxxx',  # 密码
            'code': code,
            'remember': 'on',
            'backURL': self.url,
            'backTitle': u'微博',
            'tryCount': '',
            'vk': vk,
            'capId': cap_id,
            'submit': u'登录'
        }
        return _data

    def get_content(self, form_data):
        new_html = requests.post(self.new_url, data=form_data).content  # 模拟登录新浪微博
        new_selector = etree.HTML(new_html)
        contents = new_selector.xpath('//span[@class="ctt"]')
        new_content = unicode(contents[2].xpath('string(.)')).replace('http://', '')   # 更新的微博内容
        send_time = new_selector.xpath('//span[@class="ct"]/text()')[0]
        send_text = new_content + send_time
        return send_text

    def tosave(self, text):

        # 保存微博内容

        f = open('weibo.txt', 'a')
        f.write(text + '\n')
        f.close()

    def tocheck(self, text):

        #  检查微博内容是否已经存在

        if not os.path.exists('weibo.txt'):
            return True
        else:
            f = open('weibo.txt', 'r')
            exist_wei_bo = f.readlines()
            if text + '\n' in exist_wei_bo:
                return False
            else:
                return True


if __name__ == '__main__':
    mail_to_list = ['xxxxxxxxxx']  # 收件人邮箱
    helper = WeiBoHelper()
    while True:
        source = helper.getsource()
        data = helper.get_data(source)
        content = helper.get_content(data)
        if helper.tocheck(content):
            if MailHelper().send_mail(mail_to_list, u'xx微博更新啦', content):
                print u'发送成功'
            else:
                print u'发送失败'
            helper.tosave(content)
            print content

        else:
            print u'pass'
        time.sleep(30)
