import maya.utils


def initialize():
    add_path()
    add_menu()


def add_path():
    import os
    import sys
    import inspect

    __file__ = os.path.abspath(inspect.getsourcefile(lambda: 0))

    tools_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    if tools_path not in sys.path:
        sys.path.append(tools_path)


def add_menu():
    import MayaTools.startup.Menu.menu as menu
    menu.create_menu()


maya.utils.executeDeferred(initialize)

