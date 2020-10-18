import os
import pymel.core as pm
import MayaTools
import MayaTools.tools.menu_creator.menu as menu
reload(menu)


NAME = None

def create_menu():
    path = os.path.dirname(__file__)
    menu.Menu(path, name=NAME)
