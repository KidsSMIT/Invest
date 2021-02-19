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
        try:
            cursor.execute('select id from users where name="{}"')
            exist = cursor.fetchone()
        except Exception as e:
            exist=False
        if exist==None or exist==False:
            cursor.execute('INSERT INTO users VALUES (NULL,?,?,?,?,?)', (data['name'], data['password'],1000, 0, 0))
            conn.commit()
            re = {'Success': True}
            return jsonify(re)
        else:
            print(exist)
            re ={'Success':False}
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
@app.route('/get/user/num/company', methods=['POST'])
def get_user_comp():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query="""select count(*) from companies join users on companies.company_owner_id = users.id where users.name='{}';""".format(data['username'])
    cursor.execute(query)
    grab = cursor.fetchone()
    re = {'number': grab[0]}
    print(re)
    conn.close()
    return jsonify(re)
@app.route('/get/user/num/investor', methods=['POST'])
def get_user_inves():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select count(*) from investors join users on investors.investor_id=users.id where users.name='{}';""".format(data['username'])
    cursor.execute(query)
    num = cursor.fetchone()
    re = {'number': num[0]}
    print(re)
    conn.close()
    return jsonify(re)
@app.route('/get/user/investor', methods=['POST'])
def get_user_investment():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select company_name from investors join users on investors.investor_id=users.id join companies on 
            investors.company_id = companies.id where name='{}';""".format(data['username'])
    cursor.execute(query)
    names = cursor.fetchall()
    re = {'companies_names': names}
    print(re)
    conn.close()
    return jsonify(re)
@app.route('/get/user/own_comp', methods=["POST"])
def user_owned_comp():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor=conn.cursor()
    query = """select name from companies join users on companies.company_owner_id=users.id where name='{}';""".format(data['username'])
    cursor.execute(query)
    comp_names = cursor.fetchall()
    conn.close()
    re = {'Companies name': comp_names}
    return jsonify(re)
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
    class MainScreen(Screen):
        manager =None
        is_server_running= False
        def __init__(self, **args):
            Screen.__init__(self, name='Main')
        def on_pre_enter(self, *args):
            self.add_widget(self.mains())
        def on_leave(self, *args):
            self.remove_widget(self.main)
        def mains(self, *args):
            main = GridLayout(cols =1, rows=4)
            bottom = GridLayout(cols=4, rows=1)
            bottom.add_widget(Button(text='Server', color='green', background_color='black'))
            bottom.add_widget(Button(text='Users', on_release=self.gotous, background_color='black'))
            bottom.add_widget(Button(text='Companies', on_release=self.gotocomp, background_color='black'))
            bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
            main.add_widget(bottom)
            if self.is_server_running:
                self.servertext=Label(text='Server is running')
            else:
                self.servertext = Label(text='Server is not running')
            main.add_widget(self.servertext)
            self.ipaddresstext= Label(text='You host name: '+IP)
            main.add_widget(self.ipaddresstext)
            if self.is_server_running:
                self.serverbutton = Button(text='Stop Server', background_color='red', on_release=self.serverrun)
            else:
                self.serverbutton = Button(text='Start Server', background_color='green', on_release=self.serverrun)
            main.add_widget(self.serverbutton)
            self.main = main
            return self.main
        def gotous(self, *args):
            self.manager.current ='Users'
        def gotocomp(self, *args):
            self.manager.current ='Companies'
        def gotoin(self, *args):
            self.manager.current='Investors'
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
                threading.Thread(target=self.update_companies_cost_worth_and_gain).start()
                threading.Thread(target=self.update_companies_money).start()
                threading.Thread(target=self.update_users_cost).start()
                threading.Thread(target=self.update_user_money).start()
        def update_companies_cost_worth_and_gain(self, *args):
            while self.is_server_running:
                conn = sqlite3.connect('server.db')
                cursor = conn.cursor()
                query = 'select company_name from companies;'
                cursor.execute(query)
                companies_name = cursor.fetchall()
                for companies in companies_name:
                    query = """select count(*) from investors 
                                join companies on investors.company_id = companies.id
                                join users on investors.investor_id=users.id where company_name='{}';""".format(companies[0])
                    cursor.execute(query)
                    x = cursor.fetchone()
                    cost = 50 * x[0] + 70 * x[0] 
                    query = """update companies set company_cost={} where company_name='{}';""".format(cost, companies[0])
                    conn = sqlite3.connect('server.db')
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    conn.close()
                    conn = sqlite3.connect('server.db')
                    cursor = conn.cursor()
                    query = """select company_money from companies where company_name='{}';""".format(companies[0])
                    cursor.execute(query)
                    money = cursor.fetchone()
                    worth = money[0]-cost
                    query = """update companies set company_worth = {} where company_name='{}';""".format(worth, companies[0])
                    top = (worth)
                    query = """select percent from investors 
                                join companies on investors.company_id = companies.id
                                join users on investors.investor_id=users.id where company_name='{}' and investor_id == company_owner_id;""".format(companies[0])
                    cursor.execute(query)
                    percent = cursor.fetchone()[0] / 100
                    bottom = percent * worth
                    try:
                        gain = top / bottom
                    except ZeroDivisionError:
                        gain = 0
                    query = """update companies set company_gain={} where company_name='{}';""".format(gain, companies[0])
                    cursor.execute(query)
                    conn.commit()
                conn.close()
            print('Quitting update_companies_cost_worth_and_gain')
        def update_companies_money(self, *args):
            while self.is_server_running:
                time.sleep(60)
                conn = sqlite3.connect('server.db')
                cursor = conn.cursor()
                query = 'select company_name from companies;'
                cursor.execute(query)
                companies_name = cursor.fetchall()
                for companies in companies_name:
                    query = """select company_gain from companies where company_name='{}';""".format(companies[0])
                    cursor.execute(query)
                    gain = cursor.fetchone()
                    query = """select company_money from companies where company_name='{}';""".format(companies[0])
                    conn = sqlite3.connect('server.db')
                    cursor = conn.cursor()
                    cursor.execute(query)
                    money=cursor.fetchone()
                    query ="""select company_cost from companies where company_name='{}';""".format(companies[0])
                    cursor.execute(query)
                    cost = cursor.fetchone()
                    print('money', money[0], 'gain', gain[0]/1440, 'cost', cost[0]/1440, 'total', money[0] + ((gain[0]/1440)-(cost[0]/1440)))
                    query ="""update companies set company_money={} where company_name='{}';""".format(money[0] + ((gain[0]/1440)-(cost[0]/1440)), companies[0])
                    cursor.execute(query)
                    conn.commit()
                conn.close()
            print('Quitting update_companies_money')
        def update_users_cost(self, *args):
            while self.is_server_running:
                query ='select name from users;'
                conn = sqlite3.connect('server.db')
                cursor = conn.cursor()
                cursor.execute(query)
                users = cursor.fetchall()
                for user in users:
                    query="""select company_worth, percent from investors
                        join companies on investors.company_id = companies.id
                        join users on investors.investor_id = users.id where name='{}';""".format(user[0])
                    cursor.execute(query)
                    cost = 0 
                    needed_infor = cursor.fetchall()
                    for infor in needed_infor:
                        cost += infor[0] * (infor[1]/100)
                    query = """update users set user_cost={} where name='{}'""".format(cost, user[0])
                    cursor.execute(query)
                    conn.commit()
                    conn = sqlite3.connect('server.db')
                    cursor = conn.cursor()
                    query = """select company_gain, percent from investors 
                                join companies on investors.company_id = companies.id
                                join users on investors.investor_id = users.id where name='{}'""".format(user[0])
                    cursor.execute(query)
                    gains_infor = cursor.fetchall()
                    gain = 0
                    for gains in gains_infor:
                        gain += gains[0] *(gains[1]/100)
                    query = """update users set user_gain={} where name='{}'""".format(gain, user[0])
                    cursor.execute(query)
                    conn.commit()
                conn.close()
            print('Quitting update_users_cost')
        def update_user_money(self, *args):
            while self.is_server_running:
                time.sleep(60)
                query ='select name from users;'
                conn = sqlite3.connect('server.db')
                cursor = conn.cursor()
                cursor.execute(query)
                users = cursor.fetchall()
                for user in users:
                    query = """select user_gain, user_cost, user_money from users where name='{}'""".format(user[0])
                    cursor.execute(query)
                    use_data = cursor.fetchone()
                    gain = (use_data[0]/1440) - (use_data[1]/1440)
                    print('gain', gain, 'money before gain', use_data[2], 'money after gain', use_data[2] + gain)
                    money = use_data[2] + gain
                    query = """update users set user_money={} where name='{}'""".format(money, user[0])
                    cursor.execute(query)
                    conn.commit()
                conn.close()
            print('Quitting update_user_money')
    class Users(Screen):
        manager= None
        def __init__(self, **args):
            Screen.__init__(self, name='Users')
        def on_pre_enter(self, *args):
            self.add_widget(self.users())
        def on_leave(self, *args):
            self.remove_widget(self.main)
        def users(self, *args):
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = 'select * from users;'
            try:
                print(query)
                cursor.execute(query)
                users = cursor.fetchall()
                print(users)
            except Exception as e:
                print(e)
                print('Problem at server on line 166')
                users=False
            conn.close()
            if users:
                # Remember users come in like [(id, name, password, user_money, user_gain, user_cost)]
                box = GridLayout(cols=1, rows=len(users), spacing=10, size_hint_y=len(users)/2)
                root=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
                for user in users:
                    b = Label(text='Name: '+user[1]+'\nUsers money: '+str(user[3]) + '\nUser gain: '+str(user[4]) +'\nUsers cost: '+str(user[5]),
                    font_size=20)
                    box.add_widget(b)
                root.add_widget(box)
                self.main = GridLayout(cols=1, rows=2)
                bottom = GridLayout(cols=4, rows=1)
                bottom.add_widget(Button(text='Server', on_release=self.gotous, background_color='black'))
                bottom.add_widget(Button(text='Users', color='green', background_color='black'))
                bottom.add_widget(Button(text='Companies', on_release=self.gotocomp, background_color='black'))
                bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
                self.main.add_widget(bottom)
                self.main.add_widget(root)
                return self.main
            else:
                self.main = GridLayout(cols=1, rows=1)
                self.main.add_widget(Label(text='Either you have no users or there was a problem getting user from database'))
                return self.main
        def gotous(self, *args):
            self.manager.current ='Main'
        def gotocomp(self, *args):
            self.manager.current ='Companies'
        def gotoin(self, *args):
            self.manager.current='Investors'
    class Companies(Screen):
        manager= None
        def __init__(self, **args):
            Screen.__init__(self, name='Companies')
        def on_pre_enter(self, *args):
            self.add_widget(self.company())
        def on_leave(self, *args):
            self.remove_widget(self.main)
        def company(self, *args):
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query ='select * from companies join users on companies.company_owner_id = users.id;'
            try:
                print(query)
                cursor.execute(query)
                company = cursor.fetchall()
                print(company)
            except Exception as e:
                print(e)
                print('There was a problem with server at line 221')
                company = False
            conn.close()
            if company:
                # Remember company comes in like this [(id, company_name, company_owner_id, company_cost, company_gain, date_company_created, 
                # company_money, user_id, name, password, money, gain, cost)]
                box = GridLayout(cols=1, rows=len(company), spacing=10, size_hint_y=len(company)/2)
                root=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
                for companies in company:
                    b = Button(text='Company name: '+ companies[1] + '\nCost of company: '+ str(companies[3])+
                    '\nCompany gains: '+str(companies[4]) +'\nDate company was created: '+ str(companies[5])+ '\nCompany money: '+ str(companies[6])
                    +'\nWho Created company'+str(companies[8]), font_size=20, background_color='blue', 
                    on_release=partial(self.company_detail, companies[7], companies[8]))
                    box.add_widget(b)
                root.add_widget(box)
                self.main= GridLayout(cols=1, rows=2)
                bottom = GridLayout(cols=4, rows=1)
                bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
                bottom.add_widget(Button(text='Users',on_release=self.gotous, background_color='black'))
                bottom.add_widget(Button(text='Companies', color='green', background_color='black'))
                bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
                self.main.add_widget(bottom)
                self.main.add_widget(root)
                return self.main
            else:
                self.main = GridLayout(cols=1, rows=2)
                bottom = GridLayout(cols=4, rows=1)
                bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
                bottom.add_widget(Button(text='Users',on_release=self.gotous, background_color='black'))
                bottom.add_widget(Button(text='Companies', color='green', background_color='black'))
                bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
                self.main.add_widget(bottom)
                self.main.add_widget(Label(text='Either you have no companies or there was a problem getting user from database'))
                return self.main
        def gotos(self, *args):
            self.manager.current='Main'
        def gotous(self, *args):
            self.manager.current='Users'
        def gotoin(self, *args):
            self.manager.current='Investors'
        def company_detail(self, id, name, *args):
            user_detail = GridLayout(cols=1, rows=6)
            query ='select name, user_money, user_gain, user_cost from users where id ={};'.format(id)
            conn = sqlite3.connect('server.db')
            cursor=conn.cursor()
            cursor.execute(query)
            user_infor = cursor.fetchone()
            user_detail.add_widget(Label(text='User Information'))
            for user in zip(user_infor, ['name', 'money', 'gains', 'cost']):
                print(type(user[0]), user[0])
                if type(user[0]) == str:
                    user_detail.add_widget(Label(text=user[1].capitalize() + ': '+user[0]))
                else:
                    user_detail.add_widget(Label(text=user[1].capitalize() + ': '+str(user[0])))
            query = "select company_name from companies join users on companies.company_owner_id = users.id where name='{}';".format(name)
            cursor.execute(query)
            investments = cursor.fetchall()
            user_investment=GridLayout(cols=1, rows=len(investments)+1, spacing=10, size_hint_y=len(investments)/2)
            root=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
            user_investment.add_widget(Label(text='Companies users have invested in:'))
            conn.close()
            for i in investments:
                print(i)
                user_investment.add_widget(Label(text=i[0]))
            root.add_widget(user_investment)
            mains = GridLayout(cols=3, rows=1)
            mains.add_widget(user_detail)
            mains.add_widget(root)
            close_b = Button(text='Close')
            mains.add_widget(close_b)
            pop = Popup(title=name+' details', content=mains)
            pop.open()
            close_b.bind(on_release=pop.dismiss)
    class Investors(Screen):
        manager= None
        def __init__(self, **args):
            Screen.__init__(self, name='Investors')
        def on_pre_enter(self, *args):
            self.add_widget(self.invent())
        def on_leave(self, *args):
            self.remove_widget(self.main)
        def invent(self, *args):
            query = """select company_name,  name, percent, date_company_created from investors
                        join companies on investors.company_id = companies.id
                        join users on investors.investor_id = users.id;"""
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            investors = cursor.fetchall()
            conn.close()
            main = GridLayout(cols=1, rows=len(investors)+1, spacing=10, size_hint_y=len(investors)/2)
            # Remember investors will look like this [(company_Name, name, percent, date_company_created)]
            for i in range(len(investors)):
                men = GridLayout(cols=1, rows=4)
                for inv in zip(['Companies Name', 'Name of investor', 'Percent of company investor owns', 'Date company was created'], investors[i]):
                    if inv[1] == str:
                        men.add_widget(Label(text= inv[0]+': '+inv[1]))
                    else:
                        men.add_widget(Label(text=inv[0]+': '+str(inv[1])))
                main.add_widget(men)
            root=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
            root.add_widget(main)
            mains = GridLayout(cols=1, rows=3)
            bottom = GridLayout(cols=4, rows=1)
            bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
            bottom.add_widget(Button(text='Users',on_release=self.gotous, background_color='black'))
            bottom.add_widget(Button(text='Companies', on_release=self.gotocom, background_color='black'))
            bottom.add_widget(Button(text='Investors', color='green', background_color='black'))
            mains.add_widget(bottom)
            mains.add_widget(root)
            self.main = mains 
            return self.main
        def gotos(self, *args):
            self.manager.current = 'Main'
        def gotous(self, *args):
            self.manager.current='Users'
        def gotocom(self, *args):
            self.manager.current='Companies'
    class Server(App):
        def build(self):
            Window.bind(on_request_close=self.close_win)
            sm = ScreenManager()
            sm.tittle='InvestIt Server'
            sm.add_widget(MainScreen())
            sm.add_widget(Users())
            sm.add_widget(Companies())
            sm.add_widget(Investors())
            MainScreen.manager = sm
            Users.manager=sm 
            Companies.manager= sm
            Investors.manager=sm
            return sm
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
        
    Server().run()