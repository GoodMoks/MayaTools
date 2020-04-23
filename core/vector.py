import pymel.core as pm
import MayaTools.core.base as base

''' Module for work with vector, distance, etc. '''

def get_distance(source, target):
    """ get distance between 2 objects

    :param source:
    :param target:
    :return: length distance
    """
    if not base.is_pymel(source):
        source = pm.PyNode(source)
    if not base.is_pymel(target):
        target = pm.PyNode(target)
    source_v = source.getTranslation(space="world")
    target_v = target.getTranslation(space="world")

    vector = source_v - target_v

    return vector.length()

def getDistance(v0, v1):
    v = v1 - v0

    return v.length()