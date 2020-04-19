import maya.cmds as cmds


def get_common_connections(obj1, obj2, attr=None):
    """ get common connections for two objects
    attribute "attr" allows get connections for current attribute

    :param obj1: 'str' object
    :param obj2: 'str' object
    :param attr: 'attr' name of attribute ex: attr='worldMatrix'
    :return: list with commons attr or []
    """
    obj = obj1
    if attr:
        obj = '{}.{}'.format(obj1, attr)
    connections = cmds.listConnections(obj, d=True, p=True)
    if not connections:
        return None

    return [con.split('.')[1] for con in connections if con.split('.')[0] == obj2]

