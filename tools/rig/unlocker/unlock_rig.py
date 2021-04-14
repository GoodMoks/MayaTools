import maya.cmds as cmds
import MayaTools.core.attribute as attribute
import MayaTools.core.utils as utils
import MayaTools.core.connections as connections
import MayaTools.core.layers as layers






@utils.time_info
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
        sel = cmds.ls(sl=True)
        if sel:
            return sel[0]

    @staticmethod
    def set_joint_draw_style(obj, state):
        try:
            cmds.setAttr(obj + '.drawStyle', state)
        except:
            pass

    def __init__(self):
        self.build()

    def build(self):
        obj = self.get_selected()
        if obj:
            child = cmds.listRelatives(obj, ad=True)
            print len(child)
            if child:
                child.append(obj)
                for index, c in enumerate(child):
                    try:
                        attribute.unlock_attr(c, self.MAIN_ATTR)
                    except:
                        pass
                    try:
                        connections.break_input_connections(c, attr='.visibility')
                    except:
                        pass
                    try:
                        layers.enabled_layer(c, 0)
                    except:
                        pass
                    try:
                        self.visibility_attr(c)
                    except:
                        pass

            cmds.confirmDialog(title='Notification', message='DONE',
                               button=['OK'])

    def visibility_attr(self, obj):
        shape = cmds.listRelatives(obj, s=True)
        if shape:
            for shape in shape:
                obj.append(shape)

        if len(obj) and isinstance(obj, basestring):
            objects = list(obj)

        for o in objects:
            if cmds.objectType(o) == 'joint':
                try:
                    cmds.setAttr(o + '.drawStyle', 0)
                except:
                    pass

            for attr, value in self.SHAPE_ATTR.iteritems():
                try:
                    cmds.setAttr('{}.{}'.format(o, attr), value)
                except:
                    pass
