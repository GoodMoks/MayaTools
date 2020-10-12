import pymel.core as pm
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel
from maya.OpenMaya import MGlobal
import MayaTools.core.dag as dag
import fit

reload(fit)


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

        pose = fit.FitPose(mesh=selected['mesh'])
        result = pose.check()

        if result:
            pm.confirmDialog(parent=parent, message='{} NO CHANGES'.format(selected['mesh']))
        else:
            pm.confirmDialog(parent=parent, message='{} WAS MODIFIED.'.format(selected['mesh']))

    def go_to_bindPose(self):
        selected = self.filter_selected()
        if not selected:
            return

        mesh = selected['mesh']
        cmds.select(mesh)
        mel.eval('GoToBindPose')

    def reset_bidnPose(self):
        selected = self.filter_selected()
        if not selected:
            return

        pose = fit.FitPose(mesh=selected['mesh'], joints=selected['joint'])
        pose.reset_bindPose()
