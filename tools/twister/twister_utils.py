import pymel.core as pm
from core import constraint


def get_length_chain(obj, default=5):
    """ get length chain """

    jnt = get_child(obj, type='joint')
    if not jnt:
        jnt = get_parent(obj, type='joint')

    if jnt:
        return get_distance(obj, jnt)
    else:
        return default




def get_child(obj, type='joint'):
    """ return children list on type"""

    return [x for x in obj.getChildren() if pm.nodeType(x) == type]

def get_parent(obj, type='joint'):
    """ return parent list on type"""

    return [x for x in [obj.getParent()] if pm.nodeType(x) == type]


def is_needed_targets(obj):
    child = get_child(obj)
    if not child or len(child) >= 2:
        return True
    if not constraint.get_connected_constraint(child[0]):
        return True
    return False

def get_targets_from_obj(obj, channels):
    constraint_child = constraint.get_connected_constraint(obj, channels=channels)[0]
    return constraint.get_target_constraint(constraint_child)