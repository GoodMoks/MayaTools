import os
import pymel.core as pm
import MayaTools


class Menu(object):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(MayaTools.__file__)))

    @staticmethod
    def get_parent(filepath):
        return os.path.basename(os.path.dirname(filepath))

    @staticmethod
    def install_submenu(label, parent, tearOff=True):
        menu = pm.menuItem(parent=parent, subMenu=True,
                           tearOff=tearOff, label=label, ia='')

        return menu

    @staticmethod
    def install_item(items, parent):
        pm.setParent(parent, m=True)
        for label, command in items:
            if not command:
                pm.menuItem(divider=True, ld=True, label=label)
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

        self.main_parent = None
        self.main_import_path = None

        self.restore_menu(self.path)

    def get_main_import(self, path):
        items = os.path.relpath(path, self.ROOT_DIR).split('\\')
        return '.'.join(items)

    def restore_menu(self, path):
        name = os.path.basename(path)
        if not self.name:
            self.name = name.capitalize()

        self.main_parent = self.get_parent(path)
        self.main_import_path = self.get_main_import(path)
        self.name = self.create(self.name)
        self.load_menu(path, self.main_import_path)

    def create_item(self, path, commands):
        parent = self.get_parent(path)
        main = os.path.basename(path)
        if parent == self.main_parent:
            main = self.name

        self.parents[main] = self.install_menu(main, commands, self.parents.get(parent, self.name))

    def install_menu(self, label, items, parent):
        menu = self.name
        if not label == parent:
            menu = self.install_submenu(label, parent)

        self.install_item(items=items, parent=menu)

        return menu

    def load_menu(self, path, parent):
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
                self.load_menu(new_path, new_parent)

            break

