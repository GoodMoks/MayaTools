import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.data as data
import MayaTools.core.curve as curve

class ControlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def create(type, name=None):
        controls_data = data.ShapeData()
        shape_data = controls_data.get_shape(type)
        shape = curve.CurveShape()
        shape.add_data(shape_data)
        curve_main = curve.Curve(shape)
        if not name:
            name = type
        curve_node = curve_main.create(name=name)
        return curve_node

    @staticmethod
    def export(control):
        shape = curve.CurveShape()
        shape.add_control(control)
        shape_data = data.ShapeData()
        shape_data.add_shape(key=control, value=shape.get_data(), override=True)
        om2.MGlobal.displayInfo('Export {}'.format(control))


def export_all():
    selected = cmds.ls(sl=True)
    if selected:
        for s in selected:
            ControlManager.export(s)
            om2.MGlobal.displayInfo(s)
