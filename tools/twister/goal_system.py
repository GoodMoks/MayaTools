import pymel.core as pm
import MayaTools.core.connections as connections
import MayaTools.core.constraint as constraint
import MayaTools.core.attribute as attribute
import MayaTools.core.transform as transform
import MayaTools.core.particle as particle
import MayaTools.core.vector as vector
import MayaTools.core.dag as dag


class Goal(object):
    """ Main class for goal system """

    @staticmethod
    def is_needed_targets(obj):
        """ check needed targets loc """
        child = dag.get_children(obj)
        if not child or len(child) >= 2:
            return True
        if not constraint.get_connected_constraint(child[0]):
            return True
        return False

    def __init__(self, obj):
        self.obj = obj

        # attr
        self.attr_twist = 'Twist'
        self.attr_overlap = 'Overlap'
        self.attr_stiffness = 'Stiffness'
        self.attr_smooth = 'Smooth'

    def make_grp(self, type_system):
        """ make main group """

        if not pm.objExists('{}_dyn_{}_grp'.format(self.obj, type_system)):
            self.main_grp = pm.createNode('transform', name='{}_dyn_{}_GRP'.format(self.obj, type_system))
        else:
            self.main_grp = '{}_dyn_{}_GRP'.format(self.obj, type_system)

    def add_attr(self):
        """ add attr """
        attribute.add_attr(self.pair, self.attr_overlap, dv=1, min=0, max=1)
        attribute.add_attr(self.pair, self.attr_stiffness, dv=0.75, min=0, max=1)
        attribute.add_attr(self.pair, self.attr_smooth, dv=3.0, min=0.0, max=10.0)

    def con_attr(self):
        """ connect dynamic attr to pair node and particle """
        pm.connectAttr('{}.{}'.format(self.pair, self.attr_overlap), '{}.conserve'.format(self.particle))
        pm.connectAttr('{}.{}'.format(self.pair, self.attr_stiffness), '{}.goalWeight[0]'.format(self.particle))
        pm.connectAttr('{}.{}'.format(self.pair, self.attr_smooth), '{}.goalSmoothness'.format(self.particle))

    def pair_connect(self):
        # get main constraint
        self.main_constraint = constraint.get_connected_constraint(self.obj, channels=self.channels)[0]

        # disconnect main constraint from obj
        connections.disconnect_objects(self.obj, self.main_constraint, channels=self.channels)

        # create new constraint
        self.new_constraint = getattr(pm, self.type_constraint)(self.dynamic_loc, self.obj, mo=True, weight=True)

        # disconnect new constraint from obj
        connections.disconnect_objects(self.obj, self.new_constraint, channels=self.channels)

        # create pair node and set interpolation method
        self.pair = pm.createNode('pairBlend', n='{}_{}_OPTIONS'.format(self.obj, self.system))
        pm.setAttr('{}.rotInterpolation'.format(self.pair), 1)

        # connect constraint to pair node
        for axis in ['X', 'Y', 'Z']:
            pm.connectAttr('{}.constraint{}{}'.format(self.main_constraint, self.transform, axis),
                           '{}.in{}{}1'.format(self.pair, self.transform, axis))
            pm.connectAttr('{}.constraint{}{}'.format(self.new_constraint, self.transform, axis),
                           '{}.in{}{}2'.format(self.pair, self.transform, axis))
            pm.connectAttr('{}.out{}{}'.format(self.pair, self.transform, axis),
                           '{}.{}{}'.format(self.obj, self.transform.lower(), axis))
        pm.setAttr('{}.weight'.format(self.pair), 1)

    def hide_loc(self):
        raise NotImplementedError

    def create_loc(self):
        raise NotImplementedError

    def goal_connect(self):
        raise NotImplementedError


class Point(Goal):
    SYSTEM = 'point'
    CHANNELS = ['tx', 'ty', 'tz']
    TRANSFORM = 'Translate'
    TYPE_CONSTRAINT = 'pointConstraint'

    def __init__(self, obj, visibility=True):
        self.system = self.SYSTEM
        self.channels = self.CHANNELS
        self.transform = self.TRANSFORM
        self.type_constraint = self.TYPE_CONSTRAINT

        super(Point, self).__init__(obj)
        self.visibility = visibility
        self.create()
        pm.select(self.obj)

    def create_loc(self):
        # make locators
        self.base_loc = pm.spaceLocator(n='{}_base_{}'.format(self.obj, self.SYSTEM))

        # align locators to obj
        transform.align_transform(self.obj, self.base_loc)

    def goal_connect(self):
        # add goal system
        self.dynamic_loc, self.particle = particle.create_goal(self.base_loc, base_name=self.obj, prefix=self.SYSTEM)
        pm.parent([self.base_loc, self.dynamic_loc, self.particle], self.main_grp)

        constraint.restore_constraint(self.obj, self.base_loc)

    def hide_loc(self):
        # set visibility
        self.main_grp.visibility.set(self.visibility)
        self.dynamic_loc.visibility.set(self.visibility)

    def create(self):
        self.make_grp(self.SYSTEM)
        self.create_loc()
        self.goal_connect()
        self.pair_connect()
        self.add_attr()
        self.con_attr()
        self.hide_loc()


class Twist(Goal):
    SYSTEM = 'twist'
    CHANNELS = ['rx', 'ry', 'rz']
    TRANSFORM = 'Rotate'
    TYPE_CONSTRAINT = 'orientConstraint'
    AIM_AXIS = ['x', 'y', 'z']

    def __init__(self, obj, axis='X', visibility=True, second_axis=None):
        self.system = self.SYSTEM
        self.channels = self.CHANNELS
        self.transform = self.TRANSFORM
        self.type_constraint = self.TYPE_CONSTRAINT

        super(Twist, self).__init__(obj)
        self.axis = axis.lower()
        self.aim_axis = [x for x in ['x', 'z', 'y'] if not x == self.axis][0]
        self.visibility = visibility

        if second_axis:
            if second_axis.lower() in self.AIM_AXIS and not second_axis == self.axis:
                self.axis = second_axis

        self.create()
        pm.select(self.obj)

    def create_loc(self):
        self.base_loc = pm.spaceLocator(n='{}_base_{}'.format(self.obj, self.SYSTEM))
        transform.align_transform(self.obj, self.base_loc, t=True, ro=True)
        pm.parent(self.base_loc, self.main_grp)

        # base rotate loc
        self.base_rotate_loc = pm.duplicate(self.base_loc)[0]
        pm.rename(self.base_rotate_loc, '{}_base_rotate_{}'.format(self.obj, self.SYSTEM))
        pm.parent(self.base_rotate_loc, self.base_loc)

        # goal loc for follow particle
        self.goal_loc = pm.spaceLocator(n='{}_goal_{}'.format(self.obj, self.SYSTEM))
        transform.align_transform(self.obj, self.goal_loc)
        pm.parent(self.goal_loc, self.base_rotate_loc)
        pm.setAttr('{}.t{}'.format(self.goal_loc, self.aim_axis), get_length_chain(self.obj) / 1)

        # aim dynamic loc
        self.dynamic_loc = pm.spaceLocator(n='{}_dynamic'.format(self.obj))
        transform.align_transform(self.obj, self.dynamic_loc, ro=True)
        pm.parent(self.dynamic_loc, self.main_grp)

        # target loc
        if self.is_needed_targets(self.obj):
            self.target_loc = pm.spaceLocator(n='{}_target_loc'.format(self.obj))
            transform.align_transform(self.obj, self.target_loc)
            pm.parent(self.target_loc, self.base_loc)
            pm.setAttr('{}.t{}'.format(self.target_loc, self.axis), get_length_chain(self.obj) / 2)

    def goal_connect(self):
        self.goal_transform, self.particle = particle.create_goal(self.goal_loc, base_name=self.obj,
                                                                  prefix=self.SYSTEM)
        pm.parent([self.goal_transform, self.particle], self.main_grp)

        # constraint base loc to parents targets obj
        targets_rotate = get_targets_from_obj(self.obj, channels=self.CHANNELS)
        pm.orientConstraint(targets_rotate, self.base_loc)

        # constraint base loc, dynamic loc to parents targets obj
        pm.pointConstraint(self.obj, self.base_loc)
        pm.pointConstraint(self.obj, self.dynamic_loc)

        if self.is_needed_targets(self.obj):
            targets = self.target_loc
        else:
            child = dag.get_children(self.obj)[0]
            targets = get_targets_from_obj(child, channels=['tx', 'ty', 'tz'])

        pm.aimConstraint(targets, self.dynamic_loc, mo=True, aimVector=(1, 0, 0),
                         upVector=(0, 1, 0), worldUpType='object',
                         worldUpObject=self.goal_transform)

    def hide_loc(self):
        self.main_grp.visibility.set(self.visibility)
        self.goal_transform.visibility.set(self.visibility)
        pm.setAttr('{}.visibility'.format(self.base_loc.getShape()), self.visibility)
        pm.setAttr('{}.visibility'.format(self.base_rotate_loc.getShape()), self.visibility)
        if hasattr(self, 'target_loc'):
            pm.setAttr('{}.visibility'.format(self.target_loc.getShape()), self.visibility)

    def con_attr(self):
        pm.connectAttr('{}.{}'.format(self.pair, self.attr_twist), '{}.r{}'.format(self.base_rotate_loc, self.axis))
        super(Twist, self).con_attr()

    def add_attr(self):
        super(Twist, self).add_attr()
        attribute.add_attr(self.pair, self.attr_twist, dv=0.0, min=-360, max=360)

    def create(self):
        self.make_grp(self.SYSTEM)
        self.create_loc()
        self.goal_connect()
        self.pair_connect()
        self.add_attr()
        self.con_attr()
        self.hide_loc()


def get_length_chain(obj, default=5):
    """ get length chain """

    jnt = dag.get_children(obj)
    if not jnt:
        jnt = dag.get_parent(obj)

    if jnt:
        return vector.get_distance(obj, jnt)
    else:
        return default


def get_targets_from_obj(obj, channels):
    constraint_child = constraint.get_connected_constraint(obj, channels=channels)[0]
    return constraint.get_target_constraint(constraint_child)
