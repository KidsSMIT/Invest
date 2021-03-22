from looks.imports import Screen, RelativeLayout, partial, Label, TextInput, Button, User, Popup, requests
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
                print("Sending signal now")
                does_exit = requests.get('http://'+self.hostname.text+':5000/check')
                print(does_exit)
                print('is it alive',does_exit.json()['Alive'])
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
                print('Error with client line 51')
                false = RelativeLayout(size_hint=(.4, 2))
                false.add_widget(Label(text='Host is not running at the moment', font_size=25, size_hint=(.3, .3),
                                        pos_hint={'center_x': .5, 'center_y': .4}))
                close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                false.add_widget(close)
                poped = Popup(title='Server Connect error', content=false, size_hint=(.5, .4))
                poped.open()
                close.bind(on_release=poped.dismiss)