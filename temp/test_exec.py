import pymel.core as pm
import maya.cmds as cmds
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import maya.OpenMayaUI as omui
import shiboken2
import MayaTools.core.ui.utils_qt as utils_qt

reload(utils_qt)

"""
import MayaTools.temp.test_exec as test
reload(test)

ui = test.TestWindow()
ui.showUI()

"""


def getMayaWindow():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)


class TestWindow(QtWidgets.QDialog):
    MAYA = getMayaWindow()

    def get_script_editor(self, python=False):
        pm.window()
        pm.columnLayout()
        executer = pm.cmdScrollFieldExecuter()
        if python:
            executer = pm.cmdScrollFieldExecuter(sourceType="python", commandCompletion=False, showTooltipHelp=False,
                                                 )

        qt_obj = utils_qt.convert_pymel_to_qt(executer, type_obj='QTextEdit')
        return executer, qt_obj

    @staticmethod
    def convert(executer):
        qt_obj = utils_qt.convert_pymel_to_qt(executer, type_obj='QTextEdit')
        return qt_obj

    def __init__(self, parent=MAYA):
        super(TestWindow, self).__init__(parent)
        self.build()

    def build(self):
        self.main_ly = QtWidgets.QHBoxLayout(self)
        self.editor_exec, self.editor_qt = self.get_script_editor(python=True)
        self.editor_qt.textChanged.connect(self.text_change)
        self.test_line = QtWidgets.QTextEdit()
        self.main_ly.addWidget(self.editor_qt)
        self.main_ly.addWidget(self.test_line)

    def text_change(self, *args):
        print(args)
        # if args[1] == 'k':
        #     return 0
        #
        # if not args[1] == 'k':
        #     return 1
        print(self.editor_exec.getText())

    def info(self):
        print('info')
        print(self.editor_exec.getText())

    @staticmethod
    def showUI():
        try:
            ui.close()
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = TestWindow()
        ui.show()
