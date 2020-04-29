import pymel.core as pm

def enabled_layer(obj, state):
    """ Enabled all layers

    :param obj: 'str' object
    :param state: 'bool' value
    """
    layers = pm.listConnections(obj, t='displayLayer')
    if layers:
        for layer in layers:
            pm.setAttr(layer + '.enabled', state)
