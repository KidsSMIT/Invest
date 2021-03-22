from routes import IP, start_server, stop_server, sqlite3, time, threading
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from functools import partial
from kivy.uix.screenmanager import Screen
class MainScreen(Screen):
    manager = None
    is_server_running = False

    def __init__(self, **args):
        Screen.__init__(self, name='Main')

    def on_pre_enter(self, *args):
        self.add_widget(self.mains())

    def on_leave(self, *args):
        self.remove_widget(self.main)

    def mains(self, *args):
        main = GridLayout(cols=1, rows=4)
        bottom = GridLayout(cols=4, rows=1)
        bottom.add_widget(Button(text='Server', color='green', background_color='black'))
        bottom.add_widget(Button(text='Users', on_release=self.gotous, background_color='black'))
        bottom.add_widget(Button(text='Companies', on_release=self.gotocomp, background_color='black'))
        bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
        main.add_widget(bottom)
        if self.is_server_running:
                self.servertext = Label(text='Server is running')
        else:
            self.servertext = Label(text='Server is not running')
        main.add_widget(self.servertext)
        self.ipaddresstext = Label(text='You host name: ' + IP)
        main.add_widget(self.ipaddresstext)
        if self.is_server_running:
            self.serverbutton = Button(text='Stop Server', background_color='red', on_release=self.serverrun)
        else:
            self.serverbutton = Button(text='Start Server', background_color='green', on_release=self.serverrun)
        main.add_widget(self.serverbutton)
        self.main = main
        return self.main

    def gotous(self, *args):
        self.manager.current = 'Users'

    def gotocomp(self, *args):
        self.manager.current = 'Companies'

    def gotoin(self, *args):
        self.manager.current = 'Investors'

    def serverrun(self, *args, **kwargs):
        if self.is_server_running:
            """We would want to stop running the server"""
            stop_server()
            self.servertext.text = 'Server is not running'
            self.serverbutton.text = 'Start Server'
            self.serverbutton.background_color = 'green'
            self.is_server_running = False
        else:
            start_server()
            self.servertext.text = 'Server is running'
            self.serverbutton.text = 'Stop Server'
            self.serverbutton.background_color = 'red'
            self.is_server_running = True
            threading.Thread(target=self.update_companies_cost_worth_and_gain).start()
            threading.Thread(target=self.update_companies_money).start()
            threading.Thread(target=self.update_users_cost).start()
            threading.Thread(target=self.update_user_money).start()

    def update_companies_cost_worth_and_gain(self, *args):
        print('Updating company cost worth and gain')
        iteration = 0
        while self.is_server_running:
            time.sleep(60)
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = 'select id from companies;'
            cursor.execute(query)
            companies_name = cursor.fetchall()
            for companies in companies_name:
               # Setting Companies Worth 
               query = """select count(*) from investors join companies 
                        where companies.id={} and company_owner_id != investor_id;""".format(
                   companies[0]
               )
               cursor.execute(query)
               num_of_investors = cursor.fetchone()[0]
               query = """
               select (company_gain - ((company_gain *(percent/100)))+ (50* ({}/2))) as worth from investors join companies 
                on company_id= {} where investor_id=company_owner_id;
               """.format(num_of_investors, companies[0])
               cursor.execute(query)
               worth= cursor.fetchone()[0]
               query = """
               update companies set company_worth ={} where id ={};
               """.format(worth, companies[0])
               print(query)
               cursor.execute(query)
               conn.commit()

               # Setting Companies cost
               decrease = worth * (1**iteration)
               query = """
                    update companies set company_cost={} where id={};
               """.format(decrease, companies[0])
               print(query)
               conn = sqlite3.connect('server.db')
               cursor = conn.cursor()
               cursor.execute(query)
               conn.commit()
               # Setting Companies gains
               gain = worth * ((1+1)**iteration)
               query = """update companies set company_gain={} where id={};""".format(gain, companies[0])
               conn = sqlite3.connect('server.db')
               cursor = conn.cursor()
               print(query)
               cursor.execute(query)
               conn.commit()
               conn.close()
            iteration +=1
        print('Quitting update_companies_cost_worth_and_gain')

    def update_companies_money(self, *args):
        print("Updating company money")
        while self.is_server_running:
            time.sleep(60)
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = 'select id from companies;'
            cursor.execute(query)
            companies_name = cursor.fetchall()
            for companies in companies_name:
                query = """
                    select percent from investors join companies on company_id= companies.id where 
                    companies.id = {} and investor_id = company_owner_id;
                """.format(companies[0])
                cursor.execute(query)
                percent_owned = cursor.fetchone()[0]
                query = """
                    update companies set company_money = company_money + (company_gain * {}) where id = {};
                """.format(percent_owned, companies[0])
                print(query)
                cursor.execute(query)
                conn.commit()
        print('Quitting update_companies_money')

    def update_users_cost(self, *args):
        print('Updating users cost')
        while self.is_server_running:
            time.sleep(60)
            query = 'select id from users;'
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            users = cursor.fetchall()
            for user in users:
                query = """select intial_payed, company_worth, percent from investors join companies on
                            company_id = companies.id where investor_id={};""".format(user[0])
                print(query)
                cursor.execute(query)
                investment = cursor.fetchall()
                print(investment)
                cost = 0
                for invest in investment:
                    try:
                        initial_amount_payed = invest[0]
                        comp_worth = invest[1]
                        percent_of_comp_owned_by_user = invest[2]
                        amou = ((initial_amount_payed/comp_worth)/percent_of_comp_owned_by_user)/100
                        amou= initial_amount_payed * amou
                        cost += amou
                    except ZeroDivisionError:
                        cost +=0
                query = """update users set user_cost={} where id={};""".format(cost, user[0])
                print(query)
                conn = sqlite3.connect('server.db')
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        print('Quitting update_users_cost')

    def update_user_money(self, *args):
        print('Updating user money')
        while self.is_server_running:
            time.sleep(60)
            query = 'select id from users;'
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            users = cursor.fetchall()
            for user in users:
                query = """select company_gain, percent from investors join companies on
                            company_id = companies.id where investor_id={};""".format(user[0])
                cursor.execute(query)
                investment = cursor.fetchall()
                money = 0
                for invest in investment:
                    money += invest[0] * invest[1]
                query = """select user_cost from users where id={}""".format(user[0])
                cursor.execute(query)
                cost = cursor.fetchone()
                print('cost',cost)
                money -= cost[0]      
                print('money', money)
                query = """select user_money from users where id={}""".format(user[0])
                print(query)
                cursor.execute(query)
                user_actual = cursor.fetchone()[0]
                print('mon', user_actual)
                user_actual += money 
                query = """update users set user_money={} where id={};""".format(user_actual, user[0])
                print(query)
                cursor.execute(query)
                conn.commit()
        print('Quitting update_user_money')


class Users(Screen):
        manager = None

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
                users = False
            conn.close()
            if users:
                # Remember users come in like [(id, name, password, user_money, user_gain, user_cost)]
                box = GridLayout(cols=1, rows=len(users), spacing=10, size_hint_y=len(users) / 2)
                root = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
                for user in users:
                    b = Label(text='Name: ' + user[1] + '\nUsers money: ' + str(user[3]) + '\nUser gain: ' + str(
                        user[4]) + '\nUsers cost: ' + str(user[5]),
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
                self.main.add_widget(
                    Label(text='Either you have no users or there was a problem getting user from database'))
                return self.main

        def gotous(self, *args):
            self.manager.current = 'Main'

        def gotocomp(self, *args):
            self.manager.current = 'Companies'

        def gotoin(self, *args):
            self.manager.current = 'Investors'


class Companies(Screen):
        manager = None

        def __init__(self, **args):
            Screen.__init__(self, name='Companies')

        def on_pre_enter(self, *args):
            self.add_widget(self.company())

        def on_leave(self, *args):
            self.remove_widget(self.main)

        def company(self, *args):
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = 'select * from companies join users on companies.company_owner_id = users.id;'
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
                # Remember company comes in like this [(id, company_name, company_owner_id, company_cost,
                # company_gain, date_company_created, company_money, user_id, name, password, money, gain, cost)]
                box = GridLayout(cols=1, rows=len(company), spacing=10, size_hint_y=len(company) / 2)
                root = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
                for companies in company:
                    b = Button(text='Company name: ' + companies[1] + '\nCost of company: ' + str(companies[3]) +
                                    '\nCompany gains: ' + str(companies[4]) + '\nDate company was created: ' + str(
                        companies[5]) + '\nCompany money: ' + str(companies[6])
                                    + '\nWho Created company' + str(companies[8]), font_size=20,
                               background_color='blue',
                               on_release=partial(self.company_detail, companies[7], companies[8]))
                    box.add_widget(b)
                root.add_widget(box)
                self.main = GridLayout(cols=1, rows=2)
                bottom = GridLayout(cols=4, rows=1)
                bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
                bottom.add_widget(Button(text='Users', on_release=self.gotous, background_color='black'))
                bottom.add_widget(Button(text='Companies', color='green', background_color='black'))
                bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
                self.main.add_widget(bottom)
                self.main.add_widget(root)
                return self.main
            else:
                self.main = GridLayout(cols=1, rows=2)
                bottom = GridLayout(cols=4, rows=1)
                bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
                bottom.add_widget(Button(text='Users', on_release=self.gotous, background_color='black'))
                bottom.add_widget(Button(text='Companies', color='green', background_color='black'))
                bottom.add_widget(Button(text='Investors', on_release=self.gotoin, background_color='black'))
                self.main.add_widget(bottom)
                self.main.add_widget(
                    Label(text='Either you have no companies or there was a problem getting user from database'))
                return self.main

        def gotos(self, *args):
            self.manager.current = 'Main'

        def gotous(self, *args):
            self.manager.current = 'Users'

        def gotoin(self, *args):
            self.manager.current = 'Investors'

        def company_detail(self, id, name, *args):
            user_detail = GridLayout(cols=1, rows=6)
            query = 'select name, user_money, user_gain, user_cost from users where id ={};'.format(id)
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            user_infor = cursor.fetchone()
            user_detail.add_widget(Label(text='User Information'))
            for user in zip(user_infor, ['name', 'money', 'gains', 'cost']):
                print(type(user[0]), user[0])
                if type(user[0]) == str:
                    user_detail.add_widget(Label(text=user[1].capitalize() + ': ' + user[0]))
                else:
                    user_detail.add_widget(Label(text=user[1].capitalize() + ': ' + str(user[0])))
            query = "select company_name from companies join users on companies.company_owner_id = users.id where name='{}';".format(
                name)
            cursor.execute(query)
            investments = cursor.fetchall()
            user_investment = GridLayout(cols=1, rows=len(investments) + 1, spacing=10,
                                         size_hint_y=len(investments) / 2)
            root = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
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
            pop = Popup(title=name + ' details', content=mains)
            pop.open()
            close_b.bind(on_release=pop.dismiss)


class Investors(Screen):
        manager = None

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
            main = GridLayout(cols=1, rows=len(investors) + 1, spacing=10, size_hint_y=len(investors) / 2)
            # Remember investors will look like this [(company_Name, name, percent, date_company_created)]
            for i in range(len(investors)):
                men = GridLayout(cols=1, rows=4)
                for inv in zip(['Companies Name', 'Name of investor', 'Percent of company investor owns',
                                'Date company was created'], investors[i]):
                    if inv[1] == str:
                        men.add_widget(Label(text=inv[0] + ': ' + inv[1]))
                    else:
                        men.add_widget(Label(text=inv[0] + ': ' + str(inv[1])))
                main.add_widget(men)
            root = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
            root.add_widget(main)
            mains = GridLayout(cols=1, rows=3)
            bottom = GridLayout(cols=4, rows=1)
            bottom.add_widget(Button(text='Server', on_release=self.gotos, background_color='black'))
            bottom.add_widget(Button(text='Users', on_release=self.gotous, background_color='black'))
            bottom.add_widget(Button(text='Companies', on_release=self.gotocom, background_color='black'))
            bottom.add_widget(Button(text='Investors', color='green', background_color='black'))
            mains.add_widget(bottom)
            mains.add_widget(root)
            self.main = mains
            return self.main

        def gotos(self, *args):
            self.manager.current = 'Main'

        def gotous(self, *args):
            self.manager.current = 'Users'

        def gotocom(self, *args):
            self.manager.current = 'Companies'
