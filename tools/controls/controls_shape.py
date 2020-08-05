import os
import maya.api.OpenMaya as om2
from MayaTools.core.logger import logger
import MayaTools.core.data as data


class ControlShape(data.JsonData):
    FILE_NAME = 'controls.json'
    FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

    @logger
    def __init__(self):
        print self.FILE_PATH
        super(ControlShape, self).__init__(self.FILE_PATH)
        self.shapes = self._data if self._data else {}

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
    def edit_shape(self, name, key=None, value=None):
        all_shapes = self.get_all_shapes()

        if self.__check_exist_shape(name):
            if value:
                if not value == all_shapes[name]:
                    all_shapes[name] = value

            if key:
                if not name == key:
                    all_shapes[key] = all_shapes.pop[name]

        self.write_data(all_shapes)
        self.update()

    @logger
    def delete_shape(self, names):
        if isinstance(names, basestring):
            names = [names]

        all_shapes = self.get_all_shapes()

        for name in names:
            if self.__check_exist_shape(name):
                del all_shapes[name]

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
