import maya.cmds as cmds
import maya.api.OpenMaya as om2


class UnlockRig(object):
    SHAPE_ATTR = {
        '.overrideEnabled': 1,
        '.overrideDisplayType': 0,
        '.overrideLevelOfDetail': 0,
        '.overrideShading': 1,
        '.overrideTexturing': 1,
        '.overridePlayback': 1,
        '.overrideVisibility': 1,
        '.visibility': 1,
        '.lodVisibility': 1,
        '.template': 0,
        '.hiddenInOutliner': 0,
        '.hideOnPlayback': 0}

    MAIN_ATTR = ['.tx', '.ty', '.tz',
                 '.rx', '.ry', '.rz',
                 '.sx', '.sy', '.sz',
                 '.visibility']

    @staticmethod
    def get_selected():
        sel = om2.MSelectionList()
        om2.MGlobal.getActiveSelectionList(sel)


    @staticmethod
    def set_joint_draw_style(obj, state):
        try:
            pm.setAttr(obj + '.drawStyle', state)
        except:
            pass

    def __init__(self):
        self.build()