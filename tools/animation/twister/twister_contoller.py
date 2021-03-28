import pymel.core as pm
import maya.OpenMaya as om
import twister_goal
import MayaTools.core.constraint as constraint


class GoalItem(object):
    def __init__(self):
        self.item = None
        self.object = None
        self.system = None
        self.group = None
        self.options = None
        self.particle = None

        self.goal_twist_node = None
        self.goal_point_node = None

    def set_item(self, item):
        if not isinstance(item, basestring):
            om.MGlobal.displayError('Item should be a string')
            return False

        self.item = item
        self.system = item.split(':')[0].lower()
        self.object = item.split(' ')[1]
        self.group = '{}_dyn_{}_GRP'.format(self.object, self.system)
        self.options = '{}_{}_OPTIONS'.format(self.object, self.system)
        self.particle = '{}_{}_particle'.format(self.object, self.system)

        if self.system == 'twist':
            self.goal_twist_node = '{}_goal_{}'.format(self.object, self.system)
        if self.system == 'point':
            self.goal_point_node = '{}_base_{}'.format(self.object, self.system)

    def get_overlap(self):
        return pm.getAttr('{}.Overlap'.format(self.options))

    def get_stiffness(self):
        return pm.getAttr('{}.Stiffness'.format(self.options))

    def get_smooth(self):
        return pm.getAttr('{}.Smooth'.format(self.options))

    def get_dynamic(self):
        return pm.getAttr('{}.weight'.format(self.options))

    def get_position(self):
        return self.get_position_value()

    def get_dynamic_particle(self):
        return pm.getAttr('{}.isDynamic'.format(self.particle))

    def get_visibility(self):
        return pm.getAttr('{}.visibility'.format(self.group))

    def get_position_value(self):
        if self.system == 'point':
            return 1

        position = self.get_position_goal()
        return position[1] / position[0]

    def get_position_goal(self):
        """ get values for goal twist loc in scene """
        # get length object chain
        length = twister_goal.get_length_chain(pm.PyNode(self.object))
        # check axis where exist value
        axis = [x for x in ['tx', 'ty', 'tz'] if round(pm.getAttr('{}.{}'.format(self.goal_twist_node, x)), 2)][0]
        # get value on found axis
        pos = pm.getAttr('{}.{}'.format(self.goal_twist_node, axis))

        return [length, pos, axis]

    def refresh_goal(self):
        if self.system == 'point':
            loc = self.goal_point_node
        else:

            loc = self.goal_twist_node

        pos = pm.xform(loc, q=True, t=True, ws=True)
        pm.xform(self.particle, t=pos, ws=True)

    def set_overlap(self, value):
        pm.setAttr('{}.Overlap'.format(self.options), value)

    def set_stiffness(self, value):
        pm.setAttr('{}.Stiffness'.format(self.options), value)

    def set_smooth(self, value):
        pm.setAttr('{}.Smooth'.format(self.options), value)

    def set_dynamic(self, value):
        pm.setAttr('{}.weight'.format(self.options), value)

    def set_position(self, value):
        if self.system == 'point':
            return

        position = self.get_position_goal()
        position_new = position[0] * value
        pm.setAttr('{}.{}'.format(self.goal_twist_node, position[2]), position_new)
        self.refresh_goal()

    def set_dynamic_particle(self, value):
        pm.setAttr('{}.isDynamic'.format(self.particle), value)

    def set_visibility(self, value):
        pm.setAttr('{}.visibility'.format(self.group), value)


class GoalMain(object):
    SIMULATION_GROUP = 'simulation_grp'

    @staticmethod
    def add_point(obj):
        return twister_goal.Point(obj)

    @staticmethod
    def add_twist(obj, axis):
        return twister_goal.Twist(obj, axis)

    @staticmethod
    def get_selection():
        selected = pm.selected()
        if not selected:
            om.MGlobal.displayError('Nothing selected')
            return False

        return selected

    @staticmethod
    def is_exists_system(obj, type_system):
        if pm.objExists('{}_dyn_{}_grp'.format(obj, type_system)):
            return True

        return False

    def __init__(self):
        pass

    def delete_system(self, obj, system):
        node = '{}_dyn_{}_GRP'.format(obj, system)
        if pm.objExists(node):
            pm.delete(node)
            self.delete_main_grp()

    def delete_main_grp(self):
        grp = pm.PyNode(self.SIMULATION_GROUP)
        if not grp.getChildren():
            pm.delete(self.SIMULATION_GROUP)

    def create_main_group(self):
        if pm.objExists(self.SIMULATION_GROUP):
            return

        pm.createNode('transform', name=self.SIMULATION_GROUP)
        pm.setAttr('{}.inheritsTransform'.format(self.SIMULATION_GROUP), 0)

    def get_selected_with_constraint(self):
        selected = self.get_selection()
        if selected:
            selected = [x for x in selected if constraint.get_connected_constraint(x)]
            if not selected:
                om.MGlobal.displayError('Selected objects don`t have constraint')
                return False
            return selected

    def add_system(self, axis, twist=True, point=True):
        selected_obj = self.get_selected_with_constraint()
        if selected_obj:
            created_objects = []
            for obj in selected_obj:
                if twist:
                    created_objects.append(self.add_twist(obj, axis))
                if point:
                    created_objects.append(self.add_point(obj))

            if created_objects:
                self.create_main_group()
                for obj in created_objects:
                    pm.parent(obj.main_grp, self.SIMULATION_GROUP)
