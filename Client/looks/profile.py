from looks.imports import Screen, GridLayout, requests,Label, ScrollView, User, Window, Button
class Profile(Screen):
    manager=None
    def __init__(self, **args):
        Screen.__init__(self, name='Profile')
    def on_pre_enter(self, *args):
        self.add_widget(self.profile())
    def on_leave(self, *args):
        self.remove_widget(self.main)   
    def profile(self, *args):
        main = GridLayout(cols=1, rows= 2)
        mains = GridLayout(cols=3, rows=1)
        user_infor = GridLayout(cols=1, rows=8)
        exact_user = requests.post(url='http://'+User.IP+':5000/exact_user', json={'username': User.name, 'password': User.password})
        infor = exact_user.json()['data']
        user_infor.add_widget(Label(text='User Information'))
        for infors in zip(['id', 'name', 'password', 'Money', 'Amount gained daily', 'Amount lost daily'], infor):
            if infors[0] == 'id':
                continue
            else:
                if infors[1] == str:
                    user_infor.add_widget(Label(text=infors[0] +': '+ infors[1]))
                else:
                    user_infor.add_widget(Label(text=infors[0] +': '+ str(infors[1])))
        num_comp_user = requests.post(url='http://'+User.IP+':5000/get/user/num/company', json={'username': User.name})
        user_infor.add_widget(Label(text='# of companies user owns: ' + str(num_comp_user.json()['number'])))
        num_comp_user = requests.post(url='http://'+User.IP+':5000/get/user/num/investor', json={'username': User.name})
        user_infor.add_widget(Label(text='# of company user is invested in: '+ str(num_comp_user.json()['number'])))
        name_comp = requests.post(url='http://'+User.IP+':5000/get/user/investor', json={'username': User.name})
        problem = False
        root=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        if name_comp.json()['companies_names'] == None:
            problem = True
        if problem == False:
            comp_name = GridLayout(cols=1, rows=len(name_comp.json()['companies_names'])+2, spacing=10, size_hint_y=len(name_comp.json()['companies_names'])/2)
            comp_name.add_widget(Label(text=''))
            comp_name.add_widget(Label(text='Name of companies user is invested in', font_size=15))
            for names in name_comp.json()['companies_names']:
                print(names)
                comp_name.add_widget(Label(text=names[0]))
        else:
            comp_name=GridLayout(cols=1, rows=2, spacing=10, size_hint_y=2)
            comp_name.add_widget(Label(text=''))
            comp_name.add_widget(Label(text='You are not invested in any company'))
        root.add_widget(comp_name)
        rooted=ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        name_of_owned_comp=requests.post(url='http://'+User.IP+':5000/get/user/own_comp', json={'username': User.name})
        problem = False
        if name_of_owned_comp.json()['companies_name'] == None or name_of_owned_comp.json()['companies_name']==[]:
            problem=True
        if problem == False:
            user_comp_owned = GridLayout(cols=1, rows=len(name_of_owned_comp.json()['companies_name'])+2, spacing=10, size_hint_y=len(name_of_owned_comp.json()['companies_name'])/2)
            user_comp_owned.add_widget(Label(text=''))
            user_comp_owned.add_widget(Label(text='Name of companies the user owns', font_size=15))
            for name in name_of_owned_comp.json()['companies_name']:
                user_comp_owned.add_widget(Label(text=name[0]))
        else:
            user_comp_owned = GridLayout(cols=1, rows=2, spacing=10, size_hint_y=1)
            user_comp_owned.add_widget(Label(text=''))
            user_comp_owned.add_widget(Label(text='You do not own any companies', font_size=15))
        rooted.add_widget(user_comp_owned)
        mains.add_widget(user_infor)
        mains.add_widget(root)
        mains.add_widget(rooted)
        top = GridLayout(cols=2, rows=1, size_hint=(.3,.1))
        top.add_widget(Button(text='Profile', color='green', size_hint=(.1, .1),  background_color ='black'))
        top.add_widget(Button(text='Invest',on_release=self.gotoinvest,  background_color ='black', size_hint=(.1,.1)))
        main.add_widget(top)
        main.add_widget(mains)
        self.main = main
        return self.main
    def gotoinvest(self, *args):
        self.manager.current='Invest'