import pymel.core as pm
import MayaTools.utils.connections as connections


def is_constraint(obj):
    """ check is constraint

    :param obj: 'str' constraint name
    :return: 'bool'
    """

    const_all = ['parentConstraint', 'pointConstraint',
                 'orientConstraint', 'aimConstraint',
                 'scaleConstraint', 'poleVectorConstraint']

    if [x for x in const_all if x == pm.objectType(obj)]:
        return True
    else:
        return False


def get_connected_constraint(obj, plugs=False, channels=None):
    """ get all connected constraint

    :param obj: 'str' obj name
    :return: 'list' of constraints
    """
    cons = connections.get_connections_cb(obj, plugs=plugs, channels=channels)
    constraints = set()
    for axis, connection in cons.iteritems():
        if connection:
            if is_constraint(connection):
                constraints.add(connection)
    return list(constraints)



def get_target_constraint(constraint):
    """ get target list in constraint

    :param obj: 'str' constraint name
    :return: 'list' targets
    """
    return pm.PyNode(constraint).getTargetList()


def restore_constraint(source, target, offset=True):
    """ make copy constraint connections

    version with create new constraint

    :param source: 'str' name obj
    :param target: 'str' name obj
    :param offset: 'bool' offset for constraint
    """
    connected_constraint = get_connected_constraint(source)
    if connected_constraint:
        for source_constraint in connected_constraint:
            targets = get_target_constraint(source_constraint)
            new_constraint = getattr(pm, pm.nodeType(source_constraint))(targets, target, mo=offset)
            connections.disconnect_objects(target, new_constraint)
            for axis, input_constraint in connections.get_connections_cb(source, plugs=True).iteritems():
                if input_constraint:
                    if source_constraint == input_constraint.split('.')[0]:
                        pm.connectAttr('{}.{}'.format(new_constraint, input_constraint.split('.')[1]),
                                       '{}.{}'.format(target, axis.split('.')[1]))


def duplicate_constraint_connections(source, target):
    """ make duplicate constraint and restore connections

    :param source: 'str' name obj
    :param target: 'str' name obj
    """
    connected_constraints = get_connected_constraint(source)
    for constraint in connected_constraints:
        constraint = pm.PyNode(constraint)
        outputs = constraint.outputs(c=True, p=True)
        inputs = constraint.inputs(c=True, p=True)
        duplicate_constraint = pm.duplicate(constraint)[0]
        pm.parent(duplicate_constraint, target)
        for in_connection in inputs:
            try:
                pm.connectAttr('{}.{}'.format(target, in_connection[1].split('.')[1]),
                               '{}.{}'.format(duplicate_constraint, in_connection[0].split('.')[1]))
            except:
                pass
        for out_connection in outputs:
            try:
                pm.connectAttr(out_connection[0], '{}.{}'.format(target, out_connection[1].split('.')[1]))
            except:
                pass
