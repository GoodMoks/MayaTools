import maya.cmds as cmds
from MayaTools.core.logger import logger
import MayaTools.core.dag as dag
import MayaTools.core.curve as curve
import MayaTools.tools.controls.controls_shape as shapeee
reload(shapeee)
import maya.api.OpenMaya as om2
from MayaTools.core.logger import logger

class CurveShape(object):
    def __init__(self):
        self.point = None
        self.degree = None
        self.periodic = None
        self.knot = None

    @logger
    def __add(self, point, degree, periodic, knot):
        if not isinstance(point, list):
            raise TypeError('Point must be list: [[0, 0, 0], [0, 0, 0], [0, 0, 0], ...]')

        if not isinstance(degree, int):
            raise TypeError('Degree must be integer')

        if not isinstance(periodic, int):
            raise TypeError('Periodic must be integer')

        if not isinstance(point, list):
            raise TypeError('Knot must be list: [0, 1, 2, 3, 4, 5, ...]')

        if len(point) + 1 <= degree:
            raise ValueError('Points must be 1 more than the degree')

        self.point = point
        self.degree = degree
        self.periodic = periodic
        self.knot = knot

    @logger
    def add_control(self, control):
        shape = dag.get_shapes(control)
        if not shape:
            raise ValueError('{} has no shape'.format(control))

        if not cmds.nodeType(shape[0]) == 'nurbsCurve':
            raise TypeError('{} not nurbsCurve'.format(control))

        point = cmds.getAttr("{0}.cv[*]".format(shape[0]))
        degree = cmds.getAttr("{0}.degree".format(shape[0]))
        periodic = cmds.getAttr("{0}.form".format(shape[0]))
        knot = curve.get_curve_knots(control)

        self.__add(point, degree, periodic, knot)

    def get_data(self):
        return dict(
            knot=self.knot,
            point=self.point,
            degree=self.degree,
            periodic=self.periodic
        )

    @logger
    def add_data(self, data):
        self.__add(data['point'], data['degree'],
                   data['periodic'], data['knot'])

    @logger
    def add_shape(self, point, degree, periodic=0, knot=None):
        if periodic and not knot:
            knot = []

        self.__add(point, degree, periodic, knot)

class Curve(object):
    def __init__(self, shape):
        self.shape = shape

        if not isinstance(shape, CurveShape):
            raise TypeError('Argument must be of instance class "{}"'.format(shape.CurveShape.__name__))

        self.name = 'NewCurve'

        self.knot = self.shape.knot
        self.point = self.shape.point
        self.degree = self.shape.degree
        self.periodic = self.shape.periodic

        self.curve = None

    def __create_curve(self):
        point = self.point + self.point[:self.degree] if self.periodic else self.point
        self.curve = cmds.curve(degree=self.degree, knot=self.knot, point=point,
                                periodic=self.periodic, name=self.name)

    def create(self, name=None):
        self.name = name if name else self.name
        self.__create_curve()
        return self.curve



class ControlManager(object):
    def __init__(self):
        pass


    @staticmethod
    def create(type, name=None):
        controls_data = shapeee.ControlShape()
        shape_data = controls_data.get_shape(type)
        shape = CurveShape()
        shape.add_data(shape_data)
        curve_main = Curve(shape)
        if not name:
            name = type
        curve_node = curve_main.create(name=name)
        return curve_node

    @staticmethod
    def export(control):
        shape = CurveShape()
        shape.add_control(control)
        shape_data = shapeee.ControlShape()
        shape_data.add_shape(key=control, value=shape.get_data(), override=True)
        om2.MGlobal.displayInfo('Export {}'.format(control))


def export_all():
    selected = cmds.ls(sl=True)
    if selected:
        for s in selected:
            ControlManager.export(s)
            om2.MGlobal.displayInfo(s)