import pymel.core as pm

''' Module for work with vector, distance, etc. '''

def get_distance(source, target):
    """ get distance between 2 objects

    :param source:
    :param target:
    :return: length distance
    """
    source_v = source.getTranslation(space="world")
    target_v = target[0].getTranslation(space="world")

    vector = source_v - target_v

    return vector.length()

def getDistance(v0, v1):
    v = v1 - v0

    return v.length()