from looks.imports import threading, Screen, BoxLayout, partial, AnchorLayout, requests,GridLayout, Button, User,ScrollView, Window, Graph, MeshLinePlot, Popup, TextInput, RelativeLayout, Label, time
class Chat(Screen):
    manager = None
    _in_chat_screen = False
    def __init__(self, **args):
        Screen.__init__(self, name='Chats') 
        self.chat_open= [False]
        self._current_chat= ''
        self.text=''
    def close():
        Chat._in_chat_screen=False
    def on_pre_enter(self, *args):
        self.chat = Label()
        self.message_to_send = TextInput()
        self.add_widget(self.chatss())
        Chat._in_chat_screen=True
        threading.Thread(target=self.continues_update).start()
    def on_leave(self, *args):
        self.remove_widget(self.main) 
        Chat._in_chat_screen = False  
    def chatss(self, *args):
        main = GridLayout(cols=1, rows=2)
        top = GridLayout(cols=5, rows=1)
        top.add_widget(Button(text='Back to profile', background_color='black', on_release=self.gotopro))
        top.add_widget(Button(text='Companies', background_color ='black', on_release=self.gotocompany))
        top.add_widget(Button(text='Users rank', background_color ='black', on_release=self.gotousr))
        top.add_widget(Button(text='Make a company', background_color='black', on_release=self.gotomakecomp))
        top.add_widget(Button(text='Chat', background_color='black', color='green'))
        main.add_widget(top)
        self.chat_view = GridLayout(cols=2, rows=1)
        all_users = requests.get(url='http://'+User.IP+':5000/get/all/users')
        print(all_users.json())
        users = GridLayout(cols=1, rows=len(all_users.json())+3, spacing=1, size_hint_y=1)
        for i in all_users.json():
            if User.name != i[1]:
                anch = AnchorLayout()
                anch.add_widget(Button(text=i[1], background_color='blue',size_hint=(.2,.2), on_release=partial(self.openchat, i[0], User.id, i[1]), background_normal='normal.png',background_down='down.png',border=(0, 32, 0, 32)))
                users.add_widget(anch)  
        root = ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        root.add_widget(users)
        self.chat_view.add_widget(root)  
        self.chats = BoxLayout(orientation='vertical')
        self.chats.add_widget(Label(text='Click on the User you would like to chat with'))
        self.chat_view.add_widget(self.chats)
        main.add_widget(self.chat_view) 
        self.main = main
        return self.main
    def gotopro(self, *args):
        self.manager.current = 'Profile'
    def gotocompany(self, *args):
        self.manager.current = 'Invest'
    def gotousr(self, *args):
        self.manager.current = 'Users' 
    def gotomakecomp(self, *args):
        self.manager.current='Make_Comp'
    def openchat(self, chat_id, user_id, clicked_name, *args):
        self.chat_open=[True, chat_id, user_id, clicked_name]
        print("User clicked me, for the chat_id of", chat_id, 'and user_id is', user_id, 'also the clicked name was', clicked_name)
        self.chat_view.remove_widget(self.chats)
        chats_det = requests.post(url='http://'+User.IP+':5000/get/certain/user/chat', json={'chat_id': chat_id, 'user_id':user_id})
        print('Chat details', chats_det.json())
        """
        This is how the message will look
        Name Date_Sent
        Message
        """
        self.chat = Label()
        self.chats= BoxLayout(orientation='vertical') 
        name=''
        for i in chats_det.json():
            if i[0] == chat_id:
                name += clicked_name + '     '+i[3] +'\n      '+i[2]+'\n'
            else:
                name += 'You' + '    ' + i[3]+'\n        '+i[2]+'\n'
        print('name',name)
        self._current_chat= name
        self.chat.text= name
        anch = AnchorLayout(anchor_x='left')
        anch.add_widget(self.chat)
        ach = GridLayout(cols=1, size_hint_y=len(chats_det.json())/2, spacing=10)
        ach.add_widget(anch)
        root = ScrollView(size_hint=(1,1), size=(Window.width, Window.height))
        root.add_widget(ach)
        root.scroll_y=0.27
        send = GridLayout(cols=2, rows=1)
        self.message_to_send = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, 
            size_hint=(1, .3), text=self.text
            )
        anch = AnchorLayout()
        anch.add_widget(self.message_to_send)
        send.add_widget(anch)
        anch = AnchorLayout(anchor_x='center')
        anch.add_widget(Button(text='Send', size_hint=(.3,.2), 
        on_release=partial(self.send_message, chat_id, user_id, clicked_name), color='white', background_color='blue',
        pos_hint={'center_x':.2,'center_y':.5}))
        send.add_widget(anch)
        self.chats.add_widget(root)
        self.chats.add_widget(send)
        self.chat_view.add_widget(self.chats)
    def send_message(self, chat_id, user_id, clicked_name, *args):
        print('User tried to send a message')
        send_new_message = requests.post(url='http://'+User.IP+':5000/send/message/to/user',
        json={'from_user': user_id,'to_user':chat_id, 'message':self.message_to_send.text})
        print(send_new_message, send_new_message.json())
        if send_new_message.json()['Success']:
            self.message_to_send.text = '' 
            self.openchat(chat_id, user_id, clicked_name)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='There was problem sending message, please check internet connection.'))
            my_button = Button(text='Ok', size_hint=(1, .25))
            box.add_widget(my_button)
            popup = Popup(title='Issue', content=box, size_hint=(None, None), size=(600, 300))
            my_button.bind(on_release=popup.dismiss)
            popup.open()
    def continues_update(self, *args):
        past_chat = ''
        while Chat._in_chat_screen:
            time.sleep(2)
            if self.chat_open[0]:
                past_chat = ''
                chats_det = requests.post(url='http://'+User.IP+':5000/get/certain/user/chat', json={'chat_id': self.chat_open[1], 'user_id':self.chat_open[2]})
                for i in chats_det.json():
                    if i[0] == self.chat_open[1]:
                        past_chat += self.chat_open[3] + '     '+i[3] +'\n      '+i[2]+'\n'
                    else:
                        past_chat += 'You' + '    ' + i[3]+'\n        '+i[2]+'\n'
                if self._current_chat != past_chat:
                    self.text = self.message_to_send.text
                    self.openchat(self.chat_open[1], self.chat_open[2], self.chat_open[3])