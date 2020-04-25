def initialize():
    import os
    import sys

    # add relative path to Tools
    tools_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if tools_path not in sys.path:
        sys.path.append(tools_path)


    import MayaTools.menu as menu
    menu.create()

    import MayaTools.test_menu as test
    test.test_load_menu()