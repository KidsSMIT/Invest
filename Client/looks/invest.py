from looks.imports import Screen, BoxLayout,AnchorLayout, partial, requests,GridLayout, Button, User,ScrollView, Window, Graph, MeshLinePlot, Popup, TextInput, RelativeLayout, Label
class Invest(Screen):
    manager= None
    def __init__(self, **args):
        Screen.__init__(self, name='Invest')
    def on_pre_enter(self, *args):
        self.add_widget(self.invest())
    def on_leave(self,  *args):
        self.remove_widget(self.main)
    def invest(self, *args):
        main = GridLayout(cols=1, rows=2)
        top = GridLayout(cols=5, rows=1)
        top.add_widget(Button(text='Back to profile', background_color='black', on_release=self.gotopro))
        top.add_widget(Button(text='Companies', background_color ='black', color='green'))
        top.add_widget(Button(text='Users rank', background_color ='black', on_release=self.gotousr))
        top.add_widget(Button(text='Make a company', background_color='black', on_release=self.gotomakecomp))
        top.add_widget(Button(text='Chat', on_release=self.gotochats, background_color='black'))
        main.add_widget(top)
        comps= requests.get(url='http://'+User.IP+':5000/get/all_comp')
        companies = GridLayout(cols=1, rows=len(comps.json()['Companies']), spacing=10, size_hint_y=len(comps.json()['Companies']))
        for comp in comps.json()['Companies']:
            founder= comp[9] if comp[9] != User.name else 'You'
            print(comp)
            companies.add_widget(Button(text='Company Name: '+comp[1]+'\nCompany Cost daily: '+ str(comp[3])
                                + '\nCompany Gain daily: '+ str(comp[4])+'\nDate Company was created: '+ str(comp[5])+
                                '\nCompany Worth: '+ str(comp[6])+'\nCompany Founder: '+ founder, on_release=partial(self.details, comp[0]),
                                background_color='blue'))
        root = ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        root.add_widget(companies)
        main.add_widget(root)
        self.main = main 
        return self.main
    def gotousr(self,  *args):
        self.manager.current='Users'
    def gotomakecomp(self, *args):
        self.manager.current='Make_Comp'
    def gotopro(self, *args):
        self.manager.current = 'Profile'
    def gotochats(self, *args):
        self.manager.current='Chats'
    def details(self, id, *args):
        exact_user = requests.post(url='http://'+User.IP+':5000/get/comp_detail', json={'id': id})
        print(exact_user.json())
        final = GridLayout(cols=2, rows=len(exact_user.json())+2, spacing=10)
        final.add_widget(Label(text='Name: '+ exact_user.json()[1]))
        final.add_widget(Label(text='Worth: '+ str(exact_user.json()[-1])))
        inves = requests.post(url='http://'+User.IP+':5000/get/comp/investors', json={'id':id})
        investors = ','.join(inves.json()['IN'][0])
        print(investors)
        final.add_widget(Label(text='Investors: ' + investors if investors != '' else 'No investors'))
        final.add_widget(Label(text='cost: -'+ str(exact_user.json()[3])))
        final.add_widget(Label(text='Daily gain: '+  str(exact_user.json()[4])))
        final.add_widget(Label(text='Money: ' + str(exact_user.json()[6])))
        final.add_widget(Label(text='Most likely amount of money in 100 days'))
        graph = Graph()
        graph.x_ticks_minor=1
        graph.x_ticks_major=10
        graph.y_ticks_major=10
        graph.y_ticks_minor =1
        graph.y_grid_label=True
        graph.x_grid_label=True
        graph.padding=5
        graph.x_grid=True
        graph.y_grid=True
        graph.x_min=-0
        graph.x_max=100
        money = exact_user.json()[6]
        graph.y_min=money
        graph.y_max=(money+((exact_user.json()[4] * 100) - (exact_user.json()[3]*100))) +100
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points=[(x, money + (exact_user.json()[4]*x)-(exact_user.json()[3]*x)) for x in range(0, 101)]
        graph.add_plot(plot)
        final.add_widget(graph)
        close = Button(text='Close', font_size=25)
        final.add_widget(close)
        final.add_widget(Button(text='Invest in ' + exact_user.json()[1], on_release=partial(self.investincmp, id)))
        poped = Popup(title=exact_user.json()[1]+' details', content=final)
        poped.open()
        close.bind(on_release=poped.dismiss)
    def investincmp(self, id, *args):
        percent= requests.post(url='http://'+User.IP+':5000/get/comp/investors/percents', json={'id': id})
        if percent.json()['Can_You_invest'] ==True:
            mains = GridLayout(cols=1, rows=3)
            mains.add_widget(Label(text="Congratuation you can invest in "+ 
            str(percent.json()['Percent_left_to_invest_in'])+' percent of the company'))
            money_prompt= GridLayout(cols=1, rows=2)
            money_prompt.add_widget(Label(text='How much money do you want to put in? ', size_hint=(.3, .1)))
            self.money_prompt = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.4, .4), 
            )
            anch = AnchorLayout()
            anch.add_widget(self.money_prompt)
            money_prompt.add_widget(anch)
            percent_prompt = GridLayout(cols=1, rows=2)
            percent_prompt.add_widget(Label(text='What percent of the company would you like to own', size_hint=(.3, 1)))
            self.percent_promp  = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.4, .4), 
            )
            anch = AnchorLayout()
            anch.add_widget(self.percent_promp)
            percent_prompt.add_widget(anch)
            group = GridLayout(cols=2)
            group.add_widget(money_prompt)
            group.add_widget(percent_prompt)
            mains.add_widget(group)
            buttons = GridLayout(cols=2, rows=1)
            close = Button(text='Close', size_hint=(.2, .3))
            anch = AnchorLayout()
            anch.add_widget(close)
            buttons.add_widget(anch)
            print('money',self.money_prompt.text)
            investsnow = Button(text='Invest', font_size=25,size_hint=(.2, .3))
            anch = AnchorLayout()
            anch.add_widget(investsnow)
            buttons.add_widget(anch)
            mains.add_widget(buttons)
            pops = Popup(title='Invest now', content=mains)
            pops.open()
            close.bind(on_release=pops.dismiss)
            investsnow.bind(on_release=partial(self.investnow, id, percent.json()['Percent_left_to_invest_in']))
        else:
            mains = RelativeLayout(size=(300,300))
            mains.add_widget(Label(text='You can not invest in the company, the company is owned 100% try seeing if you can buy some percent of it from user', pos_hint={'center_x': .5,'center_y':.5}))
            close=Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5,'center_y':.4})
            mains.add_widget(close)
            pops = Popup(title='Unable to invest in company', content=mains)
            pops.open()
            close.bind(on_release=pops.dismiss)
    def investnow(self, id, aval, *args):
        print('User clicked on invest now with id of ', id)
        if self.money_prompt.text != '' and self.percent_promp.text !='':
            print('User filled it out')
            if self.money_prompt.text.isdecimal() and (self.percent_promp.text.isdecimal() and self.percent_promp.text != float):
                if int(self.percent_promp.text) <= aval:
                    print("Use used only numbers")
                    user_money = int(self.money_prompt.text)
                    percent = float(int(self.percent_promp.text)/100)
                    success = requests.post(url='http://'+User.IP+':5000/get/comp/investnow', json={'user_id': User.id, 
                    'money': user_money, 'comp_id': id, 'percent': percent})
                    print('success', success.json())
                    if success.json()['Success']:
                        self.issue_warn(text='Successfully sent invest request to company owner', title='Success')
                    elif success.json()['Success']== False and success.json()['issue']=='not enough money':
                        self.issue_warn(text='You do not have enough money to invest', title='Not enough money')
                    else:
                        self.issue_warn(text='There was a problem sending invest request to company owner,\n please try again later', title='Issue')
                else:
                    self.issue_warn(text='You can not own that much of the company', title='Incorrect value')
            else:
                self.issue_warn(text='Please use only numbers', title='Incorrect type of input')
        else:
            self.issue_warn(text='Please fill out the form',title='Unfilled form') 
    def issue_warn(self, text, title):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        my_button = Button(text='Ok', size_hint=(1, .25))
        box.add_widget(my_button)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        my_button.bind(on_release=popup.dismiss)
        popup.open()
        
