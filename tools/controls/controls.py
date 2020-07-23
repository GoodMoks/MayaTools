import os
import json
import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
from MayaTools.core.logger import logger
import MayaTools.core.data as data
import MayaTools.core.dag as dag


class ControlShape(data.JsonData):
    FILE_NAME = 'controls.json'
    FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

    def __init__(self):
        super(ControlShape, self).__init__(self.FILE_PATH)
        self.shapes = self._data

    @logger
    def get_all_shapes(self):
        return self.shapes

    @logger
    def get_shape(self, name):
        if self.__check_exist_shape(name):
            return self.shapes[name]

    @logger
    def __check_exist_shape(self, name):
        if self.shapes:
            if name not in self.shapes:
                om2.MGlobal.displayError('The shape {} does not exist in the database'.format(name))
                return False

            return True

    @logger
    def delete_shape(self, names):
        if isinstance(names, basestring):
            names = [names]

        all_shapes = self.get_all_shapes()

        for name in names:
            if self.__check_exist_shape(name):
                all_shapes.pop(name, None)

        self.write_data(all_shapes)
        self.update()

    @logger
    def add_shape(self, key, value, override=False):
        all_shapes = self.get_all_shapes()
        if all_shapes.has_key(key):
            if not override:
                return

        all_shapes[key] = value

        self.write_data(all_shapes)
        self.update()

    @logger
    def update(self):
        self.shapes = self.read_data()


class Shape(object):
    def __init__(self):
        self.point = None
        self.degree = None
        self.periodic = None

    @logger
    def add_control(self, control):
        shape = dag.get_shapes(control)
        if not shape:
            raise ValueError('{} has no shape'.format(control))

        if not cmds.nodeType(shape[0]) == 'nurbsCurve':
            raise TypeError('{} not nurbsCurve'.format(control))

        self.degree = cmds.getAttr("{0}.degree".format(shape[0]))
        self.point = cmds.getAttr("{0}.cv[*]".format(shape[0]))
        self.periodic = cmds.getAttr("{0}.form".format(shape[0]))

    def add_shape(self, point, degree, periodic):
        if not isinstance(point, list):
            om2.MGlobal.displayError('Point must be list: [[0, 0, 0], [0, 0, 0], [0, 0, 0]]')
            return

        self.point = point
        self.degree = degree
        self.periodic = periodic


class CurveShape(object):
    def __init__(self, shape):
        self.shape = shape

        self.name = None
        self.point = None
        self.degree = None
        self.knot = None
        self.periodic = None

        self.curve = None

        if not isinstance(shape, Shape):
            raise TypeError('Argument must be of instance class "{}"'.format(Shape.__name__))

        self.assign()

    def assign(self):
        self.point = self.shape.point
        self.degree = self.shape.degree
        self.periodic = self.shape.periodic

    def calculate(self):
        self.point = self.shape.point.extend[:self.shape.degree] if self.shape.periodic else self.shape.point
        self.knot = range(len(self.shape.point) + self.shape.degree - 1)

    def create_curve(self):
        self.curve = cmds.curve(degree=self.degree, knot=self.knot, point=self.point,
                                periodic=self.periodic, name=self.name)

    def create(self, name=None):
        self.name = name or 'NewCurve'

        self.calculate()
        self.create_curve()
        return self.curve


class Curve(object):
    def __init__(self, points, degree, periodic, name=None, matrix=None, parent=None):
        self.points = points
        self.degree = degree
        self.periodic = periodic
        self.name = name or 'NewCurve'
        self.matrix = matrix
        self.parent = parent

        self.knot = None
        self.curve = None

        self.create()

    def create(self):
        self.create_curve()
        if self.matrix:
            print 'add matrix'

        if self.parent:
            print 'add parent'

        return self.curve

    def create_curve(self):
        self.points = self.points.extend[:self.degree] if self.periodic else self.points
        self.knot = range(len(self.points) + self.degree - 1)

        self.curve = cmds.curve(degree=self.degree,
                                knot=self.knot,
                                point=self.points,
                                periodic=self.periodic,
                                name=self.name)


class ControlsController(object):
    def __init__(self):
        pass

    def create_control(self, name):
        shape = ControlShape()
        control_shape = shape.get_shape(name)
        if control_shape:
            print control_shape

    def export_control(self, curve):
        pass


def test():
    shape = ControlShape().get_shape('cube')
    curve = Curve(shape['point'], shape['degree'], shape['periodic'])
    curve.create()

# def createCurve(name='', control='circle'):
#     """ Creates NURBS curves
#
#     :param name: 'str' name object
#     :param control: 'str' shape of the curves
#     :return: 'str' new object
#     """
#     if isinstance(name, basestring) and isinstance(control, basestring):
#         baseDir = os.path.dirname(__file__)
#         nameFile = 'controls.json'
#         path = os.path.join(baseDir, nameFile)
#
#
#         with open(path) as f:
#             control = json.load(f)[control]
#
#         curve = cmds.curve(degree=control['degree'],
#                            knot=control['knot'],
#                            point=control['point'],
#                            periodic=control['periodic'])
#         if not name == '':
#             curve = cmds.rename(curve, name)
#
#         return curve
