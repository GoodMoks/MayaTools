import pymel.core as pm
import maya.api.OpenMaya as om2
import maya.cmds as cmds
from maya.OpenMaya import MGlobal
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin
import MayaTools.core.mesh as mesh
import fit

reload(mesh)
reload(fit)
reload(dag)


class FitController(object):
    def __init__(self):
        pass

    @staticmethod
    def get_selected():
        sel = cmds.ls(sl=True)
        if not sel:
            MGlobal.displayError('Nothing selected')
            return

        return sel

    def get_selected_all(self):
        selected = self.get_selected()
        if not selected:
            return

        return_dict = dict()

        for s in selected:
            if dag.object_type(s) in return_dict:
                obj = return_dict[dag.object_type(s)]
                if not isinstance(obj, list):
                    obj = [obj]

                obj.append(s)
                return_dict[dag.object_type(s)] = obj
                continue

            return_dict[dag.object_type(s)] = s

        return return_dict

    def filter_selected(self):
        all_selected = self.get_selected_all()

        mesh = all_selected.get('mesh', None)
        if not mesh:
            om2.MGlobal.displayInfo('Please selected mesh')
            return

        joint = all_selected.get('joint', None)
        if joint:
            if not isinstance(joint, list):
                joint = [joint]

        return dict(mesh=mesh, joint=joint)

    def add(self):
        selected = self.filter_selected()
        if not selected:
            return

        pose = fit.FitPose(mesh=selected['mesh'], joints=selected['joint'])
        pose.add()

    def update(self):
        selected = self.filter_selected()
        if not selected:
            return

        pose = fit.FitPose(selected['mesh'])
        pose.update()

    def reset(self):
        selected = self.filter_selected()
        if not selected:
            return

        pose = fit.FitPose(mesh=selected['mesh'], joints=selected['joint'])
        pose.reset()

    def check(self, parent):
        selected = self.filter_selected()
        if not selected:
            return

        mesh = selected['mesh']

        skinCluster = skin.get_skinCluster(mesh)

        origin_bindPreMatrix = fit.FitPose.calculate_bindPreMatrix(skinCluster[0])
        current_bindPreMatrix = pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))

        if origin_bindPreMatrix == current_bindPreMatrix:
            pm.confirmDialog(parent=parent, message='{} this mesh has not changed'.format(mesh))
        else:
            pm.confirmDialog(parent=parent, message='{} this mesh has been modified.'.format(mesh))

# class FitControllerOld(object):
#
#     @staticmethod
#     def is_skinned_mesh(mesh):
#         pass
#
#     @staticmethod
#     def set_bindPreMatrix(matrix, mesh):
#         skinCluster = skin.get_skinCluster(mesh)
#         for index, m in enumerate(matrix):
#             pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')
#
#     @staticmethod
#     def get_bindPreMatrix(mesh):
#         skinCluster = skin.get_skinCluster(mesh)
#         if skinCluster:
#             return pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))
#
#     def calculate_bindPreMatrix(self, skinCluster):
#         matrix = pm.getAttr('{}.matrix'.format(skinCluster))
#         inverse_matrix = [pm.datatypes.Matrix(x).inverse() for x in matrix if x]
#         return inverse_matrix
#
#     def get_selected_mesh(self):
#         sel = self.get_selected()
#         if sel:
#             mesh = [mesh for mesh in sel if self.is_mesh(mesh)]
#             if not mesh:
#                 MGlobal.displayError('No geometry was selected last, please select a mesh with skin')
#                 return
#
#             return mesh
#
#     def reset_bindPreMatrix(self, mesh, joint=None):
#         skinCluster = skin.get_skinCluster(pm.PyNode(mesh))
#         if skinCluster:
#             if joint:
#                 index = fit.FitObjects.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
#                 matrix = pm.getAttr('{}.matrix[{}]'.format(skinCluster[0], index))
#                 inverse_matrix = pm.datatypes.Matrix(matrix).inverse()
#                 pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), inverse_matrix, type='matrix')
#             else:
#                 print 'set_bindPreMatrix'
#                 self.set_bindPreMatrix(self.calculate_bindPreMatrix(skinCluster[0]), mesh)
#
#     def update_mesh(self):
#         selected_mesh = self.get_selected_mesh()
#         if selected_mesh:
#             mesh_group = '{}_fit_grp'.format(selected_mesh[0])
#             if not pm.objExists(mesh_group):
#                 return
#             matrix = self.get_bindPreMatrix(selected_mesh[0])
#             pm.delete(mesh_group)
#             self.set_bindPreMatrix(matrix, selected_mesh[0])
#
#     def reset_mesh(self):
#         selected_mesh = self.get_selected_mesh()
#         if selected_mesh:
#             mesh_group = '{}_fit_grp'.format(selected_mesh[0])
#             if pm.objExists(mesh_group):
#                 pm.delete(mesh_group)
#             self.reset_bindPreMatrix(selected_mesh[0])
#
#     def check_mesh(self, parent):
#         selected_mesh = self.get_selected_mesh()
#         if selected_mesh:
#             skinCluster = skin.get_skinCluster(selected_mesh[0])
#             origin_bindPreMatrix = self.calculate_bindPreMatrix(skinCluster[0])
#             current_bindPreMatrix = pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))
#             if origin_bindPreMatrix == current_bindPreMatrix:
#                 pm.confirmDialog(parent=parent, message='{} this mesh has not changed'.format(selected_mesh[0]))
#             else:
#                 pm.confirmDialog(parent=parent, message='{} this mesh has been modified.'.format(selected_mesh[0]))
#
#     def delete_fit(self):
#         selected_mesh = self.get_selected_couple()
#         if selected_mesh:
#             joints, mesh = selected_mesh
#             for joint in joints:
#
#                 joint_fit = '{}_fit_loc'.format(joint)
#                 if not pm.objExists(joint_fit):
#                     continue
#
#                 if dag.get_children(joint_fit):
#                     child = dag.get_children(joint_fit)
#                     parent = dag.get_parent(joint_fit)[0]
#                     pm.parent(child, parent)
#
#                 pm.delete(joint_fit)
#                 mesh_fit_grp = '{}_fit_grp'.format(mesh)
#                 child = dag.get_children(mesh_fit_grp)
#                 if not child:
#                     pm.delete(mesh_fit_grp)
#
#                 self.reset_bindPreMatrix(mesh, joint)
#
#
# class FitController(object):
#     @staticmethod
#     def is_mesh(obj):
#         shapes = obj.getShape()
#         if shapes:
#             return shapes if pm.nodeType(shapes) == 'mesh' else None
#
#     @staticmethod
#     def get_selected():
#         sel = cmds.ls(sl=True)
#         if not sel:
#             MGlobal.displayError('Nothing selected')
#             return
#
#         return sel
#
#     def get_selected_couple(self):
#         sel = self.get_selected()
#         if sel:
#             joint, mesh = sel[:-1], sel[-1]
#             return joint, mesh
#
#     def add_fit(self):
#         selected = self.get_selected_couple()
#         if selected:
#             self.joints, self.mesh = selected
#             fit_pose = FitPose(geo=self.mesh)
#             fit_pose.build()
#
#     def get_selected_mesh(self):
#         sel = self.get_selected()
#         if sel:
#             mesh = [mesh for mesh in sel if self.is_mesh(mesh)]
#             if not mesh:
#                 MGlobal.displayError('No geometry was selected last, please select a mesh with skin')
#                 return
#
#             return mesh
#
#     def get_selected_all(self):
#         selected = self.get_selected()
#         if selected:
#             pass
#
#     @staticmethod
#     def set_bindPreMatrix(matrix, mesh):
#         skinCluster = skin.get_skinCluster(mesh)
#         for index, m in enumerate(matrix):
#             pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), m, type='matrix')
#
#     def reset_mesh(self):
#         selected_mesh = self.get_selected_mesh()
#         if selected_mesh:
#             mesh_group = '{}_fit_grp'.format(selected_mesh[0])
#             print mesh_group
#             # if pm.objExists(mesh_group):
#             #    pm.delete(mesh_group)
#             # self.reset_bindPreMatrix(selected_mesh[0])
#
#     def reset_bindPreMatrix(self, geo, joint=None):
#         skinCluster = skin.get_skinCluster(geo)
#         if skinCluster:
#             if joint:
#                 index = connections.get_index_common_connections(joint, skinCluster[0], attr='worldMatrix')
#                 matrix = pm.getAttr('{}.matrix[{}]'.format(skinCluster[0], index))
#                 inverse_matrix = pm.datatypes.Matrix(matrix).inverse()
#                 pm.setAttr('{}.bindPreMatrix[{}]'.format(skinCluster[0], index), inverse_matrix, type='matrix')
#             else:
#                 self.set_bindPreMatrix(self.calculate_bindPreMatrix(skinCluster[0]), geo)
