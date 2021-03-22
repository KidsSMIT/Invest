import kivy
kivy.require('2.0.0')
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.app import App
from kivy.core.window import Window 
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from looks.imports import User, requests,partial, GridLayout, time
from looks.manager import sm,close
import threading
class TradeIt(App):
    def build(self):
        Window.bind(on_request_close=self.close_win)
        #threading.Thread(target=self.continuesUpdate).start()
        threading.Thread(target=self.lookfortransactions).start()
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
        close()
        App.get_running_app().stop()
    def continuesUpdate(self, *args):
        print("User Update thread started")
        while User.active:
            User.update(requests)
        print("User Update thread ended")
    def lookfortransactions(self, *args):
        print('Starting to look for incoming transactions')
        while User.active:
            if User.IP != None and User.id != None:
                transa = requests.post(url='http://'+User.IP+':5000/send/user/transaction', json={'user_id': User.id})
                if transa.json()['Success'] == True:
                    for i in transa.json()['Transcations']:
                        self.next = False
                        print('transaction', i)
                        state= i[0] +" wants "+str(i[2])+' percent of '+i[3]+' and is willing to pay '+ str(i[1])
                        self.translook(state, i)
                        while self.next == False and User.active:
                            time.sleep(1)
        print("No longer looking for incoming transactions")
    def translook(self, statement, values, *args):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=statement))
        buttons= GridLayout(rows=2)
        close= Button(text='Decline', background_color='red')
        buttons.add_widget(close)
        opens = Button(text='Accept', background_color='green')
        buttons.add_widget(opens)
        box.add_widget(buttons)
        popup = Popup(title='Company Transactions', content=box, size_hint=(None, None), size=(600, 300))
        popup.open()
        close.bind(on_release=partial(self.deny, values, popup))
        opens.bind(on_release=partial(self.accept, values, popup))
    def deny(self, values, pop, *args):
        print("User denied")
        done = requests.post(url='http://'+User.IP+':5000/denied/user/transaction', json={'row': values[4]})
        if done.json()['Complete']:
            pop.dismiss()
            self.next=True
    def accept(self, values, pop, *args):
        print("User accepted")
        done= requests.post(url='http://'+User.IP+':5000/accept/user/transaction', json={'row': values[4]})
        if done.json()['Complete']:
            pop.dismiss()
            self.next=True


if __name__ =='__main__':
    TradeIt().run()