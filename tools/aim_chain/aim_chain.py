import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.animation as animation


"""
import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
import MayaTools.tools.aim_chain.aim_chain as aim
reload(aim)
aim.AimChain()
"""


class AimChain(object):
    MAIN_GRP = 'aim_chain'
    AIM_GRP = 'bake_aim_locs'
    POINT_GRP = 'bake_point_locs'
    PIVOT_GRP = 'bake_pivot_locs'

    @staticmethod
    def get_selected():
        sel = pm.selected()
        if not sel:
            om.MGlobal.displayError('Nothing selected')
            return None
        return sel

    @staticmethod
    def make_locator(obj, prefix):
        loc = pm.spaceLocator(n='{}_{}_loc'.format(obj, prefix))
        return loc

    @staticmethod
    def bake_result(obj):
        pm.bakeResults(obj, t=(animation.get_playback_range()), simulation=True)

    def __init__(self):
        self.forward_axis = 'x'
        self.up_axis = 'y'
        self.negative = False
        self.point_locators = []
        # self.last_point = True
        self.create_chain()

    def make_grp(self):
        self.main_grp = pm.createNode('transform', n=self.MAIN_GRP)
        self.aim_grp = pm.createNode('transform', n=self.AIM_GRP)
        self.point_grp = pm.createNode('transform', n=self.POINT_GRP)
        self.pivot_grp = pm.createNode('transform', n=self.PIVOT_GRP)

        pm.parent([self.aim_grp, self.point_grp, self.pivot_grp], self.main_grp)

    def create_point_locators(self):
        self.point_locators = []
        constraints = []
        for c in self.controls:
            point_loc = self.make_locator(c, 'Point')
            self.point_locators.append(point_loc)
            constraints.append(pm.parentConstraint(c, point_loc, mo=False))
            pm.parent(point_loc, self.POINT_GRP)
        self.bake_result(self.point_locators)
        pm.delete(constraints)

    def create_pivot_locators(self):
        self.pivot_locators = []
        self.upWorld_locators = []
        for index in xrange(len(self.controls)):
            if not index + 1 == len(self.controls):
                pivot_loc = self.make_locator(self.controls[index], 'Pivot')
                self.pivot_locators.append(pivot_loc)
                pm.delete(pm.parentConstraint(self.controls[index], pivot_loc, mo=False))

                upWorld_loc = self.make_locator(self.controls[index], 'UpWorld')
                self.upWorld_locators.append(upWorld_loc)
                pm.parent(upWorld_loc, pivot_loc)
                pm.parent(pivot_loc, self.PIVOT_GRP)

                upWorld_loc.t.set(0, 0, 0)
                pm.setAttr('{}.t{}'.format(upWorld_loc, self.up_axis), 2)

    def create_aim_locators(self):
        self.aim_locators = []
        for index in xrange(len(self.controls)):
            if not index + 1 == len(self.controls):
                aim_loc = self.make_locator(self.controls[index], 'Aim')
                pm.pointConstraint(self.controls[index], aim_loc, mo=False)

                self.aim_locators.append(aim_loc)
                pm.parent(aim_loc, self.AIM_GRP)

    def make_connections(self):
        for index in xrange(len(self.point_locators)):
            if not index + 1 == len(self.point_locators):
                pm.pointConstraint(self.controls[index], self.pivot_locators[index])
                pm.orientConstraint(self.point_locators[index], self.pivot_locators[index])
                pm.orientConstraint(self.aim_locators[index], self.controls[index])
                pm.aimConstraint(self.point_locators[index + 1], self.aim_locators[index], mo=True,
                                 aimVector=(1, 0, 0), upVector=(0, 1, 0),
                                 worldUpType='object', worldUpObject=self.upWorld_locators[index])

            if index == 0:
                pm.pointConstraint(self.point_locators[index], self.controls[index])

        self.pivot_grp.hide()
        self.aim_grp.hide()

    def create_chain(self):
        self.controls = self.get_selected()
        if self.controls:
            self.make_grp()
            self.create_point_locators()
            self.create_pivot_locators()
            self.create_aim_locators()
            self.make_connections()
