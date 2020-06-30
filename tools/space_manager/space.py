import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
import MayaTools.core.attribute as attribute
from MayaTools.core.logger import logger
import MayaTools.core.constraint as constraint


class Space(object):
    CTRL = 'Loc'
    BLEND_ATTR = 'Blend'

    def __init__(self, targets, driven, offset=True):
        self.targets = targets
        self.driven = driven
        self.offset = True

        self.reverse_node = None

        self.smooth = True
        if len(self.targets) > 2:
            self.smooth = False

        print self.targets, 'targets'
        print self.driven, 'driven'

        self.build()

    @logger
    def build(self):
        self.add_attr()
        self.connect()

    @logger
    def connect(self):
        self.apply_parentConstraint()
        self.reverse_node = cmds.createNode('reverse', n='{}_blend_rev'.format(self.driven))
        cmds.connectAttr('{}.{}'.format(self.CTRL, self.BLEND_ATTR),
                         '{}.inputX'.format(self.reverse_node))
        cmds.connectAttr('{}.outputX'.format(self.reverse_node),
                         '{}.{}W1'.format(self.parentConstraint[0], self.targets[1]))
        cmds.connectAttr('{}.{}'.format(self.CTRL, self.BLEND_ATTR),
                         '{}.{}W0'.format(self.parentConstraint[0], self.targets[0]))

    @logger
    def add_attr(self):
        if self.smooth:
            self.add_float_attr()

    @logger
    def add_float_attr(self):
        if not attribute.has_attr(self.CTRL, self.BLEND_ATTR):
            print 'add attr'
            cmds.addAttr(self.CTRL, ln=self.BLEND_ATTR, k=True)

    @logger
    def add_int_attr(self):
        pass

    @logger
    def add_enum_attr(self):
        pass

    @logger
    def apply_parentConstraint(self, translate=True, rotate=True):
        skip_translate = [] if translate else ["x", "y", "z"]
        skip_rotate = [] if rotate else ["x", "y", "z"]
        self.parentConstraint = cmds.parentConstraint(self.targets, self.driven,
                                                      skipTranslate=skip_translate,
                                                      skipRotate=skip_rotate, mo=self.offset)
