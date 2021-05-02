from PySide2 import QtWidgets
import maya.OpenMayaUI as omui
import shiboken2
import re


def convert_pymel_to_qt(maya_widget, type_obj=None):
    ptr = omui.MQtUtil.findControl(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findLayout(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findMenuItem(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findWindow(maya_widget)

    if not ptr:
        return None

    if not type_obj:
        match = re.search(r"'(\w+)", str(ptr))
        type_obj = match.group(1)


    return shiboken2.wrapInstance(int(ptr), getattr(QtWidgets, type_obj))


def convert_qt_to_pymel(widget):
    return omui.MQtUtil.fullName(int(shiboken2.getCppPointer(widget)[0]))


def get_maya_main_window():

    """

    Get the main Maya window as a QtGui.QMainWindow instance

    :return: QtGui.QMainWindow instance of the top level Maya windows

    """
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)