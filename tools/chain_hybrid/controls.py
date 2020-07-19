import os
import json
import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
from MayaTools.core.logger import logger


class JsonData(object):
    def __init__(self, file=None):
        FILE_NAME = 'controls.json'
        FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

        self.file = FILE_PATH

        self.__data = None

        self.__read()

    @logger
    def __read(self):
        if self.__check_file_exist():
            try:
                with open(self.file, 'r') as f:
                    self.__data = json.load(f)
            except Exception:
                om2.MGlobal.displayError('Failed read file: {}'.format(self.file))
                om2.MGlobal.displayError('{}'.format(Exception))

    @logger
    def __check_file_extension(self):
        file_ext = os.path.splitext(self.file)[1]
        if not file_ext == '.json':
            return False
        return True

    @logger
    def __check_file_exist(self):
        if not os.path.exists(self.file):
            if not self.__check_file_exist():
                om2.MGlobal.displayError('The file is not json: {}'.format(self.file))
                return False

            om2.MGlobal.displayError('file does not exist: {}'.format(self.file))
            return False

        return True

    @logger
    def __write(self, data):
        if self.__check_file_exist:
            try:
                with open(self.file, 'w') as f:
                    self.controls = json.dump(data, f, indent=6)
            except Exception:
                om2.MGlobal.displayError('Failed write data in file: {}'.format(self.file))
                om2.MGlobal.displayError('{}'.format(Exception))

    @logger
    def get_data(self):
        return self.__data

    @logger
    def write_data(self, data):
        self.__write(data)

    @logger
    def read_data(self):
        self.__read()


json = JsonData()
print json.data


class ControlShape(object):
    FILE_NAME = 'controls.json'
    FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

    def __init__(self):
        self.controls = None

        self.__read_file()

    @logger
    def __read_file(self):
        if self.__check_exist_file():
            try:
                with open(self.FILE_PATH, 'r') as f:
                    self.controls = json.load(f)
            except:
                om2.MGlobal.displayError('Failed read file: {}'.format(self.FILE_PATH))

    @logger
    def get_shape(self, name):
        if self.__check_exist_shape(name):
            return self.controls[name]

    @logger
    def get_all_shapes(self):
        return self.controls

    @logger
    def __check_exist_file(self):
        if not os.path.exists(self.FILE_PATH):
            om2.MGlobal.displayError('file does not exist: {}'.format(self.FILE_PATH))
            return False
        return True

    @logger
    def __check_exist_shape(self, name):
        if self.controls:
            if name not in self.controls:
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

        self.__write_file(all_shapes)

    @logger
    def __write_file(self, data):
        if self.__check_exist_file:
            try:
                with open(self.FILE_PATH, 'w') as f:
                    self.controls = json.dump(data, f, indent=6)
            except:
                om2.MGlobal.displayError('Failed write data in file: {}'.format(self.FILE_PATH))

# shape = ControlShape()
# shape.delete_shape('cube')
# print shape.get_shape('cube')


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
