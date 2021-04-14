import maya.cmds as cmds

def enabled_layer(obj, state):
    """ Enabled all layers

    :param obj: 'str' object
    :param state: 'bool' value
    """
    layers = cmds.listConnections(obj, t='displayLayer')
    if layers:
        for layer in layers:
            cmds.setAttr(layer + '.enabled', state)
