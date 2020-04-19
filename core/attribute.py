import pymel.core as pm

""" Module for work with attribute """

def add_attr(obj, attr, dv=0.5, min=0.0, max=1.0, at='double', en=None):
    """ add attr to object

    :param obj: 'str' object
    :param attr: 'str' attribute name
    :param dv: 'float' default value
    :param min: 'float' minimum value
    :param max: 'float' maximum value
    :param at: 'str' attribute type
    :param en:
    :return: 'bool' True if attr was created else not False
    """
    if not obj.hasAttr(attr):
        pm.addAttr(obj, ln=attr, at=at, en=en, dv=dv, k=True, min=min, max=max)
        return True
    return False

