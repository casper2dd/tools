#!/usr/bin/env python                                                                                                           #coding=utf8
#coding=utf8

import psutil
import ConfigParser
import json
import os
import sys
filename = sys.argv[0]
conf_file = sys.argv[3]

#dir = os.path.basename()                                                                
dir = os.path.dirname(os.path.abspath(filename))
##conf_file = 'mem.txt'                                                           
path = os.path.join(dir,conf_file)

#dir = os.getcwd()
#conf_file = 'disk.txt'
#path = os.path.join(dir,conf_file)
config = ConfigParser.RawConfigParser()
config.read(path)

upperlimit = int(config.get('disk', 'upperlimit'))
mountpoint = config.get('disk', 'mountpoint')
mountpoint_list = mountpoint.split(',')

def __getdisklist():                                                              
    disk_list = []                                                                
    disk_partitions = psutil.disk_partitions()                                    
    for i in disk_partitions:                                                     
        mountpoint = i.mountpoint                                                 
        disk_list.append(mountpoint)                                              
    return disk_list                                                              
                                                                                                                      
def getDiskstate(disklist=None):                                                  
    diskstate = {}                                                                
    if not disklist:                                                              
        disklist = __getdisklist()                                                
        for disk in disklist:                                                         
            diskstate[disk] = psutil.disk_usage(disk).percent                         
    else:
        for disk in disklist:
            disk = disk.strip("'")
            diskstate[disk] = psutil.disk_usage(disk).percent
    return diskstate                        
diskpercent_dict = getDiskstate(mountpoint_list)
result = {}
value = []
res_enctype = "1" 
for d,n in diskpercent_dict.items():
    content = ("%s used: %s %%" %(d,n))
    value.append(content)
for d,n in diskpercent_dict.items():
    if n >= upperlimit:                                                          
        status = "error"
        break
    else:
        status = "normal"
result = {"result": ','.join(value), "status": status, "res_enctype":res_enctype}
jsonresult = json.dumps(result)
print jsonresult
