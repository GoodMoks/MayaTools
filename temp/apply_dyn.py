import pymel.core as pm

def apply():
    sel = pm.selected()
    if not sel:
        return

    for control in sel:
