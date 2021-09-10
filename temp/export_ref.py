import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
import MayaTools.core.name as name

reload(name)


"""
Draft work version of my script
"""
# todo Create UI
# todo Add the option not to delete non-reference objects


def make_isolate():
    sel = cmds.ls(sl=True)
    if not sel:
        om2.MGlobal.displayError('Please select top object of hierarchy')
    if len(sel) > 1:
        om2.MGlobal.displayError('Please select only one object')

    IsolateSkeleton(sel[0])


class IsolateSkeleton(object):
    @staticmethod
    def compare_hierarchy_ref(origin, isolate):
        child_origin = pm.listRelatives(origin, ad=True)
        child_isolate = pm.listRelatives(isolate, ad=True)
        not_reference = []
        if not len(child_origin) == len(child_isolate):
            return None

        for index in range(len(child_origin)):
            state = pm.referenceQuery(child_origin[index], inr=True)
            if not state:
                not_reference.append(child_isolate[index])

        return not_reference

    @staticmethod
    def confirm_dialog(name_joint):
        response = cmds.confirmDialog(
            title='Duplicate?',
            message='There is an object with the same name as the skeleton - "{}"?'.format(name_joint),
            button=['Okey', 'Ne Okey'],
        )
        if response == 'Ne Okey':
            return False
        return True

    @staticmethod
    def is_exist_world_name(obj):
        root_name = cmds.ls(obj)

        if len(root_name):
            world_objects = [x for x in root_name if not cmds.listRelatives(x, ap=True)]
            if world_objects:
                return True
        return False

    def __init__(self, obj):
        self.main_top = obj
        self.duplicate_objects = None
        self.isolate_top = None

        cmds.undoInfo(openChunk=True)
        self.duplicate_special()
        cmds.undoInfo(closeChunk=True)

    def duplicate_special(self):


        absolute_name = name.strip_namespace(self.main_top)
        world_name = self.is_exist_world_name(absolute_name)
        if world_name:
            if not self.confirm_dialog(absolute_name):
                return False

        self.duplicate_objects = cmds.duplicate(self.main_top, ilf=True, ic=True, po=False, rr=False)
        self.isolate_top = self.duplicate_objects[0]
        cmds.connectAttr('{}.parentMatrix'.format(self.main_top), '{}.offsetParentMatrix'.format(self.isolate_top))

        if cmds.listRelatives(self.isolate_top, p=True):
            cmds.parent(self.isolate_top, w=True)

        delete_list = self.compare_hierarchy_ref(self.main_top, self.duplicate_objects[0])
        if not delete_list:
            return

        pm.delete(delete_list)
