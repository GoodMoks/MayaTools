import os

import MayaTools.menu as menu

# main_name = menu.get_main_package_name(__file__)
path_global = r'E:\Work\Pipeline\Projects\Tools\MayaTools\test_menu'
parents = dict()
parent = 'MayaTools.test_menu'
commands = [('Paths', 'import sys; for p in sys.path:   print p')]
#
# def import_module():
#     print 'init test'
#     import animation
#     # import rigging
#     # import skining
#     print 'end init'


def create_menu(path, commands):
    # print path
    # print commands
    parent = menu.get_parent_package_name(path) # MayaTools
    main = menu.get_main_package_name(path) # test_menu
    #print parents
    parents[main] = menu.install(main, commands, parents.get(parent, menu.menu_name))

def test_load_menu(path=path_global, parent=parent):
    """
    name modules, [(label, command)]

    :return:
    """
    for root, dirs, files in os.walk(path, True, None):
        for f in files:
            if f.endswith(".py"):
                if f == "__init__.py": # E:\Work\Pipeline\Projects\Tools\MayaTools\test_menu
                    try:
                        module = __import__(parent, globals(), locals(), ["*"], -1) # MayaTools.test_menu
                        create_menu(path, module.commands)
                    except:
                        pass

        for d in dirs:
            new_path = '{}/{}'.format(path, d)
            print new_path, 'new path'
            new_parent = '{}.{}'.format(parent, d)
            print new_parent, 'new parent'
            test_load_menu(new_path, new_parent)

        break

if __name__ == '__main__':
    test_load_menu()

