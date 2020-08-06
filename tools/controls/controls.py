import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.data as data
import MayaTools.core.curve as curve
reload(data)
reload(curve)

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
    def export(control, overwrite=True):
        shape = curve.CurveShape()
        shape.add_control(control)
        shape_data = data.ShapeData()
        shape_data.add_shape(key=control, value=shape.get_data(), overwrite=overwrite)
        om2.MGlobal.displayInfo('Export {}'.format(control))

    @staticmethod
    def delete(control):
        shape_data = data.ShapeData()
        shape_data.delete_shape(control)


def export_all():
    selected = cmds.ls(sl=True)
    if selected:
        for s in selected:
            ControlManager.export(s)
            om2.MGlobal.displayInfo(s)
