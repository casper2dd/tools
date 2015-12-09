#! /usr/bin/env python
#-*- encoding: utf-8 -*-
import requests
import base64
import re
import urllib
import rsa
import json
import binascii
import urllib2
from StringIO import StringIO
import gzip
import os
import random
import Sendmail
from sgmllib import SGMLParser
from HTMLParser import HTMLParser







writeStr=os.linesep
configpath='D:\\liancheng\\weibo\\config_url_mw.txt'
configpath_ms='D:\\liancheng\\weibo\\config_url_ms.txt'
configpath_yer='D:\\liancheng\\weibo\\config_url_yer.txt'
configpath_ys='D:\\liancheng\\weibo\\config_url_ys.txt'

dest_mw_path='D:\\liancheng\\weibo\\meiwen.txt'
dest_ms_path='D:\\liancheng\\weibo\\meishi.txt'
dest_yer_path='D:\\liancheng\\weibo\\yuer.txt'
dest_ys_path='D:\\liancheng\\weibo\\yangsheng.txt'

username = '*****'
password = '*****'
session = requests.Session()
url_prelogin ='http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=cycheng19880731@hotmail.com&rsakt=mod&client=ssologin.js(v1.4.2)'
url_login='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
resp = session.get(url_prelogin)
json_data  = re.search('\((.*)\)', resp.content).group(1)
data       = json.loads(json_data)
servertime = data['servertime']
nonce      = data['nonce']
pubkey     = data['pubkey']
rsakv      = data['rsakv']
username_ = urllib.quote(username)
username = base64.encodestring(username)[:-1]
rsaPublickey = int(pubkey, 16)
key = rsa.PublicKey(rsaPublickey, 65537) 
message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
passwd = rsa.encrypt(message, key)
passwd = binascii.b2a_hex(passwd)
postdata ={"entry" : 'weibo', "gateway" : '1', "from" : '', "savestate" : '7', "useticket" : '1', "ssosimplelogin" : '1', "su" : username, "service" : 'miniblog', "servertime" : servertime, "nonce" : nonce, "pwencode" : 'rsa2', "sp" : passwd, "encoding" : 'UTF-8', "rsakv" : '1330428213', "url" : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack', "returntype" : 'META'}
resp = session.post(url_login,data=postdata)
p = re.compile('location\.replace\(\'(.*?)\'\)')
#print resp.content
login_url = p.search(resp.content).group(1)
#login_url0 = p.search(resp.content).group(0)   
#login_url = p.search(resp.content).lastindex
#print login_url
#print login_url0

try:
    login_url = p.search(resp.content).group(1)
    resp_final = session.get(login_url)
    print "login success"
except:
    print 'Login error!'

#meiwen
config_url=open(configpath,'r')
config_url_list=config_url.readlines()

#if os.path.exists(dest_mw_path):
#   os.remove(dest_mw_path)

t=open(dest_mw_path,'w')

for url in config_url_list:
    #print url
    txt=session.get(url)
    content1=txt.content
    contents=re.findall(r'<em>.*?<\\/em>',content1)
    content="".join(contents)
    contentnostart=content.replace('<em>','')
    contentlist=contentnostart.split("<\\/em>")

    
    t.write(url+writeStr)
    for i in contentlist:
        i2=re.sub(r'<.*>','',i)
        content8=i2+writeStr+writeStr+writeStr
        #i2=str(i)
        num=len(str(i))
        #print type(i)
        if num>100:
           t.write(content8)
t.close()
config_url.close()

#meishi
config_url=open(configpath_ms,'r')
config_url_list=config_url.readlines()

#if os.path.exists(dest_ms_path):
#   os.remove(dest_ms_path)

t=open(dest_ms_path,'w')

for url in config_url_list:
    txt=session.get(url)
    content1=txt.content
    contents=re.findall(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>.*?<\\/div>',content1)
    content="".join(contents)
    contentnostart=re.sub(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>\\n\s+','',content)
    contentnoend=re.sub(r'\s+<\\/div>',writeStr+writeStr,contentnostart)
    t.write(contentnoend+writeStr+writeStr)

t.close()   
config_url.close()

#yuer
config_url=open(configpath_yer,'r')
config_url_list=config_url.readlines()


t=open(dest_yer_path,'w')

for url in config_url_list:
    txt=session.get(url)
    content1=txt.content
    contents=re.findall(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>.*?<\\/div>',content1)
    content="".join(contents)
    contentnostart=re.sub(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>\\n\s+','',content)
    contentnoend=re.sub(r'\s+<\\/div>',writeStr+writeStr,contentnostart)
    contentnoend=re.sub(r'<a.*>.*?<\\/a>','',contentnoend)
    contentnoend=re.sub(r'<img\s.*\\/>','',contentnoend)
    
    t.write(contentnoend+writeStr+writeStr)

t.close()   
config_url.close()
    


#yangsheng
config_url=open(configpath_ys,'r')
config_url_list=config_url.readlines()


t=open(dest_ys_path,'w')

for url in config_url_list:
    txt=session.get(url)
    content1=txt.content
    #print content1
    contents=re.findall(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>.*?<\\/div>',content1)
    content="".join(contents)
    contentnostart=re.sub(r'<div class=\\"WB_text.*\\" node-type=\\"feed_list_content\\" nick-name=\\"\S+>\\n\s+','',content)
    contentnoend=re.sub(r'\s+<\\/div>',writeStr+writeStr,contentnostart)
    t.write(contentnoend+writeStr+writeStr)

t.close()   
config_url.close()

    


Sendmail.sendmail(dest_mw_path,dest_ms_path,dest_yer_path,dest_ys_path)










