import pymel.core as pm
import MayaTools.core.base as base
import MayaTools.core.transform as transform

''' Module for work with vector, distance, etc. '''


def get_distance(source, target):
    """ get distance between 2 objects

    :param source:
    :param target:
    :return: length distance
    """
    source_dg = base.get_dag_path(source)
    target_dg = base.get_dag_path(target)
    source_v = transform.get_rotate_pivot(source_dg)
    target_v = transform.get_rotate_pivot(target_dg)

    vector = source_v - target_v

    return vector.length()


def getDistance(v0, v1):
    v = v1 - v0

    return v.length()
