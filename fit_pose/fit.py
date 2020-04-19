import re
from maya.OpenMaya import MGlobal
import pymel.core as pm
import MayaTools.utils.connections
import MayaTools.utils.dag


class FitObjects(object):
    """ class for create fit locators on joints """

    @staticmethod
    def get_skinCluster(obj):
        return MayaTools.utils.dag.history(obj, type='skinCluster')

    @staticmethod
    def get_index_common_connections(obj1, obj2, attr):
        common_con = MayaTools.utils.connections.get_common_connections(obj1, obj2, attr=attr)
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


class FitController(object):
    @staticmethod
    def is_mesh(obj):
        shapes = obj.getShape()
        if shapes:
            return shapes if pm.nodeType(shapes) == 'mesh' else None

    @staticmethod
    def get_selected():
        sel = pm.selected()
        if not sel:
            MGlobal.displayError('Nothing selected')
            return

        return sel

    @staticmethod
    def set_bindPreMatrix(matrix, mesh):
        skinCluster = FitObjects.get_skinCluster(mesh)
        for index, m in enumerate(matrix):
            pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')

    @staticmethod
    def get_bindPreMatrix(mesh):
        skinCluster = FitObjects.get_skinCluster(mesh)
        if skinCluster:
            return pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))

    def calculate_bindPreMatrix(self, skinCluster):
        matrix = pm.getAttr('{}.matrix'.format(skinCluster))
        inverse_matrix = [pm.datatypes.Matrix(x).inverse() for x in matrix]
        return inverse_matrix

    def get_selected_mesh(self):
        sel = self.get_selected()
        if sel:
            mesh = [mesh for mesh in sel if self.is_mesh(mesh)]
            if not mesh:
                MGlobal.displayError('No geometry was selected last, please select a mesh with skin')
                return

            return mesh

    def get_selected_couple(self):
        sel = self.get_selected()
        if sel:
            if len(sel) < 2:
                MGlobal.displayError('First select the joints, and at the end of the geometry')
                return

            joint, mesh = sel[:-1], sel[-1]

            if not self.is_mesh(mesh):
                MGlobal.displayError('No geometry was selected, please select a mesh with skin')
                return

            return joint, mesh

    def reset_bindPreMatrix(self, mesh, joint=None):
        skinCluster = FitObjects.get_skinCluster(mesh)
        if skinCluster:
            if joint:
                index = FitObjects.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
                matrix = pm.getAttr('{}.matrix[{}]'.format(skinCluster[0], index))
                inverse_matrix = pm.datatypes.Matrix(matrix).inverse()
                pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), inverse_matrix, type='matrix')
            else:
                self.set_bindPreMatrix(self.calculate_bindPreMatrix(skinCluster[0]), mesh)

    def update_mesh(self):
        selected_mesh = self.get_selected_mesh()
        if selected_mesh:
            mesh_group = '{}_fit_grp'.format(selected_mesh[0])
            if not pm.objExists(mesh_group):
                return
            matrix = self.get_bindPreMatrix(selected_mesh[0])
            pm.delete(mesh_group)
            self.set_bindPreMatrix(matrix, selected_mesh[0])

    def reset_mesh(self):
        selected_mesh = self.get_selected_mesh()
        if selected_mesh:
            mesh_group = '{}_fit_grp'.format(selected_mesh[0])
            if pm.objExists(mesh_group):
                pm.delete(mesh_group)

            self.reset_bindPreMatrix(selected_mesh)

    def check_mesh(self, parent):
        print parent
        selected_mesh = self.get_selected_mesh()
        if selected_mesh:
            skinCluster = FitObjects.get_skinCluster(selected_mesh[0])
            origin_bindPreMatrix = self.calculate_bindPreMatrix(skinCluster[0])
            current_bindPreMatrix = pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))
            if origin_bindPreMatrix == current_bindPreMatrix:
                pm.confirmDialog(parent=parent, message='{} this mesh has not changed'.format(selected_mesh[0]))
            else:
                pm.confirmDialog(parent=parent, message='{} this mesh has been modified.'.format(selected_mesh[0]))

    def add_fit(self):
        selected = self.get_selected_couple()
        if selected:
            self.joints, self.mesh = selected
            FitObjects(self.joints, self.mesh)

    def delete_fit(self):
        selected_mesh = self.get_selected_couple()
        if selected_mesh:
            joints, mesh = selected_mesh
            for joint in joints:

                joint_fit = '{}_fit_loc'.format(joint)
                if not pm.objExists(joint_fit):
                    continue

                if MayaTools.utils.dag.get_children(joint_fit):
                    child = MayaTools.utils.dag.get_children(joint_fit)
                    parent = MayaTools.utils.dag.get_parent(joint_fit)[0]
                    print child
                    print parent
                    pm.parent(child, parent)

                pm.delete(joint_fit)

                self.reset_bindPreMatrix(mesh, joint)


