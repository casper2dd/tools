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
#conf_file = 'cpu.txt'                                                           
#path = os.path.join(dir,conf_file)                                               
config = ConfigParser.RawConfigParser()                                          
config.read(path)      

upperlimit = int(config.get('cpu', 'upperlimit'))
interval = int(config.get('cpu', 'interval'))


def getcpupercent(interval=5):
    return psutil.cpu_percent(interval)

cpupercent = getcpupercent(interval)
result = {}
res_enctype = "1"
if cpupercent > upperlimit:
    value = ("CPU used: %s %%" % cpupercent)
    status = "error"
else:
    #value = ("CPU used: %s " % cpupercent)
    value = ("CPU used: %s %%" % cpupercent)
    status = "normal"
result = {"result": value, "status": status, "res_enctype":res_enctype}
jsonresult = json.dumps(result)
print jsonresult
