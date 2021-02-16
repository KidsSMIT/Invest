import socket
from flask import Flask, jsonify, request
import threading
import sys
import time
from werkzeug.serving import make_server
import sqlite3, json

app = Flask(__name__)
IP = socket.gethostbyname(socket.gethostname())
app.host = IP
app.port= 5000
@app.route('/', methods=['GET'])
def home():
    return 'Your flask app is working correctly'
@app.route('/check', methods=['GET'])
def check():
    re = {'Alive': True}
    return jsonify(re)
@app.route('/new_user', methods=['POST'])
def new_user():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor() 
    query = 'INSERT INTO users (id, name, password) VALUES (NULL,{},{})'.format(data['name'], data['password'])
    try:
        print(query)
        cursor.execute('INSERT INTO users VALUES (NULL,?,?)', (data['name'], data['password']))
        conn.commit()
        re = {'Success': True}
        return jsonify(re)
    except Exception as e:
        print(e)
        print('Problem at server on line 32')
    re = {'Success':False}
    return jsonify(re)
@app.route('/exact_user', methods=['POST'])
def api_user():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM users WHERE name="{}" and password="{}"'.format(data['username'], data['password'])
    try:
        print(query)
        cursor.execute(query)
        user = cursor.fetchone()
        print(user)
    except Exception as e:
        print(e)
        user = False
        print('Server issue at line 51')
    conn.close()
    if user:
        res = {'is_it_correct': True, 'data':user}
        return jsonify(res)
    else:
        res ={'is_it_correct':False}
    return jsonify(res) 
class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server(IP, 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

def start_server():
    global servers
    servers = ServerThread(app)
    servers.start()
    print('server started')

def stop_server():
    global servers
    servers.shutdown()
if __name__ =='__main__':
    from kivy.app import App
    from multiprocessing import Process
    from kivy.base import runTouchApp
    from kivy.lang import Builder
    from kivy.properties import ListProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.image import Image
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.uix.scrollview import ScrollView
    from kivy.core.window import Window 
    from functools import partial
    from kivy.config import Config
    class Server(App):
        is_server_running= False
        def build(self):
            Window.bind(on_request_close=self.close_win)
            self.main = GridLayout(cols =1, rows=3)
            self.servertext = Label(text='Server is not running')
            self.main.add_widget(self.servertext)
            self.ipaddresstext= Label(text='You host name: '+IP)
            self.main.add_widget(self.ipaddresstext)
            self.serverbutton = Button(text='Start Server', background_color='green', on_release=self.serverrun)
            self.main.add_widget(self.serverbutton)
            return self.main
        def close_win(self, *args):
            self.textpopup(title="EXIT", text='Are you sure?')
            return True
        def textpopup(self, title='', text=''):
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=text))
            my_button = Button(text='Ok', size_hint=(1, .25))
            box.add_widget(my_button)
            popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
            my_button.bind(on_release=self.close_all_thanks)
            popup.open()
        def close_all_thanks(self, *args):
            App.get_running_app().stop()
        def serverrun(self, *args, **kwargs):
            if self.is_server_running:
                """We would want to stop running the server"""
                stop_server()
                self.servertext.text='Server is not running'
                self.serverbutton.text='Start Server'
                self.serverbutton.background_color='green'
                self.is_server_running=False
            else:
                start_server()
                self.servertext.text='Server is running'
                self.serverbutton.text='Stop Server'
                self.serverbutton.background_color='red'
                self.is_server_running=True
    Server().run()