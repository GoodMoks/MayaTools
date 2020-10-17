import os
import pymel.core as pm
import MayaTools

NAME = 'AnimStudio'


class Menu(object):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(MayaTools.__file__)))

    @staticmethod
    def get_parent(filepath):
        return os.path.basename(os.path.dirname(filepath))

    @staticmethod
    def get_main(filepath):
        return os.path.basename(filepath)

    @staticmethod
    def install_submenu(label, parent, tearOff=True):
        menu = pm.menuItem(parent=parent, subMenu=True,
                           tearOff=tearOff, label=label)

        return menu

    @staticmethod
    def install_item(items, parent):
        pm.setParent(parent, m=True)
        for label, command in items:
            if not command:
                pm.menuItem(divider=True)
                continue
            pm.menuItem(label=label, command=command)

    @staticmethod
    def create(menu):
        if pm.menu(menu, exists=True):
            pm.deleteUI(menu)

        menu = pm.menu(menu,
                       parent="MayaWindow",
                       tearOff=True,
                       allowOptionBoxes=True,
                       label=menu)

        return menu

    def __init__(self, path, name=None):
        self.path = path
        self.name = name
        self.parents = dict()

        self.main_parent_dir = None
        self.main_import_path = None

        self.restore_menu(self.path)

    def get_root_dir(self, path):
        items = os.path.relpath(path, self.ROOT_DIR).split('\\')
        return '.'.join(items)

    def restore_menu(self, path):
        name = self.get_main(path)
        if not self.name:
            self.name = name.capitalize()

        self.main_parent_dir = self.get_parent(path)
        self.main_import_path = self.get_root_dir(path)
        self.name = self.create(self.name)
        self.test_load_menu(path, self.main_import_path)

    def create_item(self, path, commands):
        parent = self.get_parent(path)
        main = self.get_main(path)
        if parent == self.main_parent_dir:
            main = self.name

        self.parents[main] = self.install_menu(main, commands, self.parents.get(parent, self.name))

    def install_menu(self, label, items, parent):
        menu = self.name
        if not label == parent:
            menu = self.install_submenu(label, parent)

        self.install_item(items=items, parent=menu)

        return menu

    def test_load_menu(self, path, parent):
        for root, dirs, files in os.walk(path, True, None):
            for f in files:
                if f.endswith(".py"):
                    if f == "__init__.py":
                        try:
                            module = __import__(parent, globals(), locals(), ["*"], -1)
                            if hasattr(module, 'commands'):
                                self.create_item(path, module.commands)
                        except:
                            pass

            for d in dirs:
                new_path = '{}/{}'.format(path, d)
                new_parent = '{}.{}'.format(parent, d)
                self.test_load_menu(new_path, new_parent)

            break


def create_menu():
    path = os.path.dirname(__file__)
    Menu(path, name=NAME)
