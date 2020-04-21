import pymel.core as pm
import maya.OpenMaya as om

"""
import sys

sys.path.append(r'D:\Projects\BakeAimChain')
import bake_chain
reload(bake_chain)

bake_chain.BakeAimChain()
"""




class BakeAimChain:
    MAIN_GRP = 'bake_aim_chain'
    AIM_GRP = 'bake_aim_locs'
    POINT_GRP = 'bake_point_locs'
    PIVOT_GRP = 'bake_pivot_locs'
    ATTR_NAME = 'Up_Loc'

    def __init__(self):
        self.bake()

    def display_massage(self, text):
        om.MGlobal.displayError(text)

    def get_selected(self):
        sel = pm.selected()
        if not sel:
            self.display_massage('Nothing selected')
            return None
        return sel

    def make_loc(self, obj, prefix):
        loc = pm.spaceLocator(n='{}_{}_loc'.format(obj, prefix))
        return loc

    def get_time_range(self):
        start = pm.playbackOptions(q=True, min=True)
        end = pm.playbackOptions(q=True, max=True)
        return (start, end)

    def bake_result(self, obj):
        pm.bakeResults(obj, t=(self.get_time_range()), simulation=True)

    def make_grp(self):
        if not pm.objExists(self.MAIN_GRP):
            self.main = pm.createNode('transform', n=self.MAIN_GRP)
        if not pm.objExists(self.AIM_GRP):
            self.aim = pm.createNode('transform', n=self.AIM_GRP)
        if not pm.objExists(self.POINT_GRP):
            self.point = pm.createNode('transform', n=self.POINT_GRP)
        if not pm.objExists(self.PIVOT_GRP):
            self.pivot = pm.createNode('transform', n=self.PIVOT_GRP)

        try:
            pm.parent([self.aim, self.point, self.pivot], self.main)
        except:
            pass

    def add_attr(self, obj, name):
        pm.addAttr(obj, ln=name, dv=0, k=True)

    def offset_shape_loc(self, locs):
        pass

    def bake(self):
        ctrls = self.get_selected()
        if ctrls:
            self.make_grp()

            point_locs = []
            pivot_locs = []
            up_locs = []
            aim_locs = []
            temp_const = []

            for count in xrange(len(ctrls)):

                # make pivot locators
                pivot_loc = self.make_loc(ctrls[count], 'Pivot')
                pivot_locs.append(pivot_loc)
                temp_const.append(pm.parentConstraint(ctrls[count], pivot_loc, mo=False))

                up_loc = self.make_loc(ctrls[count], 'UpWorld')
                up_locs.append(up_loc)
                pm.parent(up_loc, pivot_loc)
                pm.parent(pivot_loc, self.PIVOT_GRP)
                up_loc.t.set(0, 0, 0)
                up_loc.ty.set(2)

                # make point locators
                if not count == 0:
                    point_loc = self.make_loc(ctrls[count], 'Point')
                    temp_const.append(pm.pointConstraint(ctrls[count], point_loc, mo=False))
                    temp_const.append(pm.orientConstraint(ctrls[count], point_loc, mo=False))

                    # self.add_attr(point_loc, self.ATTR_NAME)

                    point_locs.append(point_loc)
                    pm.parent(point_loc, self.POINT_GRP)

                # make aim locators
                if not count + 1 == len(ctrls):
                    aim_loc = self.make_loc(ctrls[count], 'Aim')
                    pm.pointConstraint(ctrls[count], aim_loc, mo=False)

                    aim_locs.append(aim_loc)
                    pm.parent(aim_loc, self.AIM_GRP)

            self.bake_result([point_locs, pivot_locs])
            InstanceShape(point_locs, 'Up_Loc_VISIBILITY')
            self.add_attr('Up_Loc_VISIBILITY', 'Show')
            for count in xrange(len(aim_locs)):
                pm.connectAttr('Up_Loc_VISIBILITY.Show', '{}.visibility'.format(up_locs[count]))
                pm.orientConstraint(aim_locs[count], ctrls[count])
                pm.pointConstraint(ctrls[count], pivot_locs[count])
                pm.orientConstraint(point_locs[count], pivot_locs[count + 1])
                pm.aimConstraint(point_locs[count], aim_locs[count], mo=True,
                                 aimVector=(1, 0, 0), upVector=(0, 1, 0),
                                 worldUpType='object', worldUpObject=up_locs[count])

            pm.delete(temp_const)
            self.aim.hide()
            self.pivot.hide()
