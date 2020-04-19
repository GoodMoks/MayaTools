import pymel.core as pm
import maya.OpenMaya as om


def get_history(node, type=None):
    """ get node for type in history connections

    :param node: 'str' object
    :param type: 'str' type of object
    :return: 'list' with objects or []
    """
    history = pm.listHistory(node)
    if not type:
        return history

    return [n for n in history if pm.nodeType(n) == type]



def get_MObject(object):
    """ get MObject for given object

    :param object: 'str' object
    :return: MObject
    """
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(object, selectionList)
    mObject = om.MObject()
    selectionList.getDependNode(0, mObject)
    return mObject


def isShape(obj):
    """ check if the given object is a shape node

    :param obj: 'str' object
    :return: 'boot' True if object is shape
    """
    mObject = get_MObject(obj)
    if not mObject.hasFn(om.MFn.kShape):
        return False

    return True


def get_children(obj, all=False, shapes=False):
    """ get children for given object

    :param obj: 'str' object
    :param all: 'bool' True: get all children in hierarchy
    :param shapes: 'bool' False: skip all shapes node
    :return: 'list' of children or []
    """
    child = pm.listRelatives(obj, c=True, ad=all)
    if child:
        if not shapes:
                return [c for c in child if not isShape(c)]
        return child



def get_parent(obj, all=False):
    """ get parents for given objects

    :param obj: 'str' object
    :param all: 'bool' True: get all parents in hierarchy
    :return: 'list' with parents or []
    """
    return pm.listRelatives(obj, p=True, ap=all, shapes=False)
