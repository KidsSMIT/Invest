from kivy.uix.screenmanager import ScreenManager
from looks.getip import GetIP, User
from looks.invest import Invest
from looks.login import Login
from looks.profile import Profile
from looks.makecompany import MakeCompany
from looks.user_ranks import User_Rank
from looks.chat import Chat
sm = ScreenManager()
sm.title='InvestIt'
users = User()
sm.add_widget(GetIP())
sm.add_widget(Login())
sm.add_widget(Profile())
sm.add_widget(Invest())
sm.add_widget(MakeCompany())
sm.add_widget(User_Rank())
sm.add_widget(Chat())
Login.manager = sm
GetIP.manager = sm 
Profile.manager= sm
Invest.manager=sm
MakeCompany.manager= sm
Chat.manager=sm
def close():
    print('Closing')
    Chat._in_chat_screen = False
    Chat.close()