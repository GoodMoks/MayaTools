from PySide2 import QtWidgets
import maya.OpenMayaUI as omui
import shiboken2
import re


def convert_pymel_to_qt(maya_widget):
    ptr = omui.MQtUtil.findControl(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findLayout(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findMenuItem(maya_widget)
    if not ptr:
        ptr = omui.MQtUtil.findWindow(maya_widget)

    if not ptr:
        return None
    match = re.search(r"'(\w+)", str(ptr))
    type_obj = match.group(1)

    return shiboken2.wrapInstance(long(ptr), getattr(QtWidgets, type_obj))


def convert_qt_to_pymel(widget):
    return omui.MQtUtil.fullName(long(shiboken2.getCppPointer(widget)[0]))
