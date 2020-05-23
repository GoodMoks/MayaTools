import maya.cmds as cmds
import maya.api.OpenMaya as om2
import time

""" Module for other useful functions """


def create_goal(obj, base_name, prefix=None, w=0.5):
    """ create particle and apply goal

    :param obj: str(obj)
    :param base_name: str(base_name) name of main object
    :param prefix: 'str' prefix to end name particle
    :param w: weight goal
    :return: locator, particle
    """
    if prefix:
        base_name = '{}_{}'.format(base_name, prefix)
    pos = cmds.xform(obj, piv=True, q=True, ws=True)
    if not cmds.objExists('{}_particle'.format(base_name)):
        particle = cmds.particle(p=[0, 0, 0], n='{}_particle'.format(base_name))[0]
        cmds.xform(particle, t=pos)
        cmds.setAttr('{}.particleRenderType'.format(particle), 4)
        cmds.goal(particle, g=obj, w=w)
        if not cmds.objExists('{}_goal_transform'.format(base_name)):
            goal_transform = cmds.spaceLocator(n='{}_goal_transform'.format(base_name))
            cmds.connectAttr('{}.worldCentroid'.format(particle), '{}.t'.format(goal_transform))
            return [goal_transform, particle]
        else:
            om2.MGlobal.displayError('{}_goal_transform already_exists'.format(base_name))
    else:
        om2.MGlobal.displayError('{}_particle already exists'.format(base_name))


def time_info(func):
    """Decorator to track the time

    Args: func: [function for decorate]
    Returns: [func]
    """

    def timeRun(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print 'Time: {}'.format(end - start)

        return result

    return timeRun


def create_follicle(name):
    """ create follicle
    :param name: 'str' name for follicle
    :return: (follicle, follicle_shape)
    """
    follicle = cmds.createNode('transform', n=name)
    follicle_shape = cmds.createNode('follicle', n='{}Shape'.format(follicle), p=follicle)
    cmds.connectAttr('{}.outTranslate'.format(follicle_shape), '{}.translate'.format(follicle))
    cmds.connectAttr('{}.outRotate'.format(follicle_shape), '{}.rotate'.format(follicle))
    cmds.setAttr('{}.inheritsTransform'.format(follicle), 0)
    return follicle, follicle_shape
