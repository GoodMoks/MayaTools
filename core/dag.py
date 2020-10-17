import maya.cmds as cmds
import MayaTools.core.base as base

""" Module for work with DAG hierarchy """

def get_children(obj, all=False, shapes=False):
    """ get children for given object

    :param obj: 'str' object
    :param all: 'bool' True: get all children in hierarchy
    :param shapes: 'bool' False: skip all shapes node
    :return: 'list' of children or []
    """

    child = cmds.listRelatives(obj, c=True, ad=all, path=True)
    if child:
        if not shapes:
            return [c for c in child if not base.is_shape(c)]
        return child

def get_shapes(obj, skip=True):
    """ get shapes for given object

    :param obj: 'str' object
    :param skip: 'bool' skip intermediate objects
    :return: 'list' with shapes or []
    """
    return cmds.listRelatives(obj, s=True, ni=skip, path=True)

def get_parent(obj, all=False):
    """ get parents for given objects


    :param obj: 'str' object
    :param all: 'bool' True: get all parents in hierarchy
    :return: 'list' with parents or []
    """
    if not all:
        return cmds.listRelatives(obj, p=True, shapes=False, path=True)

    if all:
        return get_top_parent(obj)


def object_type(obj):
    shapes = get_shapes(obj)
    if not shapes:
        return cmds.objectType(obj)

    return cmds.objectType(shapes[0])

def get_top_parent(obj):
    parent = cmds.listRelatives(obj, ap=True, shapes=False, path=True)
    if not parent:
        return obj
    return get_top_parent(parent[0])


def get_all_parent(obj, parents=[]):
    parent = cmds.listRelatives(obj, ap=True, shapes=False, path=True)
    if not parent:
        parents.append(obj)
        return parents

    parents.append(obj)
    return get_top_parent(parent[0])
