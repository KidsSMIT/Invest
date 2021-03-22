from looks.imports import Screen, partial, requests,GridLayout, Button, User,ScrollView, Window, Graph, MeshLinePlot, Popup, TextInput, RelativeLayout, Label
class User_Rank(Screen):
    manager= None
    def __init__(self, **args):
        Screen.__init__(self, name='Users')
    def on_pre_enter(self, *args):
        self.add_widget(self.rank()) 
    def on_leave(self, *args):
        self.remove_widget(self.main)
    def rank(self, *args):
        ranks = requests.post(url='http://'+User.IP+':5000/UserRanksArrange', json={'id': User.id})
        print(ranks.json())
        top = GridLayout(cols=5, rows=1)
        top.add_widget(Button(text='Back to profile', background_color='black', on_release=self.gotopro))
        top.add_widget(Button(text='Companies', background_color ='black', on_release=self.gotocompany))
        top.add_widget(Button(text='Users rank', background_color ='black', color='green'))
        top.add_widget(Button(text='Make a company', background_color='black', on_release=self.gotomakecomp))
        top.add_widget(Button(text='Chat', on_release=self.gotochats, background_color='black'))
        main = GridLayout(cols=1, rows=2)
        main.add_widget(top) 
        rank = GridLayout(cols=1, rows=1) 
        rank.add_widget(Button(text='Your Rank: '+ str(ranks.json()['User_INFOR']['Rank'])+'     Your Money: '+ str(ranks.json()['User_INFOR']['Money']), background_color='green'))
        root = ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        root_content = GridLayout(cols=1, rows=len(ranks.json()['Rank_'])+2, spacing=10, size_hint_y=len(ranks.json()['Rank_']))
        num = 1
        root_content.add_widget(rank)
        for ran in ranks.json()['Rank_']:
            root_content.add_widget(Label(text=str(num)+'. '+ran[2]+'       Money: '+ str(ran[0])))
            num +=1
        root.add_widget(root_content)
        main.add_widget(root) 
        self.main = main
        return self.main
    def gotopro(self, *args):
        self.manager.current = 'Profile'
    def gotocompany(self, *args):
        self.manager.current='Invest'
    def gotomakecomp(self, *args):
        self.manager.current='Make_Comp'
    def gotochats(self, *args):
        self.manager.current='Chats'