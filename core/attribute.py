import pymel.core as pm

""" Module for work with attribute """

main_attr = ['.tx', '.ty', '.tz',
             '.rx', '.ry', '.rz',
             '.sx', '.sy', '.sz',
             '.visibility']



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


def unlock_attr(obj, attr):
    """ Unlocks main attributes

    :param obj: 'list' list of object
    :param attr: 'list' attr to unlock
    """
    for o in obj:
        for a in attr:
            full_attr = '{}.{}'.format(o, a)
            try:
                pm.setAttr(full_attr, l=False, k=True)
            except:
                pass


