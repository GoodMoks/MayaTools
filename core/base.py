import maya.OpenMaya as om
import pymel.core as pm

''' base functions, api functions'''

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


def isShape(obj):
    """ check if the given object is a shape node

    :param obj: 'str' object
    :return: 'boot' True if object is shape
    """
    mObject = get_MObject(obj)
    if not mObject.hasFn(om.MFn.kShape):
        return False

    return True

def get_instances():
    """ get all instance object in the scene

    :return: 'list' with instances or []
    """
    instances = []
    iterDag = om.MItDag(om.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances