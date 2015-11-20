# coding=UTF-8
# script create by Konstantyn Davidenko
# mail: kostya_ya@it-transit.com
#
# __version__ == '0.1.0'
"""
server for fast search anonimous web chat
"""
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.websocket import WebSocketClosedError
import json
from tornado.options import define, options, parse_command_line
import os


define("port", default=80, help="run on the given port", type=int)

# we gonna store clients in dictionary..

# from client to server
# initial message
# {"sex": "M", "looking_sex": "F", "language": "en", "message': "init"}
# general send client
# {"message": "hello world"}
# {"message': "get_online"}


# from server to client
# initial message
# {"message": "connected", "connected": "true", "online": "1"}
# general message
# {"message": "hello world", "connected": "true", "online": "2"}

class Static:
    connections = []
    # clients = []
    # rooms = {}
    client_id = 0
    room_id = 0


class Room:
    id = 0
    clients = []
    full = False

    def __init__(self):
        self.clients = []
        self.full = False
        self.id = Static.room_id
        Static.room_id += 1

    def add_client(self, connection):
        self.clients.append(connection)
        if len(self.clients) >= 2:
            self.full = True

class Client:
    id = None
    sex = ''
    language = ''
    looking_sex = ''

    def __init__(self, client_id, sex, looking_sex, language, conn):
        self.conn = conn
        self.id = client_id
        self.sex = sex
        self.looking_sex = looking_sex
        self.language = language


# noinspection PyAbstractClass
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        try:
            host = os.environ['OPENSHIFT_APP_DNS']
            port = options.port
            uri = '/ws'
            self.render("client.html", **{'host': host, 'port': port, 'uri': uri})
        except:
            host = '0.0.0.0'
            port = options.port
            uri = '/ws'
            self.render("templates/client.html", **{'host': host, 'port': port, 'uri': uri})

    def post(self, *args, **kwargs):
        data = dict()
        data['online'] = len(Static.connections)
        response = json.dumps(data)
        self.write(response)

class IndexHandlerTest(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        try:
            host = os.environ['OPENSHIFT_APP_DNS']
            # port = os.environ['OPENSHIFT_PYTHON_PORT']
            port = options.port
            uri = '/ws'
            self.render("test.html", **{'host': host, 'port': port, 'uri': uri})
        except:
            host = '0.0.0.0'
            uri = '/ws'
            port = options.port
            self.render("templates/test.html", **{'host': host, 'port': port, 'uri': uri})


class WSHandler(tornado.websocket.WebSocketHandler):

    client = None
    room = None

    def open(self):
        Static.connections.append(self)

    def on_message(self, message):
        data = self.__serialize_json__(message)
        if not data:
            data = {'message': 'invalid data', 'data': message}
            self.__send_message__(data)
        elif data.get('message').lower() == 'init':
            client = self.__new_client__(data)
            self.client = client
            pair = self.__find_pair__()
            if pair:
                room = pair.room
                room.add_client(self)
                self.room = room
                self.__send_message__({'message': 'connected'})
            else:
                room = self.__get_new_room__()
                self.room = room
                room.add_client(self)
                self.room = room
        elif data.get('message').lower() == 'get_online':
            self.__send_message__(dict())
        else:
            self.__send_message__(data)

    @staticmethod
    def __serialize_json__(json_data):
        try:
            return json.loads(json_data)
        except Exception as e:
            print(e)

    def __new_client__(self, json_data):
        client = Client(client_id=Static.client_id, sex=json_data.get('sex'), looking_sex=json_data.get('looking_sex'), language=json_data.get('language'), conn=self)
        Static.client_id += 1
        return client

    def __send_message__(self, data):
        if not data.get('connected'):
            data['connected'] = 'true'
        data['online'] = len(Static.connections)
        for cli in self.room.clients:
            try:
                cli.write_message(data)
            except WebSocketClosedError:
                print('socket closed')

    def __find_pair__(self):
        for conn in Static.connections:
            if conn != self and not conn.room.full:
                if conn.client.sex == self.client.looking_sex and conn.client.looking_sex == self.client.sex:
                    return conn
        return None

    def __get_new_room__(self):
        return Room()

    def __leave_room__(self):
        data = {'connected': 'false'}
        self.__send_message__(data)

    def on_close(self):
        Static.connections.remove(self)
        self.__leave_room__()

handlers = [
    (r'/', IndexHandler),
    (r'/test', IndexHandlerTest),
    (r'/ws', WSHandler),
    (r'/get_online', IndexHandler)
]

app = tornado.web.Application(handlers)

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()