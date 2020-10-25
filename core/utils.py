import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.dag as dag
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


def chunk_decorator(func):
    cmds.undoInfo(openChunk=True)

    def function(*func_args, **func_kwargs):
        return func(*func_args, **func_kwargs)

    cmds.undoInfo(closeChunk=True)
    return function


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

def get_joint_display_scale(joint):
    joint_scale = cmds.jointDisplayScale(query=True)
    joint_radius = cmds.getAttr('{}.radius'.format(joint))
    return joint_radius * joint_scale

def get_value_range(count, max=1):
    coefficient = max / float(count-1)

    return [round(x * coefficient, 5) for x in xrange(count)]

def matrix_round_pymel(matrix, digits):
    for first_index in xrange(4):
        for second_index in xrange(4):
            old = getattr(matrix, 'a{}{}'.format(first_index, second_index))
            setattr(matrix, 'a{}{}'.format(first_index, second_index), round(old, digits))

    return matrix

def numbers_list_round(matrix, digits):
    for index in xrange(len(matrix)):
        matrix[index] = round(matrix[index], digits)

    return matrix

def recompose_matrix(matrix):
    return list([data for data in matrix])


class ColorObject(object):
    @staticmethod
    def set_color_rgb(obj, attr, color):
        for channel, color in zip(("R", "G", "B"), color):
            cmds.setAttr('{}.{}{}'.format(obj, attr, channel), color)

    def __init__(self, obj, color=None, shape=True, transform=False, outliner=False):
        self.obj = obj
        self.color = color
        self.outliner = outliner
        self.shape = shape
        self.transform = transform

        self.check_arguments()

        self.shapes = dag.get_shapes(self.obj)
        self.set_color()

    def check_arguments(self):
        if not isinstance(self.obj, basestring):
            raise AttributeError('Object must be a string')

        if not cmds.objExists(self.obj):
            raise AttributeError('{} does not exist'.format(self.obj))

        if not cmds.listRelatives(self.obj):
            raise AttributeError('{} is not dag object'.format(self.obj))

        if not cmds.objectType(self.obj) == 'transform':
            raise AttributeError('Object must be a transform node')

        if not self.shape and not self.transform and not self.outliner:
            raise AttributeError('Specify one of the attributes: shape, transform or outliner')

    def apply_color(self, obj, color):
        cmds.setAttr('{}.overrideEnabled'.format(obj), True)
        cmds.setAttr('{}.overrideRGBColors'.format(obj), True)
        self.set_color_rgb(obj, 'overrideColor', color)

        if self.outliner:
            cmds.setAttr('{}.useOutlinerColor'.format(obj), True)
            self.set_color_rgb(obj, 'outlinerColor', color)

    def set_color(self, color=None):
        if not color:
            color = self.color

        if self.shape:
            for shape in self.shapes:
                self.apply_color(shape, color)

        if self.transform:
            self.apply_color(self.obj, color)

    def reset_color(self):
        if self.shape:
            for shape in self.shapes:
                cmds.setAttr("{0}.overrideEnabled".format(shape), False)

        if self.transform:
            cmds.setAttr("{0}.overrideEnabled".format(self.obj), False)