import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.api.OpenMaya as om2

""" Module for work with transform """


def align_transform(source, target, t=True, ro=True):
    """ align transform constraint method

    :param source:
    :param target:
    :param t:
    :param ro:
    :return:
    """
    if t:
        pm.delete(pm.pointConstraint(source, target, mo=False))
    if ro:
        pm.delete(pm.orientConstraint(source, target, mo=False))


def get_rotate_pivot(obj):
    """ get world space position of rotate pivot method

    :param obj: dag path
    :return: MVector
    """
    transform_fn = om.MFnTransform(obj)
    rotate_pivot = transform_fn.rotatePivot(om.MSpace.kWorld)
    return om.MVector(rotate_pivot.x, rotate_pivot.y, rotate_pivot.z)

