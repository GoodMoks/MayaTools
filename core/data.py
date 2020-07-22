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
            if not self.__check_file_exist():
                om2.MGlobal.displayError('The file is not json: {}'.format(self.file_path))
                return False

            om2.MGlobal.displayError('file does not exist: {}'.format(self.file_path))
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
