#!/usr/bin/python
#conding=utf-8
import os
import xml.dom.minidom
import shutil
import re,sys,commands,time
import logging,logging.config

def cando():
    cmd="ps -ef | grep -w 'package' | grep -v $$ | wc -l"
    output=commands.getoutput(cmd)
    if output != "0":
       print "package is running\n"
       sys.exit(2)

def usage():
    print "usage: package install <server.xml> <apps=app1[,app2...]|noapps=app1[,app2...]|group=groupname>\n"
    sys.exit(2)

def log_debug(msg):
    logging.config.fileConfig('logging.config')
    logger=logging.getLogger('root')
    logger.info(msg)

def log(msg):
    logging.config.fileConfig('logging.config')
    logger=logging.getLogger('debug')
    logger.info(msg)




def get_xmlnode(node,name):
    return node.getElementsByTagName(name) 

def get_attrvalue(node,attrname):
    return node.getAttribute(attrname)

def do_copy(src,dest):
    shutil.copyfile(src,dest)

def do_systemrun(command):
    os.system(command)

def xml_to_string(filename='user.xml'):
    doc = xml.dom.minidom.parse(filename)
    return doc.toxml('UTF-8')

def get_documentElement(filename='./test.xml'):
    dom = xml.dom.minidom.parse(filename)
    return dom.documentElement

def do_replace(file,src,dest):
    dir_dest=dirname(file)+'/dest.txt'
    dir_back=file+'.bak'
    file_src=open(file,'r')
    file_dest=open(dir_dest,'w')
    for line in file_src.readlines():
        line_dest=re.sub(src,dest,line)
        file_dest.write(line_dest)
    file_dest.close()
    file_src.close()
    if os.path.exists(dir_back):
       os.remove(dir_back) 
    os.rename(file, dir_back) 
    os.rename(dir_dest, file)


def do_mvbak(filename):
    os.rename(filename,filename+r'.bak')
 

def do_createfile(filename,content):
    tmp_path=filename
    content=re.sub(r'\\n',r'\n',content) 
    content=re.sub(r'\n\s+',r'\n',content)
    content=re.sub(r'^\s+','',content)
    file_tmp=open(tmp_path,'w')
    file_tmp.writelines(content)
    file_tmp.close()


def check_exist(filename):
    if os.path.exists(filename):
       return True
    else:
       print "\'%s\': No such file or directory." %filename
       sys.exit(2) 

def dirname(filename):
    dir=os.path.dirname(filename)
    return dir



def do_mkdir(dir):
    os.mkdir(dir)

def get_apps():
    app_xml=[]
    doc=get_documentElement('./test.xml')
    gamedoc=get_xmlnode(doc,'application')
    for app in gamedoc: 
        app_name=get_attrvalue(app,'name')
        app_xml.append(app_name)
    check=be_single(app_xml)
    if check!=0:
       print ("More than on " + check)
       sys.exit(2)
    else:
       return app_xml

def be_single(app_xml):
    for tempstr in app_xml:
        p=app_xml.count(tempstr)
        if p>1:
           return tempstr
    return 0


def get_do_apps(action,app_list):
    do_apps=[]
    app_xml=get_apps()
    if action == 'except':
       do_apps=app_xml
       undo_list=app_list.split(r',')
       for str in undo_list:
           p=undo_list.count(str)
           t=do_apps.count(str)
           if p>1:
              print "There has the same apps name " + str + " in 'noapps'\n"
              sys.exit(2)  
           if t<1:
              print "Don't have " + str +" in xml\n"
              sys.exit(2)
           elif t == 1: do_apps.remove(str)
    elif action == 'do':
         do_list=app_list.split(r',')
         if len(do_list) == 1 and do_list[0] == 'all':
            do_apps=app_xml
            return do_apps
         for str in do_list:
             p=app_xml.count(str)
             if p>1:
                print "There has the same apps name " + str + " in xml\n"
                sys.exit(2)
             elif p<1:
                print "Don't have " + str +" in xml\n"
                sys.exit(2)
             havein=do_list.count(str)
             if havein == 1:
                do_apps.append(str)
             else:
                print "There has the same apps name " + str + " in 'apps'\n"
                sys.exit(2)
    return do_apps
# print do_apps

#def get_do_group(groupname):
# doc=get_documentElement('/root/test.xml')
# groupslist=get_xmlnode(doc,'groups')
# groupsdoc=groupslist[0]
# groupdoc=get_xmlnode(groupsdoc,'group') 
# for group in groupdoc:
#  name=get_attrvalue(group,'name')
#  if name == groupname:
#   do_list=get_attrvalue(group,'apps')
#   break
#  else:
#   print "No group " + groupname + " in xml"
#   sys.exit(2)
# do_apps=get_do_apps('do',do_list)
# return do_apps


def get_do_group(groupname):
    flag=0
    doc=get_documentElement('./test.xml')
    groupslist=get_xmlnode(doc,'groups')
    groupsdoc=groupslist[0]
    groupdoc=get_xmlnode(groupsdoc,'group')
    for group in groupdoc:
        name=get_attrvalue(group,'name')
        if name == groupname:
           flag=1
           final_group=group
           break
    if flag == 1:
       do_list=get_attrvalue(group,'apps')
    else:
       print "No group " + groupname + " in xml"
       sys.exit(2)
    do_apps=get_do_apps('do',do_list)
    return do_apps

#   do_list=get_attrvalue(group,'apps')
#   break
#  else:
#   print "No group " + groupname + " in xml"
#   sys.exit(2)
# do_apps=get_do_apps('do',do_list)
# return do_apps



#main start
if len(sys.argv) != 4:
   usage()

cando()

xmlfile=sys.argv[2]

if sys.argv[1] == 'install':
   if str(os.path.exists(xmlfile)) == 'False':
      print "There don't has file: " + xmlfile
      usage()
   elif sys.argv[3].startswith('noapps='):
        (tmp,except_list)=sys.argv[3].split('=')
        if len(except_list) == 0: usage()
        do_apps=get_do_apps('except',except_list)
   elif sys.argv[3].startswith('apps='):
        (tmp,do_list)=sys.argv[3].split('=')
        if len(do_list) == 0: usage()
        do_apps=get_do_apps('do',do_list)
   elif sys.argv[3].startswith('group='):
        (tmp,group)=sys.argv[3].split('=')
        if len(group) == 0: usage()
        do_apps=get_do_group(group)
   else:
        print "Input error\n"
        usage()
else:
     usage()

doc=get_documentElement('./test.xml')
networkdoc=get_xmlnode(doc,'network')
network=networkdoc[0]
hostdoc=get_xmlnode(network,'host')
host_list=[]
for host in hostdoc:
    host_name=get_attrvalue(host,'hostname')
    host_list.append(host_name)

check_str=be_single(host_list)
if check_str != 0:
   print "More than one " + check_str + " server configuration in the xml"
   sys.exit(2)

applications=get_xmlnode(doc,'application')
for app in applications:
    app_name=get_attrvalue(app,'name')
    check_name=do_apps.count(app_name)
    if check_name == 1:
       print "Installing: " + app_name + "\n"
       parts=get_xmlnode(app,'part')
       for part in parts:
           mkdirs= get_xmlnode(part,'mkdir')
           if len(mkdirs) > 0:
              for mkdir in mkdirs:
                  dir=get_attrvalue(mkdir,'dir')
                  host=get_attrvalue(mkdir,'host')
                  do_mkdir(dir)
   
           createfiles= get_xmlnode(part,'createfile')
           if len(createfiles) > 0:
              for createfile in createfiles:
                  filename=get_attrvalue(createfile,'file')
                  content=get_attrvalue(createfile,'content')
                  do_createfile(filename,content)
   
           copys=get_xmlnode(part,'copy')
           if len(copys) > 0:
              for copy in copys:
                  src=get_attrvalue(copy,'src')
                  dest=get_attrvalue(copy,'dest')
                  do_copy(src,dest)
   
           replaces=get_xmlnode(part,'replace')
           if len(replaces) > 0:
              for replace in replaces:
                  filename=get_attrvalue(replace,'file')
                  src=get_attrvalue(replace,'src')
                  dest=get_attrvalue(replace,'dest')
                  do_replace(filename,src,dest)
    
           systemruns=get_xmlnode(part,'systemrun')
           if len(systemruns) > 0:
              for systemrun in systemruns:
                  command=get_attrvalue(systemrun,'command')
                  do_systemrun(command)

           mvbaks=get_xmlnode(part,'mvbak')
           if len(mvbaks) > 0:
              for mvbak in mvbaks:
                  filename=get_attrvalue(mvbak,'file')
                  do_mvbak(filename)


   

     

#root=get_documentElement()
#user_nodes = get_xmlnode(root,'createfile')
#for node in user_nodes:
# file=get_attrvalue(node,'file')
# content=get_attrvalue(node,'content') 
# do_createfile('lianchengliancheng.txt',content)
#


   
#do_createfile('lianchengliancheng.txt',r'')









#do_replace(r'/root/lc/lc3.txt','456456','123123')










#print get_documentElement()


#dom = xml.dom.minidom.parse('/root/test.xml')

#root = dom.documentElement

#print (root)
'''root=get_documentElement()
user_nodes = get_xmlnode(root,'copy')

#print user_nodes

for node in user_nodes:
   src=get_attrvalue(node,'src')
   dest=get_attrvalue(node,'dest')
   do_copy(src,dest)



#command_list=get_xmlnode(root,'systemrun')
#print command_list    
#for node in command_list:
#    command=get_attrvalue(node,'command') 
 #   do_systemrun(command)
#print xml_to_string('/root/test.xml')'''
