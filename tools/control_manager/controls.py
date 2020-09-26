import maya.cmds as cmds
import MayaTools.core.curve as curve

reload(curve)


class ControlCurve(object):
    def __init__(self, control, name=None, size=None, matrix=None, align=None, scale=False, world=True):
        self.name = name
        self.control_type = control
        self.size = size
        self.matrix = matrix
        self.align = align
        self.scale = scale
        self.world = world

        self.curve = None
        self.shape = None

        self.check_arguments()
        self.create()

    def check_arguments(self):
        if self.name and not isinstance(self.name, basestring):
            raise TypeError('Name must be a string')

        if not isinstance(self.control_type, basestring):
            raise TypeError('Control type must be a string')

        if self.align and not isinstance(self.align, basestring):
            raise TypeError('Align object must be a string')

        if not cmds.objExists(self.align):
            raise AttributeError('{} does not exist'.format(self.align))

        if self.scale and not isinstance(self.scale, bool):
            raise AttributeError('Scale must be a True or False')

        if self.world and not isinstance(self.world, bool):
            raise AttributeError('World must be a True or False')

    def create(self):
        new_curve = curve.CurveManager.create(curve_type=self.control_type, name=self.name)
        if not new_curve:
            return False
        self.curve, self.shape = new_curve

        if self.size:
            self.set_scale_shape()

        if self.matrix and not self.align:
            self.set_matrix(matrix=self.matrix)

        if not self.matrix and self.align:
            self.align_object()

        return new_curve

    def set_matrix(self, matrix):
        cmds.xform(self.curve, m=matrix)
        if not self.scale:
            cmds.makeIdentity(self.curve, a=True, scale=True)

    def set_scale_shape(self):
        cmds.scale(self.size, self.size, self.size, '{}.cv[*]'.format(self.curve))

    def align_object(self):
        matrix = cmds.xform(self.align, q=True, ws=self.world, matrix=True)
        self.set_matrix(matrix)


def test():
    sel = cmds.ls(sl=True)
    if not sel:
        return

    sel = sel[0]

    ControlCurve(control='cube', align=sel, scale=False, world=True)
