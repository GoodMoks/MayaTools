import pymel.core as pm
import maya.OpenMaya as om


def history(node, type=None):
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
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(object, selectionList)
    mObject = om.MObject()
    selectionList.getDependNode(0, mObject)
    return mObject


def isShape(obj):
    # Check Shape
    mObject = get_MObject(obj)
    if not mObject.hasFn(om.MFn.kShape):
        return False

    return True


def get_children(obj, all=False, shapes=False):
    child = pm.listRelatives(obj, c=True, ad=all)
    if child:
        if not shapes:
                return [c for c in child if not isShape(c)]
        return child




# def get_children(obj, all=False):
#
#     if child:
#         child.append(obj)
#         shapes_set = set()
#         child_set = set(child)
#         [[shapes_set.add(x) for x in pm.listRelatives(c, shapes=True)] for c in child if
#          pm.listRelatives(c, shapes=True)]
#         obj_set = set([obj])
#         filtred_set = child_set.difference(shapes_set)
#         return list(filtred_set.difference(obj_set))


def get_parent(obj, all=False):
    return pm.listRelatives(obj, p=True, ap=all, shapes=False)
