import pymel.core as pm
import os

menu_name = 'test_menu'



def get_parent_package_name(filepath):
    return os.path.basename(os.path.dirname(filepath))


def get_main_package_name(filepath):
    return os.path.basename(filepath)


def create(menu=menu_name):
    if pm.menu(menu, exists=True):
        pm.deleteUI(menu)

    pm.menu(menu,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menu)

    return menu


def install(label, commands, parent=menu_name):
    m = pm.menuItem(parent=parent,
                    subMenu=True,
                    tearOff=True,
                    label=label)
    for label, command in commands:
        if not command:
            pm.menuItem(divider=True)
            continue
        if not label:
            command(m)
            pm.setParent(m, menu=True)
            continue

        pm.menuItem(label=label, command=command)

    return m
