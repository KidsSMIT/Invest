from kivy.app import App
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
import requests
class User:
    IP = None
class GetIP(Screen):
    manager = None
    def __init__(self, **args):
        Screen.__init__(self, name='GetIP')
    def on_pre_enter(self,  *args):
        self.add_widget(self.getip())
    def on_leave(self,  *args):
        self.remove_widget(self.main)
    def getip(self, *args):
        main = RelativeLayout(size=(300, 300))
        main.add_widget(Label(text='Login to an IP to get Investing and Trading', font_size=25,
                            size_hint=(.3, .3), pos_hint={'center_x': .5, 'center_y': .9}))
        main.add_widget(Label(text='Hostname:', size_hint=(.3, .3), font_size=25, pos_hint={'center_x': .3, 'center_y': .6}))
        self.hostname = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3, .1), pos_hint={'center_x': .55, 'center_y': .6}
        )
        main.add_widget(self.hostname)
        main.add_widget(Button(
            text='Login', size_hint=(.2,.1), pos_hint={'center_x': .6, 'center_y':.4}, on_release=partial(self.check)
        ))
        self.main = main
        return self.main
    def check(self,  *args):
        if self.hostname.text == '':
            false = RelativeLayout(size_hint=(.3, .2))
            false.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3,.3), pos_hint={'center_x': .5, 'center_x':.4}))
            close = Button(text='Close', size_hint=(.2,.1), pos_hint={'center_x': .5, 'center_y':.1})
            false.add_widget(close)
            pop = Popup(title='Please fill out form', content=false, size_hint=(.4,.4))
            pop.open()
            close.bind(on_release=pop.dismiss)
        else:
            try:
                does_exit = requests.get('http://'+self.hostname.text+':5000/check')
                print(does_exit.json()['Alive'])
                if does_exit.json()['Alive']:
                    User.IP = self.hostname.text
                    self.manager.current='Login'
                else:
                    false = RelativeLayout(size_hint=(.4, 2))
                    false.add_widget(Label(text='Incorrect Host name, Host might not be running', font_size=25, size_hint=(.3, .3),
                                        pos_hint={'center_x': .5, 'center_y': .4}))
                    close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                    false.add_widget(close)
                    poped = Popup(title='Server Connect error', content=false, size_hint=(.5, .4))
                    poped.open()
                    close.bind(on_release=poped.dismiss)
            except Exception as e:
                print(e)
                false = RelativeLayout(size_hint=(.4, 2))
                false.add_widget(Label(text='Host is not running at the moment', font_size=25, size_hint=(.3, .3),
                                        pos_hint={'center_x': .5, 'center_y': .4}))
                close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                false.add_widget(close)
                poped = Popup(title='Server Connect error', content=false, size_hint=(.5, .4))
                poped.open()
                close.bind(on_release=poped.dismiss)
class Login(Screen):
    manager = None
    def __init__(self, **args):
        Screen.__init__(self, name='Login')
    def on_pre_enter(self,  *args):
        self.add_widget(self.login())
    def on_leave(self,  *args):
        self.remove_widget(self.main)
    def login(self,  *args):
        main = RelativeLayout(size=(300, 300))
        main.add_widget(Label(text='Login to get Investing and Trading', font_size=25,
                            size_hint=(.3, .3), pos_hint={'center_x': .5, 'center_y': .9}))
        main.add_widget(Label(text='Username:', size_hint=(.3, .3), font_size=25, pos_hint={'center_x': .3, 'center_y': .6}))
        main.add_widget(Label(text='Password:', size_hint=(.3,.3), font_size=25, pos_hint={'center_x': .3, 'center_y': .5}))
        self.username = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3, .1), pos_hint={'center_x': .55, 'center_y': .6}
        )
        self.password = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3,.1), pos_hint={'center_x': .55, 'center_y': .5}, password=True
        )
        main.add_widget(self.username)
        main.add_widget(self.password)
        main.add_widget(Button(
            text='Login', size_hint=(.1,.1), pos_hint={'center_x': .65, 'center_y':.4}, on_release=partial(self.check)
        ))
        main.add_widget(Button(text='Create a new account', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .4},
        on_release=self.new_user))
        self.main = main
        return self.main
    def check(self,  *args):
        exact_user = requests.post(url='http://'+User.IP+':5000/exact_user', json={'username': self.username.text, 'password': self.password.text})
        if exact_user.json()['is_it_correct'] == True:
            data = exact_user.json()['data']
            print(data)
            User.update_all(id=data[0], name=data[1], password=data[2], worth=data[3], 
            cost=data[4], daily_gain=data[5], money=data[6], investment=data[7])
            self.manager.current = 'Profile'
        else:
            false = RelativeLayout(size_hint=(.4, 2))
            false.add_widget(Label(text='Incorrect Name or Password', font_size=25, size_hint=(.3, .3),
                                    pos_hint={'center_x': .5, 'center_y': .4}))
            close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
            false.add_widget(close)
            poped = Popup(title='False Login', content=false, size_hint=(.5, .4))
            poped.open()
            close.bind(on_release=poped.dismiss)
    def new_user(self,  *args):
        false = RelativeLayout(size_hint=(.4, 2))
        false.add_widget(Label(text='Username:', font_size=25, size_hint=(.3, .3),
                                    pos_hint={'center_x': .25, 'center_y': .4}))
        user = TextInput(text='username',
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.4,.1), pos_hint={'center_x': .65, 'center_y': .4}
        )
        false.add_widget(user)
        false.add_widget(Label(text='Password:', font_size=25, size_hint=(.3,.3), pos_hint={'center_x': .25, 'center_y':.3}))
        password = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.4,.1), pos_hint={'center_x': .65, 'center_y': .3}, password=True
        )
        false.add_widget(password)
        def logs(*args):
            new_user = requests.post(url='http://'+User.IP+':5000/new_user', json={'name': user.text, 'password':password.text})
            if new_user.json()['Success'] == True:
                    falsed = RelativeLayout(size_hint=(.4, 2))
                    falsed.add_widget(Label(text='New User created, login in with that user', font_size=20, size_hint=(.3, .3),
                                            pos_hint={'center_x': .5, 'center_y': .4}))
                    close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                    falsed.add_widget(close)
                    poped = Popup(title='New User created', content=falsed, size_hint=(.5, .4))
                    poped.open()
                    close.bind(on_release=poped.dismiss)
            else:
                falsed = RelativeLayout(size_hint=(.4, 2))
                falsed.add_widget(Label(text='Problem creating new user please try again', font_size=20, size_hint=(.3, .3),
                                            pos_hint={'center_x': .5, 'center_y': .4}))
                close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                falsed.add_widget(close)
                poped = Popup(title='New User created', content=falsed, size_hint=(.5, .4))
                poped.open()
                close.bind(on_release=poped.dismiss)
        close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .3, 'center_y': .2})
        false.add_widget(close)
        false.add_widget(Button(text='Create User', size_hint=(.3, .1), pos_hint={'center_x': .6, 'center_y':.2}, on_release=logs))
        poped = Popup(title='Create new user', content=false, size_hint=(.5, .4))
        poped.open()
        close.bind(on_release=poped.dismiss)
        

sm = ScreenManager()
sm.title='InvestIt'
users = User()
sm.add_widget(GetIP())
sm.add_widget(Login())
Login.manager = sm
GetIP.manager = sm 
class TradeIt(App):
    def build(self):
        Window.bind(on_request_close=self.close_win)
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
        User.active = False
        App.get_running_app().stop()


if __name__ =='__main__':
    TradeIt().run()