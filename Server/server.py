if __name__ == '__main__':
    import kivy
    kivy.require('2.0.0')
    from kivy.config import Config
    Config.set('graphics', 'multisamples', '0')
    import os
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.screenmanager import ScreenManager
    from app_looks import MainScreen, Users, Companies, Investors
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.base import runTouchApp
    from kivy.lang import Builder
    from kivy.uix.boxlayout import BoxLayout
    from kivy.core.window import Window
    class Server(App):
        def build(self):
            Window.bind(on_request_close=self.close_win)
            sm = ScreenManager()
            sm.tittle = 'InvestIt Server'
            sm.add_widget(MainScreen())
            sm.add_widget(Users())
            sm.add_widget(Companies())
            sm.add_widget(Investors())
            MainScreen.manager = sm
            Users.manager = sm
            Companies.manager = sm
            Investors.manager = sm
            try:
                f = open("LogFile.txt", "x")
                f.close
            except Exception as e:
                print(e)
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
            try:
                os.remove('LogFile.txt')
            except Exception as e:
                print(e)
            App.get_running_app().stop()


    Server().run()
