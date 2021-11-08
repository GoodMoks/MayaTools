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


def get_selected_anim_layers():
    """ return all selected anim later in scene

    :return 'list' with all selected anim layers
    """
    selected = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)
    return selected


def get_affected_layer(obj, skip_base_layer=True):
    layers = cmds.animLayer(obj, afl=True, q=True)
    if skip_base_layer:
        layers = [layer for layer in layers if not layer == 'BaseAnimation']

    return layers


def get_anim_curves_from_layer(layer):
    curves = cmds.animLayer(layer, anc=True, q=True)
    return curves


def get_objects_from_anim_layer(layer, attributes=False):
    objects_with_attributes = cmds.animLayer(layer, q=True, at=True)
    if attributes:
        return objects_with_attributes

    objects = list(set(attr.split('.')[0] for attr in objects_with_attributes))
    return objects
