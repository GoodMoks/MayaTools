import pymel.core as pm
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel
from maya.OpenMaya import MGlobal
import MayaTools.core.dag as dag
import MayaTools.core.skin as skin
import MayaTools.core.utils as utils
import fit

class FitController(object):
    def __init__(self):
        pass

    @staticmethod
    def calculate_bindPoseMatrix(bindPose):
        matrix = pm.getAttr('{}.worldMatrix'.format(bindPose))
        inverse_matrix = [pm.datatypes.Matrix(x).inverse() for x in matrix if x]
        return inverse_matrix

    @staticmethod
    def get_selected():
        sel = cmds.ls(sl=True)
        if not sel:
            MGlobal.displayError('Nothing selected')
            return

        return sel

    @staticmethod
    def all_matrix_round(matrix):
        for index, m in enumerate(matrix):
            matrix[index] = utils.matrix_round_pymel(m, 4)

        return matrix

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
        bindPose = skin.get_bindPose(mesh)

        origin = self.calculate_bindPoseMatrix(bindPose[0])
        current = pm.getAttr('{}.bindPreMatrix'.format(skinCluster[0]))

        origin_round = self.all_matrix_round(origin)
        current_round = self.all_matrix_round(current)

        if origin_round == current_round:
            pm.confirmDialog(parent=parent, message='{} NO CHANGES'.format(mesh))
        else:
            pm.confirmDialog(parent=parent, message='{} WAS MODIFIED.'.format(mesh))

    def go_to_bindPose(self):
        selected = self.filter_selected()
        if not selected:
            return

        mesh = selected['mesh']
        cmds.select(mesh)
        mel.eval('GoToBindPose')


