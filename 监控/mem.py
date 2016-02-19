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
#conf_file = 'mem.txt'                                                           
#path = os.path.join(dir,conf_file)                                               
config = ConfigParser.RawConfigParser()                                          
config.read(path)  


upperlimit = int(config.get('mem', 'upperlimit'))

def getMemorystate():
    phymem = psutil.virtual_memory()
    percent = phymem.percent
    used = str(__bytes2human(phymem.used))
    total = str(__bytes2human(phymem.total))
    return percent,used,total

def __bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y') 
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)

mempercent,memused,memtotal = getMemorystate()

result = {}
res_enctype = "1"
if mempercent > upperlimit:
    value = "Memory:%5s%% %6s/%s" % (mempercent,memused,memtotal)
    status = "error"
else:
    value = "Memory:%5s%% %6s/%s" % (mempercent,memused,memtotal)
    status = "normal"
result = {"result": value, "status": status, "res_enctype":res_enctype}
jsonresult = json.dumps(result)
print jsonresult
