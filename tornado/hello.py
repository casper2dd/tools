import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import torndb
import json
import datetime

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        hostaddress = '127.0.0.1:3306'
        mydb = 'my_db'
        user = 'root'
        password = ''
        d = datetime.datetime.now()
        time = '{:%Y-%m-%d %H:%M:%S}'.format(d)
        opt = self.get_argument('opt')
        #self.write(greeting + ', friendly user!')
        db=torndb.Connection(hostaddress,mydb,user,password)
        if opt == 'insert':
            name = self.get_argument('name')
            ip = self.get_argument('ip')
        #greeting = self.get_argument('type')
            #ql = "INSERT INTO roles (name,ip,opttime) VALUES (%s,%s,date_format(NOW(),'%Y-%m-%d'))"%(name,ip)
            ql = "INSERT INTO roles (name,ip,opttime) VALUES (%s,%s,%s)"
            db.insert(ql,name,ip,time)
            self.write('ok') 
        elif opt == 'selectall':
            ql =db.query('select *  from roles')
            self.write(json.dumps(ql))
        elif opt == 'select':
            name = self.get_argument('name')
            ql = db.get('select * from roles where name = \'%s\''%name)
            self.write(json.dumps(ql))
        elif opt == 'update':
            name = self.get_argument('name')
            ip = self.get_argument('ip')
            pk = self.get_argument('pk')
            ql = "update roles set name = \'%s\',ip = \'%s\',opttime = \'%s\' where id = %s"%(name,ip,time,pk)
            db.execute(ql)
            self.write('ok') 
        elif opt == 'delete':
            pk = self.get_argument('pk')
            ql = "delete from roles where id = %s"%(pk)
            db.execute(ql)
            self.write('ok') 
         

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
