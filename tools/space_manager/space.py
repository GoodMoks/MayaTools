import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
import MayaTools.core.attribute as attribute
from MayaTools.core.logger import logger
import MayaTools.core.constraint as constraint


class SpaceFloat(object):
    CTRL = 'Loc'
    BLEND_ATTR = 'Blend'

    def __init__(self, targets, driven, offset=True):
        self.targets = targets
        self.driven = driven
        self.offset = offset

        self.reverse_node = None

        self.smooth = True
        if len(self.targets) > 2:
            self.smooth = False

        print self.targets, 'targets'
        print self.driven, 'driven'

        self.build()

    @logger
    def build(self):
        # smooth ---------
        # self.add_attr()
        # self.connect_float()

        # enum ---------
        self.connect_enum()

    @logger
    def connect_enum(self):
        self.apply_parentConstraint()

        self.add_enum_attr()
        for index, target in enumerate(self.targets):
            logic_node = cmds.createNode('floatLogic', n='{}_logic'.format(target))
            cmds.setAttr('{}.floatB'.format(logic_node), index)
            cmds.connectAttr('{}.{}'.format(self.CTRL, self.BLEND_ATTR), '{}.floatA'.format(logic_node))
            cmds.connectAttr('{}.outBool'.format(logic_node),
                             '{}.{}W{}'.format(self.parentConstraint[0], self.targets[index], index))

    @logger
    def connect_float(self):
        self.apply_parentConstraint()
        self.reverse_node = cmds.createNode('reverse', n='{}_blend_rev'.format(self.driven))
        cmds.connectAttr('{}.{}'.format(self.CTRL, self.BLEND_ATTR),
                         '{}.inputX'.format(self.reverse_node))
        cmds.connectAttr('{}.outputX'.format(self.reverse_node),
                         '{}.{}W1'.format(self.parentConstraint[0], self.targets[1]))
        cmds.connectAttr('{}.{}'.format(self.CTRL, self.BLEND_ATTR),
                         '{}.{}W0'.format(self.parentConstraint[0], self.targets[0]))

    @logger
    def add_attr(self, int=False):
        if self.smooth:
            self.add_float_attr()
            return

        if int:
            self.add_int_attr()
            return

        self.add_enum_attr()

    @logger
    def add_float_attr(self):
        if not attribute.has_attr(self.CTRL, self.BLEND_ATTR):
            cmds.addAttr(self.CTRL, ln=self.BLEND_ATTR, k=True)

    @logger
    def add_int_attr(self):
        pass

    @logger
    def add_enum_attr(self):
        if not attribute.has_attr(self.CTRL, self.BLEND_ATTR):
            cmds.addAttr(self.CTRL, ln=self.BLEND_ATTR, enumName=':'.join(self.targets), k=True, attributeType='enum')

    @logger
    def apply_parentConstraint(self, translate=True, rotate=True):
        skip_translate = [] if translate else ["x", "y", "z"]
        skip_rotate = [] if rotate else ["x", "y", "z"]
        self.parentConstraint = cmds.parentConstraint(self.targets, self.driven,
                                                      skipTranslate=skip_translate,
                                                      skipRotate=skip_rotate, mo=self.offset)





class SpaceController(object):
    def __init__(self, targets, driven, ctrl, attr_name, offset=True, ):
        self.targets = targets
        self.driven = driven
        self.offset = offset



