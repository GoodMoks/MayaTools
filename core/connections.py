import maya.cmds as cmds
import re

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
    connections = cmds.listConnections(obj, d=True, p=True)
    if not connections:
        return None

    return [con.split('.')[1] for con in connections if con.split('.')[0] == obj2]


def get_index_common_connections(obj1, obj2, attr):
    common_con = get_common_connections('{}'.format(obj1), '{}'.format(obj2), attr=attr)
    if common_con:
        return re.findall('[0-9]+', common_con[0])[0]

def get_input_connections_pairs(obj):
    inputs = []
    input_connections = cmds.listConnections(obj, c=True, s=True, d=False, p=True)
    if input_connections:
        inputs.extend(zip(input_connections[::2], input_connections[1::2]))
    return inputs

def get_output_connections_pairs(obj):
    output = []
    output_connections_ = cmds.listConnections(obj, c=True, s=False, d=True, p=True)
    if output_connections_:
        output.extend(zip(output_connections_[::2], output_connections_[1::2]))
    return output


def disconnect_objects(first, second, channels=None):
    """ disconnect objects

    :param first: 'str' first object
    :param second: 'str' second object
    :param channels: 'list' channels for delete connections
    """
    con = cmds.listConnections(first, plugs=True, connections=True, destination=False)
    for first_connections, second_connections in con:
        if second_connections.split('.')[0] == second:
            if channels:
                if first_connections.split('.')[1] in channels:
                    cmds.disconnectAttr(second_connections, first_connections)
            else:
                cmds.disconnectAttr(second_connections, first_connections)


def get_connections_cb(obj, plugs=False, channels=None):
    """ get input connection in channel box

    :param obj: 'str' object
    :return: dict['object.axis'] = object.axis
    """
    channel_list = channels if channels else CHANNELS_LIST
    connections_dict = dict()
    for channel in channel_list:
        obj_attribute = '{}.{}'.format(obj, channel)
        inputs = cmds.listConnections(obj_attribute, d=True, p=True)
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
    con = get_input_connections_pairs(obj)

    if con:
        for dest, source in con:
            if attr:
                for c in attr:
                    full_attr = '{}.{}'.format(obj, c)
                    if dest == full_attr:
                        cmds.disconnectAttr(source, dest)
            else:
                cmds.disconnectAttr(source, dest)












