from looks.imports import Screen, RelativeLayout, Label,TextInput,Button,requests, User,Popup, partial
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
            User.update_all(id=data[0], name=data[1], password=data[2], money=data[3], 
            gain=data[4], cost=data[5])
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
        user = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.4,.1), pos_hint={'center_x': .65, 'center_y': .4}
        )
        false.add_widget(user)
        false.add_widget(Label(text='Password:', font_size=20, size_hint=(.3,.3), pos_hint={'center_x': .25, 'center_y':.3}))
        password = TextInput(
            multiline=False, readonly=False, halign='right', font_size=20, size_hint=(.4,.1), pos_hint={'center_x': .65, 'center_y': .3}, password=True
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
                falsed.add_widget(Label(text='Problem creating new user, user already created', font_size=20, size_hint=(.3, .3),
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