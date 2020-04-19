import pymel.core as pm
import MayaTools.core.shape as shape

""" Module for work with DAG hierarchy """

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
            return [c for c in child if not shape.isShape(c)]
        return child


def get_parent(obj, all=False):
    """ get parents for given objects


    :param obj: 'str' object
    :param all: 'bool' True: get all parents in hierarchy
    :return: 'list' with parents or []
    """

    return pm.listRelatives(obj, p=True, ap=all, shapes=False)
