import maya.cmds as cmds


def get_common_connections(obj1, obj2, attr):
    """ get common connections between two objects"""
    connections = cmds.listConnections('{}.{}'.format(obj1, attr), d=True, p=True)
    if not connections:
        return None

    return [con.split('.')[1] for con in connections if con.split('.')[0] == obj2]
