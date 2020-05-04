import maya.api.OpenMaya as om2
import maya.OpenMaya as om
import maya.cmds as cmds


''' base functions, api functions'''


def get_MObject(object):
    """ get MObject for given object

    :param object: 'str' object
    :return: MObject
    """
    selectionList = om2.MGlobal.getSelectionListByName(object)
    return selectionList.getDependNode(0)


def get_history(node, type=None):
    """ get node for type in history connections

    :param node: 'str' object
    :param type: 'str' type of object
    :return: 'list' with objects or []
    """
    history = cmds.listHistory(node)
    if not type:
        return history

    return [n for n in history if cmds.nodeType(n) == type]


def isShape(obj):
    """ check if the given object is a shape node

    :param obj: 'str' object
    :return: 'boot' True if object is shape
    """
    mObject = get_MObject(obj)
    if not mObject.hasFn(om2.MFn.kShape):
        return False

    return True

def get_instances():
    """ get all instance object in the scene

    :return: 'list' with instances or []
    """
    instances = []
    iterDag = om2.MItDag(om2.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om2.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances


def get_instances_test():
    """ get all instance object in the scene

    :return: 'list' with instances or []
    """
    instances = []
    iterDag = om2.MItDag(om2.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om2.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances

def get_object_with_attr(obj_type, attr):
    """ get objects who has given attr

    :param obj_type: 'om2.MFn.kLocator'
    :param attr: 'str' name of attr
    :return: 'list' with objects
    """
    instances = []
    iterDag = om2.MItDag(om2.MItDag.kDepthFirst, obj_type)
    while not iterDag.isDone():
        m_object = iterDag.currentItem()
        m_objFn = om2.MFnDependencyNode(m_object)
        if m_objFn.hasAttribute(attr):
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances


def is_pymel(obj):
    """ check is pymel object

    :param obj: object
    :return: 'bool' True if pymel object
    """
    try:
        module = obj.__module__
        print module
    except AttributeError:
        try:
            module = obj.__name__
        except AttributeError:
            return False
    return module.startswith('pymel')


def get_dag_path(obj):
    """ get dag path of given object

    :param obj: object
    :return: dag path
    """
    dag_path = om.MDagPath()
    sel = om.MSelectionList()
    sel.add(str(obj))
    sel.getDagPath(0, dag_path)
    return dag_path
