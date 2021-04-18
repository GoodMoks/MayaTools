import maya.cmds as cmds
import MayaTools.core.curve as curve
import MayaTools.core.utils as utils
from collections import namedtuple
import enum

_ = namedtuple('VectorAxis', ['vector', 'axis', 'angle'])

class ShapeAngle(enum.Enum):
    pos_x = _('+', 'X', [0, 0, -90])
    pos_y = _('+', 'Y', [0, 0, 0])
    pos_z = _('+', 'Z', [90, 0, 0])
    neg_x = _('-', 'X', [0, 0, 90])
    neg_y = _('-', 'Y', [0, 0, 180])
    neg_z = _('-', 'Z', [-90, 0, 0])

class ControlCurve(object):
    def __init__(self, control, name=None, size=None,
                 matrix=None, align=None, scale=False,
                 world=True, suffix='_CTRL', align_name=True,
                 color=None, aim='Y', vector='+'):
        self.name = name
        self.control = control
        self.size = size
        self.matrix = matrix
        self.align = align
        self.scale = scale
        self.world = world
        self.prefix = suffix
        self.align_name = align_name
        self.color = color
        self.aim = aim
        self.vector = vector

        self.curve = None
        self.shape = None

        self.check_arguments()

    def check_arguments(self):
        if self.name and not isinstance(self.name, str):
            raise TypeError('Name must be a string')

        if not isinstance(self.control, str):
            raise TypeError('Control type must be a string')

        if self.align and not isinstance(self.align, str):
            raise TypeError('Align object must be a string')

        if self.align and not cmds.objExists(self.align):
            raise TypeError('{} does not exist'.format(self.align))

        if self.scale and not isinstance(self.scale, bool):
            raise TypeError('Scale must be a True or False')

        if self.world and not isinstance(self.world, bool):
            raise TypeError('World must be a True or False')

        if not isinstance(self.prefix, str):
            raise TypeError('Prefix must be a string')

        if self.align_name and not isinstance(self.align_name, bool):
            raise TypeError('Align name must be a True or False')

        if not isinstance(self.aim, str):
            raise TypeError('Aim axis type must be a string')

        if not isinstance(self.vector, str) or self.vector not in ['-', '+']:
            raise TypeError('Vector type must be a string and be plus or minus')

    def create(self):
        cmds.undoInfo(openChunk=True)

        self.add_prefix(prefix=self.prefix)

        new_curve = curve.CurveManager.create(curve_type=self.control, name=self.name)
        if not new_curve:
            return False

        self.curve, self.shape = new_curve

        if self.size:
            self.set_scale_shape(size=self.size)

        if self.matrix or self.align:
            if self.matrix and not self.align:
                self.set_matrix(matrix=self.matrix)

            if not self.matrix and self.align:
                self.align_object(align=self.align)

        if self.color:
            utils.ColorObject(obj=self.curve, color=self.color)

        self.aim_axis_shape(vector=self.vector, axis=self.aim)

        cmds.undoInfo(closeChunk=True)

        return new_curve

    def add_prefix(self, prefix):
        name = None
        if self.name:
            name = self.name

        if self.align and self.align_name:
            name = self.align

        if not name:
            name = self.control

        self.name = name + prefix

    def set_matrix(self, matrix):
        cmds.xform(self.curve, m=matrix)
        if self.scale:
            cmds.makeIdentity(self.curve, a=True, scale=True)

    def set_scale_shape(self, size):
        cmds.scale(size, size, size, '{}.cv[*]'.format(self.curve))

    def set_rotate_shape(self, angle):
        cmds.rotate(angle[0], angle[1], angle[2], '{}.cv[*]'.format(self.curve))

    def aim_axis_shape(self, vector, axis):
        for obj in ShapeAngle:
            if vector in obj.value.vector:
                if axis in obj.value.axis:
                    self.set_rotate_shape(angle=obj.value.angle)

    def align_object(self, align):
        matrix = cmds.xform(align, q=True, ws=self.world, matrix=True)
        self.set_matrix(matrix)
