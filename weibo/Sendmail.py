# -*- coding: cp936 -*-

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time

date=time.strftime('%Y-%m-%d',time.localtime(time.time()))

def sendmail(dest_mw_path,dest_ms_path,dest_yer_path,dest_ys_path):

#创建一个带附件的实例
 msg = MIMEMultipart()

#构造附件
 att1 = MIMEText(open(dest_mw_path, 'rb').read(), 'base64', 'gb2312')
 att1["Content-Type"] = 'application/octet-stream'
 att1["Content-Disposition"] = 'attachment; filename="美文.txt"'#这里的filename可以任意写，写什么名字，邮件中显示什么名字
 msg.attach(att1)

#构造附件
 att2 = MIMEText(open(dest_ms_path, 'rb').read(), 'base64', 'gb2312')
 att2["Content-Type"] = 'application/octet-stream'
 att2["Content-Disposition"] = 'attachment; filename="美食.txt"'#这里的filename可以任意写，写什么名字，邮件中显示什么名字
 msg.attach(att2)

#构造附件
 att3 = MIMEText(open(dest_yer_path, 'rb').read(), 'base64', 'gb2312')
 att3["Content-Type"] = 'application/octet-stream'
 att3["Content-Disposition"] = 'attachment; filename="育儿.txt"'#这里的filename可以任意写，写什么名字，邮件中显示什么名字
 msg.attach(att3)

#构造附件
 att4 = MIMEText(open(dest_ys_path, 'rb').read(), 'base64', 'gb2312')
 att4["Content-Type"] = 'application/octet-stream'
 att4["Content-Disposition"] = 'attachment; filename="养生.txt"'#这里的filename可以任意写，写什么名字，邮件中显示什么名字
 msg.attach(att4)

#加邮件头
 msg['to'] = '***'
 #msg = MIMEText('辛苦倍思冬',_subtype='plain',_charset='gb2312')
 #msg['to'] = '****'
 #msg['from'] = '****'
 msg['from'] = '****1@163.com'
 msg['subject'] =date+ u'BB 资料收集****'
 

#发送邮件
 try:
    server = smtplib.SMTP()
    server.connect('smtp.163.com')
    server.login('****','*****')#XXX为用户名，XXXXX为密码
    server.sendmail(msg['from'], msg['to'],msg.as_string())
    server.quit()
    print '发送成功'
 except Exception, e:  
    print str(e) 