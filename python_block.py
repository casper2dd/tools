#过滤列表
list = [x for x in list if x.strip() != '']

#一行一行写文件
with open('/path/file','r') as f:
    for line in f:
        print line

#逐行读文件
f = open('/path/file','w')
for e in slist:
    f.write(e + '\n')
f.close()

#正则匹配搜索
m = re.search('\d+-\d+',line)
#like 123-123
if m:
    current = m.group(0)

#查询数据库
db = MySQLdb.connect('localhost','username','passwd','dbname')
cursor = db.cursor()
sql = 'select * from user'
cursor.execute(sql)
results = cursor.fetchall()
for row in results:
    print row[0] + rou[1]
db.close()

#指定字符串链接
thelist = ['a','b','c']
joinstring = ','.join(thelist)

#去除重复元素
targetlist = list(set(abc_list))

#在一列字符串中去除空字符串
targetlist = [v for v in targetlist if not v.strip() == '']
#or
targetlist = filter(lambda x:len(x)>0,targetlist)

#讲一个列表连接到另一个列表后面
anoterlist.extend(alist)

#遍历一个字典
for k,v in dict.iteritems():
    print k+v

#检查一列字符串中是否有任何一个出现在指定字符串里
if any(x in targetstring for x in alist):
    print 'true'