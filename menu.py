import os
import pymel.core as pm


class Menu(object):
    @staticmethod
    def get_parent_package_name(filepath):
        return os.path.basename(os.path.dirname(filepath))

    @staticmethod
    def get_main_package_name(filepath):
        return os.path.basename(filepath)

    @staticmethod
    def install_submenu(label, parent, tearOff=True):
        return pm.menuItem(parent=parent, subMenu=True,
                           tearOff=tearOff, label=label)

    @staticmethod
    def install_item(items, parent):
        pm.setParent(parent, m=True)
        for label, command, in items:
            if not command:
                pm.menuItem(divider=True)
                continue
            pm.menuItem(label=label, command=command)

    @staticmethod
    def create(menu):
        if pm.menu(menu, exists=True):
            pm.deleteUI(menu)

        pm.menu(menu,
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

    def restore_menu(self, path):
        name = self.get_main_package_name(path)
        if not self.name:
            self.name = name.capitalize()

        self.main_parent_dir = self.get_parent_package_name(path)
        self.main_import_path = '{}.{}'.format(self.main_parent_dir, name)
        self.name = self.create(self.name)
        self.test_load_menu(path, self.main_import_path)

    def create_item(self, path, commands):
        parent = self.get_parent_package_name(path)  # MayaTools
        main = self.get_main_package_name(path)  # test_menu
        if parent == self.main_parent_dir:
            main = self.name
        self.parents[main.capitalize()] = self.install_menu(main.capitalize(), commands,
                                                            self.parents.get(parent.capitalize(), self.name))

    def install_menu(self, label, items, parent):
        menu = self.name
        if not label == parent:
            menu = self.install_submenu(label, parent)

        self.install_item(items=items, parent=menu)

        if menu:
            return menu

        return parent

    def test_load_menu(self, path, parent):
        for root, dirs, files in os.walk(path, True, None):
            for f in files:
                if f.endswith(".py"):
                    if f == "__init__.py":
                        try:
                            module = __import__(parent, globals(), locals(), ["*"], -1)
                            self.create_item(path, module.commands)
                        except:
                            pass

            for d in dirs:
                new_path = '{}/{}'.format(path, d)
                new_parent = '{}.{}'.format(parent, d)
                self.test_load_menu(new_path, new_parent)

            break
