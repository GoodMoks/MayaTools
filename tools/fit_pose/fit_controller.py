import pymel.core as pm
from maya.OpenMaya import MGlobal
import MayaTools.core.dag as dag
import fit



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
        skinCluster = fit.FitObjects.get_skinCluster(mesh)
        for index, m in enumerate(matrix):
            pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')

    @staticmethod
    def get_bindPreMatrix(mesh):
        skinCluster = fit.FitObjects.get_skinCluster(mesh)
        if skinCluster:
            return pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))

    def calculate_bindPreMatrix(self, skinCluster):
        matrix = pm.getAttr('{}.matrix'.format(skinCluster))
        inverse_matrix = [pm.datatypes.Matrix(x).inverse() for x in matrix if x]
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
        skinCluster = fit.FitObjects.get_skinCluster(mesh)
        if skinCluster:
            if joint:
                index = fit.FitObjects.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
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
        selected_mesh = self.get_selected_mesh()
        if selected_mesh:
            skinCluster = fit.FitObjects.get_skinCluster(selected_mesh[0])
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
            fit.FitObjects(self.joints, self.mesh)

    def delete_fit(self):
        selected_mesh = self.get_selected_couple()
        if selected_mesh:
            joints, mesh = selected_mesh
            for joint in joints:

                joint_fit = '{}_fit_loc'.format(joint)
                if not pm.objExists(joint_fit):
                    continue

                if dag.get_children(joint_fit):
                    child = dag.get_children(joint_fit)
                    parent = dag.get_parent(joint_fit)[0]
                    print child
                    print parent
                    pm.parent(child, parent)

                pm.delete(joint_fit)

                self.reset_bindPreMatrix(mesh, joint)
