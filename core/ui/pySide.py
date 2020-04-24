from shiboken2 import getCppPointer
import maya.OpenMayaUI as omui


def get_maya_control(widget):
    """ convert pySide widgets to maya object

    :param widget: pySide object
    :return: maya object
    """
    return omui.MQtUtil.fullName(long(getCppPointer(widget)[0]))