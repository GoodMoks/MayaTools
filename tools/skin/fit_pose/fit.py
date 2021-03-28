import pymel.core as pm
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin
import MayaTools.core.utils as utils
import MayaTools.core.mesh as core_mesh
import MayaTools.core.connections as connections
import MayaTools.tools.rig.control_manager.controls as controls


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
            try:
                pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')
            except:
                pass

    @staticmethod
    def get_all_bindPoseMatrix(mesh):
        joints = skin.get_influence_joint(mesh)
        matrix = list([pm.getAttr('{}.bindPose'.format(joint)) for joint in joints])
        inverse_matrix = [pm.datatypes.Matrix(x).inverse() for x in matrix if x]
        return inverse_matrix

    @staticmethod
    def all_matrix_round(matrix):
        for index, m in enumerate(matrix):
            matrix[index] = utils.matrix_round_pymel(m, 4)

        return matrix

    def __init__(self, mesh, joints=None):
        self.mesh = mesh
        self.joints = joints

        self.check_arguments()

        if not self.joints:
            self.get_bind_joints()

        self.reset_bindPose()


    def check_arguments(self):
        if not isinstance(self.mesh, basestring):
            raise AttributeError('Geo must be a string name of bind geometry')

        if not cmds.objExists(self.mesh):
            raise AttributeError('{} does not exist'.format(self.mesh))

        if not core_mesh.is_mesh(self.mesh):
            raise AttributeError('{} is not a polygon mesh'.format(self.mesh))

        if not skin.get_skinCluster(self.mesh):
            raise AttributeError('{} since it is not a skinned object'.format(self.mesh))

        if not skin.get_bindPose(self.mesh):
            raise AttributeError('{} this objects has no bindPose'.format(self.mesh))

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

        for joint in self.joints:
            fit_object = '{}{}'.format(joint, FitObjects.PREFIX)
            if pm.objExists(fit_object):
                fit_children = dag.get_children(fit_object)
                if fit_children:
                    fit_parent = dag.get_parent(fit_object)
                    cmds.parent(fit_children, fit_parent)

                cmds.delete(fit_object)

            index_skinCluster = connections.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
            matrix = om2.MMatrix(cmds.getAttr('{}.bindPose'.format(joint))).inverse()
            cmds.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index_skinCluster), matrix, type='matrix')

        if pm.objExists('{}{}'.format(self.mesh, self.PREFIX_GRP)):
            fit_grp = '{}{}'.format(self.mesh, self.PREFIX_GRP)
            fit_children = dag.get_children(fit_grp)
            if not fit_children:
                cmds.delete(fit_grp)

    def check(self):
        skinCluster = skin.get_skinCluster(self.mesh)[0]
        joints = skin.get_influence_joint(self.mesh)

        dif = []
        for index, joint in enumerate(joints):
            bindPose = om2.MMatrix(cmds.getAttr('{}.bindPose'.format(joint))).inverse()
            preBind = om2.MMatrix(cmds.getAttr('{}.bindPreMatrix[{}]'.format(skinCluster, index)))

            bindPose_round = utils.numbers_list_round(bindPose, 2)
            preBind_round = utils.numbers_list_round(preBind, 2)

            if not bindPose_round == preBind_round:
                dif.append(joint)

        return dif

    def reset_bindPose(self):
        bindPose = skin.get_bindPose(self.mesh)[0]

        duplicate = cmds.duplicate(bindPose, rc=True, un=True)

        copy_bindPose = duplicate[0]

        joints = cmds.listConnections('{}.members'.format(bindPose), type='joint')
        copy_joints = cmds.listConnections('{}.members'.format(copy_bindPose), type='joint')

        pm.dagPose(r=True, n=copy_bindPose)
        for copy, source in zip(copy_joints, joints):
            joint_parentMatrix = cmds.getAttr('{}.worldMatrix'.format(copy))
            cmds.setAttr('{}.bindPose'.format(source), joint_parentMatrix, type='matrix')

        cmds.delete(duplicate)

    def add(self):
        FitObjects(joints=self.joints, mesh=self.mesh)


class FitObjects(object):
    """ class for create fit locators on joints """
    PREFIX = '_Fit'

    def __init__(self, joints, mesh):
        self.joints = joints
        self.mesh = mesh

        self.skinCluster = None
        self.bindPose = None
        self.fit_grp = None
        self.fit_objects = []

        self.build()

    def create_fit_grp(self):
        self.fit_grp = '{}_fit_grp'.format(self.mesh)
        if not cmds.objExists(self.fit_grp):
            self.fit_grp = cmds.createNode('transform', n=self.fit_grp)

    def restore_hierarchy(self):
        for obj, joint in zip(self.fit_objects, self.joints):
            parent_joint = dag.get_parent(joint)
            if parent_joint:
                if parent_joint[0] in self.joints:
                    cmds.parent(obj, '{}{}'.format(parent_joint[0], self.PREFIX))

    def build(self):
        self.create_fit_grp()
        self.skinCluster = skin.get_skinCluster(self.mesh)[0]
        for joint in self.joints:
            index_skinCluster = connections.get_index_common_connections(joint, self.skinCluster, attr='worldMatrix')
            if not index_skinCluster:
                continue

            joint_scale = utils.get_joint_display_scale(joint)
            curve = controls.ControlCurve('sphere', name=joint, suffix=self.PREFIX, size=joint_scale * 2, color=(1, 0, 0))
            fit_object = curve.create()[0]
            self.fit_objects.append(fit_object)
            cmds.parent(str(fit_object), self.fit_grp)

            # get matrices
            joint_world = om2.MMatrix(cmds.getAttr('{}.worldMatrix'.format(joint)))
            joint_worldInverse = om2.MMatrix(cmds.getAttr('{}.worldInverseMatrix'.format(joint)))
            bindPre = om2.MMatrix(cmds.getAttr('{}.bindPreMatrix[{}]'.format(self.skinCluster, index_skinCluster)))
            bindPose = om2.MMatrix(cmds.getAttr('{}.bindPose'.format(joint)))
            bindPose_inverse = bindPose.inverse()

            object_matrix = (bindPose * bindPre * joint_world)
            cmds.xform(fit_object, matrix=object_matrix)

            mult_node = cmds.createNode('multMatrix', n='{}_fit_multMatrix'.format(joint))
            pm.setAttr('{}.matrixIn[0]'.format(mult_node), bindPose_inverse, type='matrix')
            pm.connectAttr('{}.worldMatrix'.format(fit_object), '{}.matrixIn[1]'.format(mult_node))
            pm.setAttr('{}.matrixIn[2]'.format(mult_node), joint_worldInverse, type='matrix')

            pm.connectAttr('{}.matrixSum'.format(mult_node),
                           '{}.bindPreMatrix[{}]'.format(self.skinCluster, index_skinCluster))

        self.restore_hierarchy()
