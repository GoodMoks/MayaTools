import pymel.core as pm

def get_license_user_name():
    name = 'IPM_Button_Placeholder'
    status = pm.ui.PyUI(name).asQtObject()
    children = status.children()[0]
    item = children.itemAt(0).widget()
    children = item.children()

    for child in children:
        try:
            name = child.text()
            if name:
                return name
        except:
            pass

class():
    def __init__(self):
        pass

