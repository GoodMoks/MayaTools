import os
import MayaTools.menus.menu as menu


def create_menu():
    path = os.path.dirname(__file__)
    menu.Menu(path, name='AnimationStudio')
