import pymel.core as pm


def add_attr(obj, attr, dv=0.5, min=0.0, max=1.0, at='double', en=None):
    if not obj.hasAttr(attr):
        pm.addAttr(obj, ln=attr, at=at, en=en, dv=dv, k=True, min=min, max=max)

