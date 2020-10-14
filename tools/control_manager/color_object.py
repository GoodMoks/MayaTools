import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2


class ColorObject(object):
    def __init__(self, obj, color=None, shape=False, transform=True, outliner=False, viewport=False):
        self.obj = obj
        self.color = color
        self.outliner = outliner
        self.viewport = viewport
        self.shape = shape
        self.transform = transform

        self.check_arguments()

    def check_arguments(self):
        if not isinstance(self.obj, basestring):
            raise AttributeError('Object must be a string')

        if not cmds.objExists(self.obj):
            raise AttributeError('{} does not exist'.format(self.obj))

        if not cmds.listRelatives(self.obj):
            raise AttributeError('{} is not dag object'.format(self.obj))


    def get_color(self, ):
        pass

    def set_color(self, color):
        pass

    def reset_color(self):
        pass


def get_color(node):
    """Get the color from shape node

    Args:
        node (TYPE): shape

    Returns:
        TYPE: Description
    """
    shp = node.getShape()
    if shp:
        if shp.overrideRGBColors.get():
            color = shp.overrideColorRGB.get()
        else:
            color = shp.overrideColor.get()

        return color


def set_color(node, color):
    """Set the color in the Icons.

    Arguments:
        node(dagNode): The object
        color (int or list of float): The color in index base or RGB.


    """
    # on Maya version.
    # version = mgear.core.getMayaver()

    if isinstance(color, int):

        for shp in node.listRelatives(shapes=True):
            shp.setAttr("overrideEnabled", True)
            shp.setAttr("overrideColor", color)
    else:
        for shp in node.listRelatives(shapes=True):
            shp.overrideEnabled.set(1)
            shp.overrideRGBColors.set(1)
            shp.overrideColorRGB.set(color[0], color[1], color[2])