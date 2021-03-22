from looks.imports import Screen,BoxLayout, GridLayout, RelativeLayout, partial, Label, TextInput, Button, User, Popup, requests
class MakeCompany(Screen):
    manager = None 
    def __init__(self):
        Screen.__init__(self, name='Make_Comp')
    def on_pre_enter(self, *args):
        self.add_widget(self.makecomp())
    def on_leave(self, *args):
        self.remove_widget(self.main)
    def makecomp(self, *args):
        main = RelativeLayout(size=(300, 300))
        top = GridLayout(cols=5, rows=1, pos_hint={'center_x':.5, 'center_y':.9})
        top.add_widget(Button(text='Back to profile', background_color='black', on_release=self.gotopro))
        top.add_widget(Button(text='Companies', background_color ='black',on_release=self.gotocomp ))
        top.add_widget(Button(text='Users rank', background_color ='black', on_release=self.gotousr))
        top.add_widget(Button(text='Make a company', background_color='black', color='green'))
        top.add_widget(Button(text='Chat', on_release=self.gotochats, background_color='black'))
        main.add_widget(top)
        main.add_widget(Label(text='Name of Company', pos_hint={'center_x': .5, 'center_y':.7}))
        self.Name_of_comp=TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3, .1), 
            pos_hint={'center_x': .5, 'center_y':.6}
            )
        main.add_widget(self.Name_of_comp)
        main.add_widget(Label(text='How much will you like to put in the company to start off', font_size=16,
        pos_hint={'center_x': .53, 'center_y': .5}))
        self.Money_of_comp = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3, .1), 
            pos_hint={'center_x': .5,'center_y':.4}
            )
        main.add_widget(self.Money_of_comp)
        main.add_widget(Label(text='Minimum value is 1000',
        pos_hint={'center_x':.5, 'center_y':.3}, color='red'))
        main.add_widget(Button(text="Create", size_hint=(.2,.1),
        background_color='green', pos_hint={'center_x': .5, 'center_y':.2},
        on_release=self.create))
        self.main = main
        return self.main
    def gotousr(self,  *args):
        self.manager.current='Users'
    def gotocomp(self, *args):
        self.manager.current='Invest'
    def gotopro(self, *args):
        self.manager.current = 'Profile'
    def gotochats(self, *args):
        self.manager.current='Chats'
    def creationerror(self,title, text, *args):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        my_button = Button(text='Ok', size_hint=(1,.25))
        box.add_widget(my_button)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        my_button.bind(on_release=popup.dismiss)
        popup.open()
    def create(self, *args):
        print('User clicked me')
        if self.Name_of_comp.text != '':
            print("User has text")
            if self.Money_of_comp.text != '':
                print("User money has text")
                if self.Money_of_comp.text.isdecimal():
                    print("User used only numbers")
                    amount = int(self.Money_of_comp.text)
                    print('User amount',amount)
                    print(User.money)
                    if amount >= 1000:
                        if User.money >= amount:
                            print("User has more than enough money")
                            creation = requests.post(url='http://'+User.IP+':5000/createusercomp', json={'comp_name':self.Name_of_comp.text, 'owner_id':User.id,
                            'amount': amount})
                            print(creation)
                            if creation.ok and creation.json()['Success'] == True:
                                self.creationerror(title='Success', text="Your company was successfully created")
                            else:
                                self.creationerror(title='Unsuccess', text="We were unable to create your company please check your local server for issues")
                        else:
                            self.creationerror(title='Not enough', text="Sorry you do not have enough money to start a buisness")
                    else:
                        self.creationerror(title='Not enough', text="You need to put at least 1000 money in other to start a buisness")
                else:
                    self.creationerror(title='Incorrect input', text="Please type only numbers in")
            else:
                print("User money has no text")
                self.creationerror(title='Fill out form', text="Please type in how much you want to put in the company")
        else:
            self.creationerror(title='Fill out form', text="Please type in the name of the company you would like to create.")