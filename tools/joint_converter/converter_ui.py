import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.tools.joint_converter.converter as converter

reload(converter)

class JointConverterUI(object):
    MAIN_NAME = 'ConvertJoint'

    def __init__(self):
        self.showUI()

    def showUI(self):
        if pm.window(self.MAIN_NAME, exists=True):
            pm.deleteUI(self.MAIN_NAME)

        with pm.window(self.MAIN_NAME, s=False, rtf=True, t='Convert Joint',
                       ds=True, wh=(200, 100), tlb=True) as self.main:
            with pm.verticalLayout():
                with pm.horizontalLayout():
                    self.joint_float = pm.floatFieldGrp(numberOfFields=1, label='Joint', value1=1,
                                                        cal=((1, "left"), (2, "left")),
                                                        cw=([1, 30], [2, 50]))
                    self.middle_float = pm.floatFieldGrp(numberOfFields=1, label='Middle', value1=1,
                                                         cal=((1, "left"), (2, "left")),
                                                         cw=([1, 40], [2, 50]))
                with pm.autoLayout(orientation='horizontal', spacing=2, reversed=False, ratios=None):
                    pm.button('Convert', c=pm.Callback(self.convert))

    def convert(self):
        selected = cmds.ls(sl=True)
        if not selected:
            om2.MGlobal.displayError('Nothing selected\nPlease selected root joint')

        joint_radius = self.joint_float.getValue()[0]
        middle_radius = self.middle_float.getValue()[0]
        converter.JointConverter(selected[0], joint_radius=joint_radius, middle_radius=middle_radius)