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
