import maya.cmds as cmds

def get_input_connections_pairs(obj):
    inputs = []
    input_connections = cmds.listConnections(obj, c=True, s=True, d=False, p=True)
    if input_connections:
        inputs.extend(zip(input_connections[::2], input_connections[1::2]))
    return inputs


def break_input_connections(obj, attr=None):
    """ disconnect inputs connections

    :param obj: 'str' object
    :param channel: 'list' of attributes
    """
    con = get_input_connections_pairs(obj)

    if con:
        for dest, source in con:
            if attr:
                for c in attr:
                    full_attr = '{}.{}'.format(obj, c)
                    if dest == full_attr:
                        try:
                            cmds.disconnectAttr(source, dest)
                        except:
                            pass
            else:
                try:
                    cmds.disconnectAttr(source, dest)
                except:
                    pass

def align_controls():
    namespace = 'H3'

    world = '{}:Hydra_World_CTRL'.format(namespace)
    root = '{}:Root_CTRL'.format(namespace)
    local = '{}:Local_CTRL'.format(namespace)

    cmds.undoInfo(openChunk=True)
    for ctrl in [world, root, local]:
        break_input_connections(ctrl)

    pos_root = cmds.getAttr('{}.t'.format(root))[0]
    pos_y = pos_root[1]

    cmds.delete(cmds.parentConstraint(world, root, mo=False))
    cmds.setAttr('{}.t'.format(world), pos_root[0], 0, pos_root[2])
    cmds.setAttr('')

    cmds.undoInfo(closeChunk=True)

align_controls()
