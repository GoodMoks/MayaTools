import pymel.core as pm
import maya.OpenMaya as om


class MirrorCtrl(object):
    """docstring for MirrorCtrl"""

    @staticmethod
    def rename(name, orig, replace):
        new_name = name.replace('{}_'.format(orig), '{}_'.format(replace))[:-1]
        name = pm.rename(name, new_name)

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
        obj = pm.selected()
        if not obj:
            om.MGlobal.displayError('Nothing is currently selected')
            return

        self.obj = obj

    def duplicate(self):
        duplicate_selected = pm.duplicate(self.obj)[0]
        print self.orig
        print self.replace
        self.duplicate_selected = self.rename(duplicate_selected, orig=self.orig, replace=self.replace)

    def mirror(self):
        pm.select(d=True)
        # grp = pm.group(w=True, em=True)
        grp = pm.createNode('transform')
        pm.parent(self.duplicate_selected, grp)

        if self.x_axis_checkbox:
            pm.setAttr('{}.sx'.format(grp), -1)

        if self.y_axis_checkbox:
            pm.setAttr('{}.sy'.format(grp), -1)

        if self.z_axis_checkbox:
            pm.setAttr('{}.sz'.format(grp), -1)

        pm.parent(self.duplicate_selected, w=True)
        pm.delete(grp)

    def zero_out(self):
        duplicate_selected = pm.selected()

        for d in duplicate_selected:
            obj = d
            # Create null group
            position_grp = pm.createNode('transform', n=obj + '_POS')
            constraint_grp = pm.createNode('transform', n=obj + '_CON')
            # Query all transform
            translate = pm.xform(obj, q=True, t=True, ws=True)
            rotate = pm.xform(obj, q=True, ro=True, ws=True)
            scale = pm.xform(obj, q=True, s=True, ws=True)
            # Parent null groups
            group_to_parent = pm.parent(constraint_grp, position_grp)[0]
            xform_grp = obj + '_POS'
            # Set transform on main position group
            pm.xform(xform_grp, t=translate, ws=True)
            pm.xform(xform_grp, ro=rotate, ws=True)
            pm.xform(xform_grp, s=scale, ws=True)
            # Parent object to group
            pm.parent(obj, group_to_parent)
            if self.preserve_orient:
                pm.setAttr('{}.rotateY'.format(position_grp), 0)
                pm.setAttr('{}.sz'.format(position_grp), 1)


    def runner(self):
        if not self.obj:
            self.get_sel()

        if self.obj:
            for o in self.obj:
                self.duplicate()
                self.mirror()
                self.zero_out()
