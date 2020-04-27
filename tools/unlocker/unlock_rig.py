import pymel.core as pm
import MayaTools.core.attribute as attribute
import MayaTools.core.connections as connections
import MayaTools.core.layers as layers


"""
import MayaTools.tools.unlocker.unlock_rig as unlock
reload(unlock)
unlock.UnlockRig()
"""

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
        sel = pm.selected()
        if sel:
            return sel[0]

    @staticmethod
    def set_joint_draw_style(obj, state):
        try:
            pm.setAttr(obj + '.drawStyle', state)
        except:
            pass

    def __init__(self):
        self.build()

    def build(self):
        obj = self.get_selected()
        if obj:
            child = pm.listRelatives(obj, ad=True)
            if child:
                child.append(obj)
                for c in child:
                    try:
                        attribute.unlock_attr(child, self.MAIN_ATTR)
                        connections.break_input_connections(child, attr='.visibility')
                        layers.enabled_layer(child, 0)
                        self.visibility_attr(c)
                    except:
                        pass

            pm.confirmDialog(title='Notification', message='DONE',
                             button=['OK'])

    def visibility_attr(self, obj):
        shape = pm.listRelatives(obj, s=True)
        if shape:
            for shape in shape:
                obj.append(shape)

        if len(obj) and isinstance(obj, basestring):
            objects = list(obj)

        for o in objects:
            if pm.objectType(o) == 'joint':
                try:
                    pm.setAttr(o + '.drawStyle', 0)
                except:
                    pass

            for attr, value in self.SHAPE_ATTR.iteritems():
                try:
                    pm.setAttr('{}.{}'.format(o, attr), value)
                except:
                    pass
