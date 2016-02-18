#!/usr/bin/python
# conding=utf-8
'''
海外根据xml录入服务器信息到omcenter
'''
import xml.dom.minidom
import os
import sys
import MySQLdb


def get_xmlnode(node, name):
    '''
    获取xml元素
    '''
    return node.getElementsByTagName(name) if node else []


def get_attrvalue(node, attrname):
    '''
    获取xml属性
    '''
    return node.getAttribute(attrname) if node else ''


def get_nodevalue(node, index=0):
    return node.childNodes[index].nodeValue if node else ''


def do_copy(src, dest):
    shutil.copyfile(src, dest)


def do_systemrun(command):
    os.system(command)


def xml_to_string(filename='user.xml'):
    doc = xml.dom.minidom.parse(filename)
    return doc.toxml('UTF-8')


def get_documentElement(filename='./test.xml'):
    dom = xml.dom.minidom.parse(filename)
    return dom.documentElement


def initMysqldb():
    global dbhost, dbuser, dbpswd, dbname, dbcharset, db, cursor
    db = MySQLdb.connect(host=dbhost, user=dbuser,
                         passwd=dbpswd, db=dbname, charset=dbcharset)
    cursor = db.cursor()
    db.autocommit(True)


def buildTable(tbname, sqlList):
    cursor.execute("truncate %s" % tbname)
    for key in sqlList:
        sql = "INSERT INTO %s%s" % (tbname, key)
        cursor.execute(sql)
    return(0)


def test():
    sql = 'select count(*) from cmdb'
    cursor.execute(sql)
    b = cursor.fetchall()
    print b

dbhost = "127.0.0.1"
dbuser = "root"
dbpswd = ""
dbname = "omcenter"
dbcharset = "utf8"

'''main'''
initMysqldb()
test()

filename = sys.argv[0]
conf_file = 'wanmei.monitor.xml'

#dir = os.path.basename()
dir = os.path.dirname(os.path.abspath(filename))
##conf_file = 'mem.txt'
path = os.path.join(dir, conf_file)

print path


doc = get_documentElement(path)


games = get_xmlnode(doc, "game")
sqllist = []

for game in games:
    game_name = get_attrvalue(game, "name")
    game_id = get_attrvalue(game, "gameId")
    game_country = get_attrvalue(game, "country")
    game_countryid = get_attrvalue(game, "countryId")
    logicservers = get_xmlnode(game, "logicServer")
    for logicserver in logicservers:
        logicservernames = get_xmlnode(logicserver, "name")
        for logicservername in logicservernames:
            server_name = get_nodevalue(logicservername)
        servers = get_xmlnode(logicserver, "server")
        for server in servers:
            server_id = get_attrvalue(server, "serverId")
            server_ip = get_attrvalue(server, "ip")
            status = 'unknown'
            item = 'unknown'
            type = 'unknown'
            hostname = 'unknown'
            is_virtual = 'unknown'
            item_type = 'unknown'
            item_id = 'unknown'
            group_id = 'unknown'
            os = 'unknown'
            idc = 'unknown'
        print "game_name is %s ,game_id is %s , game_country is %s , game_countryid is %s , server_name is %s , serverid is %s" % (game_name, game_id, game_country, game_countryid, server_name, server_id)
        st = game_country + game_id + server_id
        line = "(status,manager_ip,innerip,item,type,hostname,is_virtual,st,item_type,item_id,group_id,os,idc) values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" \
            % (status, server_ip, server_ip, item, type, hostname, is_virtual, st, item_type, item_id, group_id, os, idc)
        sqllist.append(line)
buildTable('cmdbliancheng', sqllist)
