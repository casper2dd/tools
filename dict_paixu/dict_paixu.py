#!/usr/bin/env python


f = open('./apache','r')
content = f.readlines()

f.close()
dict = {}
for i in content:
    line = i.strip('\n')
    l = line.split(' ')
    if len(l) > 1:
        key = int(l[3])
        dict[key] = line
      #  dict[line] = l[3]
print dict
result = sorted(dict.iteritems(),key = lambda d:d[0], reverse = True)
#result = sorted(dict.iteritems(),key = lambda d:d[0], reverse = False)
print result
for j in result:
    print j[1]
#list = content.split(' ')
#print list
