import os
import json
import maya.api.OpenMaya as om2


class JsonData(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self._data = None

        self.__read()

    def __write(self, data):
        if self.__check_file_exist:
            try:
                with open(self.file_path, 'w') as f:
                    self.shapes = json.dump(data, f, indent=6)
            except Exception:
                om2.MGlobal.displayError('Failed write data in file: {}'.format(self.file_path))
                om2.MGlobal.displayError('{}'.format(Exception))

    def __read(self):
        if self.__check_file_exist():
            try:
                with open(self.file_path, 'r') as f:
                    self._data = json.load(f)
            except Exception:
                om2.MGlobal.displayError('Failed read file: {}'.format(self.file_path))
                om2.MGlobal.displayError('{}'.format(Exception))

    def __check_file_exist(self):
        if not os.path.exists(self.file_path):
            om2.MGlobal.displayError('file does not exist: {}'.format(self.file_path))
            return False

        if not self.__check_file_extension():
            om2.MGlobal.displayError('The file is not json: {}'.format(self.file_path))
            return False

        return True

    def __check_file_extension(self):
        file_ext = os.path.splitext(self.file_path)[1]
        if not file_ext == '.json':
            return False
        return True

    def write_data(self, data):
        self.__write(data)

    def read_data(self):
        self.__read()
        return self._data


class CurveShapeData(JsonData):
    # FILE_NAME = 'control_manager.json'
    # FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

    FILE_PATH = 'E:\Work\Pipeline\Projects\Tools\MayaTools\data\controls.json'

    def __init__(self):
        super(CurveShapeData, self).__init__(self.FILE_PATH)
        self.shapes = self._data if self._data else {}

    def get_all_shapes(self):
        return self.shapes

    def get_shape(self, name):
        if self.__check_exist_shape(name):
            return self.shapes[name]

    def __check_exist_shape(self, name):
        if self.shapes:
            if name not in self.shapes:
                om2.MGlobal.displayError('The shape {} does not exist in the database'.format(name))
                return False

            return True

    def edit_shape(self, name, key=None, value=None):
        all_shapes = self.get_all_shapes()
        if self.__check_exist_shape(name):
            if value:
                if not value == all_shapes[name]:
                    all_shapes[name] = value

            if key:
                if not name == key:
                    all_shapes[key] = all_shapes.pop(name)

        self.write_data(all_shapes)
        self.update()

    def delete_shape(self, name):
        all_shapes = self.get_all_shapes()
        if self.__check_exist_shape(name):
            del all_shapes[name]

        self.write_data(all_shapes)
        self.update()

    def add_shape(self, key, value, overwrite=False):
        all_shapes = self.get_all_shapes()
        if all_shapes.has_key(key):
            if not overwrite:
                return

        all_shapes[key] = value

        self.write_data(all_shapes)
        self.update()

    def update(self):
        self.shapes = self.read_data()
