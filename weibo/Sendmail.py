# -*- coding: cp936 -*-

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time

date=time.strftime('%Y-%m-%d',time.localtime(time.time()))

def sendmail(dest_mw_path,dest_ms_path,dest_yer_path,dest_ys_path):

#����һ����������ʵ��
 msg = MIMEMultipart()

#���츽��
 att1 = MIMEText(open(dest_mw_path, 'rb').read(), 'base64', 'gb2312')
 att1["Content-Type"] = 'application/octet-stream'
 att1["Content-Disposition"] = 'attachment; filename="����.txt"'#�����filename��������д��дʲô���֣��ʼ�����ʾʲô����
 msg.attach(att1)

#���츽��
 att2 = MIMEText(open(dest_ms_path, 'rb').read(), 'base64', 'gb2312')
 att2["Content-Type"] = 'application/octet-stream'
 att2["Content-Disposition"] = 'attachment; filename="��ʳ.txt"'#�����filename��������д��дʲô���֣��ʼ�����ʾʲô����
 msg.attach(att2)

#���츽��
 att3 = MIMEText(open(dest_yer_path, 'rb').read(), 'base64', 'gb2312')
 att3["Content-Type"] = 'application/octet-stream'
 att3["Content-Disposition"] = 'attachment; filename="����.txt"'#�����filename��������д��дʲô���֣��ʼ�����ʾʲô����
 msg.attach(att3)

#���츽��
 att4 = MIMEText(open(dest_ys_path, 'rb').read(), 'base64', 'gb2312')
 att4["Content-Type"] = 'application/octet-stream'
 att4["Content-Disposition"] = 'attachment; filename="����.txt"'#�����filename��������д��дʲô���֣��ʼ�����ʾʲô����
 msg.attach(att4)

#���ʼ�ͷ
 msg['to'] = '***'
 #msg = MIMEText('���౶˼��',_subtype='plain',_charset='gb2312')
 #msg['to'] = '****'
 #msg['from'] = '****'
 msg['from'] = '****1@163.com'
 msg['subject'] =date+ u'BB �����ռ�****'
 

#�����ʼ�
 try:
    server = smtplib.SMTP()
    server.connect('smtp.163.com')
    server.login('****','*****')#XXXΪ�û�����XXXXXΪ����
    server.sendmail(msg['from'], msg['to'],msg.as_string())
    server.quit()
    print '���ͳɹ�'
 except Exception, e:  
    print str(e) 