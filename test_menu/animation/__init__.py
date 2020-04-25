# import MayaTools.menu as menu
# import MayaTools.test_menu as test
# parent_name = menu.get_parent_package_name(__file__)
# main_name = menu.get_main_package_name(__file__).capitalize()
#
# commands = [
#     ('------', None)
# ]
#
# test.parents[main_name] = menu.install(main_name, commands, test.parents.get(parent_name, menu.menu_name))
#
# import mocap

commands = [
    ('new_tool', 'import new_tool')
]