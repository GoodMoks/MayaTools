import pymel.core as pm
import maya.cmds as cmds
from maya.OpenMaya import MGlobal
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin
import MayaTools.core.mesh as mesh
import fit

reload(mesh)
reload(fit)


class FitController(object):

    @staticmethod
    def is_skinned_mesh(mesh):
        pass

    @staticmethod
    def set_bindPreMatrix(matrix, mesh):
        skinCluster = skin.get_skinCluster(mesh)
        for index, m in enumerate(matrix):
            pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')

    @staticmethod
    def get_bindPreMatrix(mesh):
        skinCluster = skin.get_skinCluster(mesh)
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

    def reset_bindPreMatrix(self, mesh, joint=None):
        skinCluster = skin.get_skinCluster(pm.PyNode(mesh))
        if skinCluster:
            if joint:
                index = fit.FitObjects.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
                matrix = pm.getAttr('{}.matrix[{}]'.format(skinCluster[0], index))
                inverse_matrix = pm.datatypes.Matrix(matrix).inverse()
                pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), inverse_matrix, type='matrix')
            else:
                print 'set_bindPreMatrix'
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
            self.reset_bindPreMatrix(selected_mesh[0])

    def check_mesh(self, parent):
        selected_mesh = self.get_selected_mesh()
        if selected_mesh:
            skinCluster = skin.get_skinCluster(selected_mesh[0])
            origin_bindPreMatrix = self.calculate_bindPreMatrix(skinCluster[0])
            current_bindPreMatrix = pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))
            if origin_bindPreMatrix == current_bindPreMatrix:
                pm.confirmDialog(parent=parent, message='{} this mesh has not changed'.format(selected_mesh[0]))
            else:
                pm.confirmDialog(parent=parent, message='{} this mesh has been modified.'.format(selected_mesh[0]))

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
                    pm.parent(child, parent)

                pm.delete(joint_fit)
                mesh_fit_grp = '{}_fit_grp'.format(mesh)
                child = dag.get_children(mesh_fit_grp)
                if not child:
                    pm.delete(mesh_fit_grp)

                self.reset_bindPreMatrix(mesh, joint)


class FitController_New(object):
    def __init__(self):
        pass

    @staticmethod
    def is_mesh(obj):
        shapes = obj.getShape()
        if shapes:
            return shapes if pm.nodeType(shapes) == 'mesh' else None

    @staticmethod
    def get_selected():
        sel = cmds.ls(sl=True)
        if not sel:
            MGlobal.displayError('Nothing selected')
            return

        return sel

    def get_selected_couple(self):
        sel = self.get_selected()
        if sel:
            # if len(sel) < 2:
            #     MGlobal.displayError('First select the joints, and at the end of the geometry')
            #     return

            joint, mesh = sel[:-1], sel[-1]

            # if not self.is_mesh(mesh):
            #     MGlobal.displayError('No geometry was selected, please select a mesh with skin')
            #     return

            return joint, mesh

    def add_fit(self):
        selected = self.get_selected_couple()
        if selected:
            self.joints, self.mesh = selected
            print self.mesh, 'mesh'
            print self.joints, 'joints'
            fit_pose = FitPose(geo=self.mesh)


class FitPose(object):
    def __init__(self, geo, joints=None):
        self.geo = geo
        self.joints = joints

        self.check_arguments()

        if not self.joints:
            self.get_bind_joints()

        self.build()

    def check_arguments(self):
        if not isinstance(self.geo, basestring):
            raise AttributeError('Geo must be a string name of bind geometry')

        if not cmds.objExists(self.geo):
            raise AttributeError('{} does not exist'.format(self.geo))

        if not mesh.is_mesh(self.geo):
            raise AttributeError('{} is not a polygon mesh'.format(self.geo))

        if not skin.get_skinCluster(self.geo):
            raise AttributeError('{} since it is not a skinned object'.format(self.geo))

        if self.joints:
            if not isinstance(self.joints, list):
                raise AttributeError('Joints must be a list of joints')

            for joint in self.joints:
                if not cmds.objExists(joint):
                    raise AttributeError('{} does not exist'.format(joint))

    def get_bind_joints(self):
        joints = skin.get_influence_joint(self.geo)
        if joints:
            self.joints = joints

    @staticmethod
    def add_fit_objects(joints, geo):
        fit.FitObjects(joints=joints, geo=geo)

    def build(self):
        self.add_fit_objects(joints=self.joints, geo=self.geo)
