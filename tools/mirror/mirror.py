import maya.cmds as cmds
import maya.OpenMaya as om


class MirrorCtrl(object):
    """docstring for MirrorCtrl"""

    @staticmethod
    def rename(name, orig, replace):
        new_name = name.replace('{}_'.format(orig), '{}_'.format(replace))[:-1]
        name = cmds.rename(name, new_name)

        return name

    def __init__(self, obj, orig, replace, x_axis_checkbox, y_axis_checkbox, z_axis_checkbox, preserve_orient):
        self.obj = obj
        self.orig = orig
        self.replace = replace
        self.duplicate_selected = None
        self.x_axis_checkbox = x_axis_checkbox
        self.y_axis_checkbox = y_axis_checkbox
        self.z_axis_checkbox = z_axis_checkbox
        self.preserve_orient = preserve_orient

        self.runner()

    def get_sel(self):
        obj = cmds.ls(sl=True)
        if not obj:
            om.MGlobal.displayError('Nothing is currently selected')
            return

        return obj

    def duplicate(self, obj):
        duplicate_selected = cmds.duplicate(obj)[0]
        return self.rename(duplicate_selected, orig=self.orig, replace=self.replace)

    def mirror(self, obj):
        cmds.select(d=True)
        # grp = pm.group(w=True, em=True)
        grp = cmds.createNode('transform')
        cmds.parent(obj, grp)

        if self.x_axis_checkbox:
            cmds.setAttr('{}.sx'.format(grp), -1)

        if self.y_axis_checkbox:
            cmds.setAttr('{}.sy'.format(grp), -1)

        if self.z_axis_checkbox:
            cmds.setAttr('{}.sz'.format(grp), -1)

        cmds.parent(obj, w=True)
        cmds.delete(grp)

    def zero_out(self, obj):
        # Create null group
        position_grp = cmds.createNode('transform', n=obj + '_POS')
        constraint_grp = cmds.createNode('transform', n=obj + '_CON')
        # Query all transform
        translate = cmds.xform(obj, q=True, t=True, ws=True)
        rotate = cmds.xform(obj, q=True, ro=True, ws=True)
        scale = cmds.xform(obj, q=True, s=True, ws=True)
        # Parent null groups
        group_to_parent = cmds.parent(constraint_grp, position_grp)[0]
        xform_grp = obj + '_POS'
        # Set transform on main position group
        cmds.xform(xform_grp, t=translate, ws=True)
        cmds.xform(xform_grp, ro=rotate, ws=True)
        cmds.xform(xform_grp, s=scale, ws=True)
        # Parent object to group
        cmds.parent(obj, group_to_parent)
        if self.preserve_orient:
            cmds.setAttr('{}.rotateY'.format(position_grp), 0)
            cmds.setAttr('{}.sz'.format(position_grp), 1)

    def runner(self):
        if not self.obj:
            self.obj = self.get_sel()

        if self.obj:
            for o in self.obj:
                duplicated = self.duplicate(o)
                self.mirror(duplicated)
                self.zero_out(duplicated)
