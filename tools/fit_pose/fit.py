import pymel.core as pm
import maya.cmds as cmds
import MayaTools.core.connections as connections
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin
import MayaTools.core.mesh as core_mesh
import MayaTools.tools.control_manager.controls as controls

reload(skin)
reload(connections)

class FitPose(object):
    PREFIX_GRP = '_fit_grp'

    @staticmethod
    def get_bindPreMatrix(geo):
        skinCluster = skin.get_skinCluster(geo)
        if skinCluster:
            return pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))

    @staticmethod
    def set_bindPreMatrix(matrix, geo):
        skinCluster = skin.get_skinCluster(geo)
        for index, m in enumerate(matrix):
            pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')


    def __init__(self, mesh, joints=None):
        self.mesh = mesh
        self.joints = joints

        self.check_arguments()

        if not self.joints:
            self.get_bind_joints()

        print 'init FitPose'

    def check_arguments(self):
        if not isinstance(self.mesh, basestring):
            raise AttributeError('Geo must be a string name of bind geometry')

        if not cmds.objExists(self.mesh):
            raise AttributeError('{} does not exist'.format(self.mesh))

        if not core_mesh.is_mesh(self.mesh):
            raise AttributeError('{} is not a polygon mesh'.format(self.mesh))

        if not skin.get_skinCluster(self.mesh):
            raise AttributeError('{} since it is not a skinned object'.format(self.mesh))

        if self.joints:
            if not isinstance(self.joints, list):
                raise AttributeError('Joints must be a list of joints')

            for joint in self.joints:
                if not cmds.objExists(joint):
                    raise AttributeError('{} does not exist'.format(joint))

    def get_bind_joints(self):
        joints = skin.get_influence_joint(self.mesh)
        if joints:
            self.joints = joints

    def update(self):
        if pm.objExists('{}{}'.format(self.mesh, self.PREFIX_GRP)):
            fit_grp = '{}{}'.format(self.mesh, self.PREFIX_GRP)

            matrix = self.get_bindPreMatrix(self.mesh)
            cmds.delete(fit_grp)
            self.set_bindPreMatrix(matrix, self.mesh)

    def reset(self):
        skinCluster = skin.get_skinCluster(self.mesh)
        bindPose = skin.get_bindPose(self.mesh)
        if self.joints:
            for joint in self.joints:
                index = connections.get_index_common_connections(joint, bindPose[0], attr='bindPose')
                matrix = pm.getAttr('{}.worldMatrix[{}]'.format(bindPose[0], index))
                inverse_matrix = pm.datatypes.Matrix(matrix).inverse()
                pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), inverse_matrix, type='matrix')

    def add(self):
        FitObjects(joints=self.joints, mesh=self.mesh)


class FitObjects(object):
    """ class for create fit locators on joints """
    PREFIX = '_Fit'

    def __init__(self, joints, mesh):
        self.joints = joints
        self.mesh = mesh
        self.skinCluster = None

        self.fit_grp = None
        self.fit_objects = []

        self.build()

    def create_fit_grp(self):
        self.fit_grp = '{}_fit_grp'.format(self.mesh)
        if not pm.objExists(self.fit_grp):
            self.fit_grp = cmds.createNode('transform', n=self.fit_grp)

    def restore_hierarchy(self):
        for obj, joint in zip(self.fit_objects, self.joints):
            parent_joint = dag.get_parent(joint)
            if parent_joint:
                if parent_joint[0] in self.joints:
                    pm.parent(obj, '{}{}'.format(parent_joint[0], self.PREFIX))

    def build(self):
        self.create_fit_grp()
        self.skinCluster = skin.get_skinCluster(self.mesh)[0]
        for joint in self.joints:
            index = connections.get_index_common_connections(joint, self.skinCluster, attr='worldMatrix')
            if not index:
                continue

            curve = controls.ControlCurve('sphere', name=joint, prefix=self.PREFIX, size=5)
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
