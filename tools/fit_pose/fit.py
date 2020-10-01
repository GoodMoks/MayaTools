import pymel.core as pm
import maya.cmds as cmds
import MayaTools.core.connections as connections
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin

import MayaTools.tools.control_manager.controls as controls

class FitObjects(object):
    """ class for create fit locators on joints """
    PREFIX = '_Fit'
    def __init__(self, joints, geo):
        self.joints = joints
        self.geo = geo
        self.skinCluster = None

        self.fit_grp = None
        self.fit_objects = []

        self.build()

    def create_fit_grp(self):
        self.fit_grp = '{}_fit_grp'.format(self.geo)
        if not pm.objExists(self.fit_grp):
            self.fit_grp = cmds.createNode('transform', n=self.fit_grp)

    def restore_hierarchy(self):
        for loc, joint in zip(self.fit_objects, self.joints):
            parent_joint = dag.get_parent(joint)
            if parent_joint in self.joints:
                pm.parent(loc, '{}{}'.format(parent_joint, self.PREFIX))

    def build(self):
        self.create_fit_grp()
        self.skinCluster = skin.get_skinCluster(self.geo)[0]
        for joint in self.joints:
            index = connections.get_index_common_connections(joint, self.skinCluster, attr='worldMatrix')
            if not index:
                continue

            curve = controls.ControlCurve('sphere', name='{}'.format(joint), prefix=self.PREFIX)
            fit_object = pm.PyNode(curve.create()[0])
            self.fit_objects.append(fit_object)
            cmds.parent(str(fit_object), self.fit_grp)

            # get connected bindPreMatrix data
            joint_worldMarix = pm.getAttr('{}.worldMatrix'.format(joint))
            bindPreMatrix = pm.getAttr('{}.bindPreMatrix[{}]'.format(self.skinCluster, index))


            object_matrix = joint_worldMarix * bindPreMatrix * joint_worldMarix
            fit_object.setMatrix(object_matrix)

            mult_node = cmds.createNode('multMatrix', n='{}_fit_multMatrix'.format(joint))

            joint_worldInverseMatrix = cmds.getAttr('{}.worldInverseMatrix'.format(joint))
            cmds.setAttr('{}.matrixIn[0]'.format(mult_node), joint_worldInverseMatrix, type='matrix')
            cmds.connectAttr('{}.worldMatrix'.format(fit_object), '{}.matrixIn[1]'.format(mult_node))
            cmds.setAttr('{}.matrixIn[2]'.format(mult_node), joint_worldInverseMatrix, type='matrix')

            cmds.connectAttr('{}.matrixSum'.format(mult_node), '{}.bindPreMatrix[{}]'.format(self.skinCluster, index))

        self.restore_hierarchy()
