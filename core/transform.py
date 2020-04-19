import pymel.core as pm

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




