from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window 
from functools import partial
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.anchorlayout import AnchorLayout
import requests
from looks.user import User
import threading
import time