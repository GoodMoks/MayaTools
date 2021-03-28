import pymel.core as pm
import aim_chain_controller




class AimChain(object):
    MAIN_GRP = 'aim_chain'
    AIM_GRP = 'bake_aim_locs'
    POINT_GRP = 'bake_point_locs'
    PIVOT_GRP = 'bake_pivot_locs'

    def __init__(self, controls, axis):
        self.controls = controls
        self.axis = axis
        self.set_axis(self.axis)
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
            point_loc = aim_chain_controller.AimChainController.make_locator(c, 'Point')
            self.point_locators.append(point_loc)
            constraints.append(pm.parentConstraint(c, point_loc, mo=False))
            pm.parent(point_loc, self.POINT_GRP)
        aim_chain_controller.AimChainController.bake_result(self.point_locators)
        pm.delete(constraints)

    def create_pivot_locators(self):
        self.pivot_locators = []
        self.upWorld_locators = []
        for index in xrange(len(self.controls)):
            if not index + 1 == len(self.controls):
                pivot_loc = aim_chain_controller.AimChainController.make_locator(self.controls[index], 'Pivot')
                self.pivot_locators.append(pivot_loc)
                pm.delete(pm.parentConstraint(self.controls[index], pivot_loc, mo=False))

                upWorld_loc = aim_chain_controller.AimChainController.make_locator(self.controls[index], 'UpWorld')
                self.upWorld_locators.append(upWorld_loc)
                pm.parent(upWorld_loc, pivot_loc)
                pm.parent(pivot_loc, self.PIVOT_GRP)

                upWorld_loc.t.set(0, 0, 0)
                pm.setAttr('{}.t{}'.format(upWorld_loc, self.aim_axis), 2)

    def create_aim_locators(self):
        self.aim_locators = []
        for index in xrange(len(self.controls)):
            if not index + 1 == len(self.controls):
                aim_loc = aim_chain_controller.AimChainController.make_locator(self.controls[index], 'Aim')
                pm.pointConstraint(self.controls[index], aim_loc, mo=False)

                self.aim_locators.append(aim_loc)
                pm.parent(aim_loc, self.AIM_GRP)

    def make_connections(self):
        for index in xrange(len(self.point_locators)):
            if not index + 1 == len(self.point_locators):
                pm.pointConstraint(self.controls[index], self.pivot_locators[index])
                pm.orientConstraint(self.point_locators[index], self.pivot_locators[index])
                pm.orientConstraint(self.aim_locators[index], self.controls[index], mo=True)
                pm.aimConstraint(self.point_locators[index + 1], self.aim_locators[index], mo=True,
                                 aimVector=(1, 0, 0), upVector=(0, 1, 0),
                                 worldUpType='object', worldUpObject=self.upWorld_locators[index])

            if index == 0:
                pm.pointConstraint(self.point_locators[index], self.controls[index])

        self.pivot_grp.hide()
        self.aim_grp.hide()

    def set_axis(self, axis):
        self.aim_axis = [x for x in ['x', 'z', 'y'] if not x == axis.lower()][0]

    def create_chain(self):
        self.make_grp()
        self.create_point_locators()
        self.create_pivot_locators()
        self.create_aim_locators()
        self.make_connections()
