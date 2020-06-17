import maya.cmds as cmds
import MayaTools.core.base as base
import maya.api.OpenMaya as om2

""" Module for work with attribute """

main_attr = ['tx', 'ty', 'tz',
             'rx', 'ry', 'rz',
             'sx', 'sy', 'sz',
             'visibility']


def has_attr(obj, attr):
    """ check exist attribute in object

    :param obj: 'srt' object
    :param attr: 'str' attribute
    :return: 'bool' True if attr exist
    """
    m_obj = base.get_MObject(obj)
    dep_node = om2.MFnDependencyNode(m_obj)
    return dep_node.hasAttribute(attr)


# def is_proxy_attr(obj, attr):
#     m_obj = base.get_MObject(obj)
#     dep_node = om2.MFnDependencyNode(m_obj)
#     return dep_node.a


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

    if not hasattr(obj, attr):
        cmds.addAttr(obj, ln=attr, at=at, en=en, dv=dv, k=True, min=min, max=max)
        return True
    return False


def unlock_attr(obj, attr):
    """ Unlocks main attributes

    :param obj: 'list' name of object
    :param attr: 'list' attr to unlock
    """

    for a in attr:
        full_attr = '{}.{}'.format(obj, a)
        try:
            cmds.setAttr(full_attr, l=False, k=True)
        except:
            pass
