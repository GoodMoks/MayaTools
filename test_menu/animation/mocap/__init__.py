# import pymel.core as pm
# import MayaTools.menu as menu
# import MayaTools.test_menu as test
# parent_name = menu.get_parent_package_name(__file__)
# main_name = menu.get_main_package_name(__file__).capitalize()
#
# import test_module
#
# commands = [
#     ('test', pm.Callback(test_module.test_func))
# ]
#
# test.parents[main_name] = menu.install(main_name, commands, test.parents.get(parent_name, menu.menu_name))

commands = [
    ('test', 'import test_module; reload(test_module); test_module.test_func()')
]
