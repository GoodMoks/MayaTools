import os
import pymel.core as pm
import MayaTools.menu as menu


def create_menu():
    path = os.path.dirname(__file__)
    menu_class = menu.Menu(path, name='Lool')

    menu_class.install_item(items=[("Item", "import os")], parent=menu_class.parents['Mocap'])
