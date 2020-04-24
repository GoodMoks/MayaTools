import re
from maya.OpenMaya import MGlobal
import pymel.core as pm
import MayaTools.core.connections as connections
import MayaTools.core.base as base


class FitObjects(object):
    """ class for create fit locators on joints """

    @staticmethod
    def get_skinCluster(obj):
        return base.get_history(obj, type='skinCluster')

    @staticmethod
    def get_index_common_connections(obj1, obj2, attr):
        common_con = connections.get_common_connections(obj1, obj2, attr=attr)
        if common_con:
            return re.findall('[0-9]+', common_con[0])[0]

    def __init__(self, joints, geo):
        self.joints = joints
        self.geo = geo
        self.skinCluster = None
        self.build()

    def build(self):
        self.skinCluster = self.get_skinCluster(self.geo)[0]
        if not self.skinCluster:
            MGlobal.displayError('{} since it is not a skinned object'.format(self.geo))
            return False

        fit_locators = []
        fit_joints = []

        self.mesh_fit_grp = '{}_fit_grp'.format(self.geo)
        if not pm.objExists(self.mesh_fit_grp):
            self.mesh_fit_grp = pm.createNode('transform', n=self.mesh_fit_grp)

        for joint in self.joints:
            bindPreMatrixIndex = self.get_index_common_connections(joint, self.skinCluster, attr='worldMatrix')
            if not bindPreMatrixIndex:
                continue

            # get connected bindPreMatrix data
            joint_worldMarix = pm.getAttr('{}.worldMatrix'.format(joint))
            bindPreMatrix = pm.getAttr('{}.bindPreMatrix[{}]'.format(self.skinCluster, bindPreMatrixIndex))

            fit_joints.append(joint)

            loc = pm.spaceLocator(n='{}_fit_loc'.format(joint))

            loc.setMatrix((joint_worldMarix * bindPreMatrix * joint_worldMarix))
            pm.parent(loc, self.mesh_fit_grp)
            fit_locators.append(loc)

            mult_node = pm.createNode('multMatrix', n='{}_fit_multMatrix'.format(joint))

            loc_inverseWorldMatrix = pm.getAttr('{}.worldInverseMatrix'.format(joint))
            pm.setAttr('{}.matrixIn[0]'.format(mult_node), loc_inverseWorldMatrix)
            pm.connectAttr('{}.worldMatrix'.format(loc), '{}.matrixIn[1]'.format(mult_node))
            pm.setAttr('{}.matrixIn[2]'.format(mult_node), loc_inverseWorldMatrix)

            mult_node.matrixSum.connect('{}.bindPreMatrix[{}]'.format(self.skinCluster, bindPreMatrixIndex))

        for loc, joint in zip(fit_locators, self.joints):
            parent_joint = joint.getParent()
            if parent_joint in self.joints:
                pm.parent(loc, '{}_fit_loc'.format(parent_joint))




