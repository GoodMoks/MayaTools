import pymel.core as pm
"""
Module for works with connections 
"""

CHANNELS_LIST = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']


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
    connections = pm.listConnections(obj, d=True, p=True)
    if not connections:
        return None

    return [con.split('.')[1] for con in connections if con.split('.')[0] == obj2]


def disconnect_objects(first, second, channels=None):
    """ disconnect objects

    :param first: 'str' first object
    :param second: 'str' second object
    :param channels: 'list' channels for delete connections
    """
    con = pm.listConnections(first, plugs=True, connections=True, destination=False)
    for first_connections, second_connections in con:
        if second_connections.split('.')[0] == second:
            if channels:
                if first_connections.shortName(fullPath=False) in channels:
                    pm.disconnectAttr(second_connections, first_connections)
            else:
                pm.disconnectAttr(second_connections, first_connections)


def get_connections_cb(obj, plugs=False, channels=None):
    """ get input connection in channel box

    :param obj: 'str' object
    :return: dict['object.axis'] = object.axis
    """
    channel_list = channels if channels else CHANNELS_LIST
    connections_dict = dict()
    for channel in channel_list:
        obj_attribute = '{}.{}'.format(obj, channel)
        inputs = pm.listConnections(obj_attribute, d=True, p=True)
        if inputs:
            connections_dict[obj_attribute] = inputs[0] if plugs else inputs[0].split('.')[0]
        else:
            connections_dict[obj_attribute] = None

    return connections_dict

def break_input_connections(obj, attr=None):
    """ disconnect inputs connections

    :param obj: 'str' object
    :param channel: 'list' of attributes
    """
    con = pm.listConnections(obj, plugs=True, connections=True, destination=False)

    if con:
        for dest, source in con:
            if attr:
                for c in attr:
                    full_attr = '{}.{}'.format(obj, c)
                    if dest == full_attr:
                        pm.disconnectAttr(source, dest)
            else:
                pm.disconnectAttr(source, dest)












