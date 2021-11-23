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


def get_affected_anim_layer(obj, skip_base_layer=False):
    """ get related animation later for given object

    :param obj: 'str' name of object
    :param skip_base_layer: 'bool' return value with 'BaseAnimation' or not
    :return: 'list' of animation layers
    """
    layers = cmds.animLayer([obj], afl=True, q=True)

    if skip_base_layer and layers:
        layers = [layer for layer in layers if not layer == 'BaseAnimation']

    return layers


def get_base_layer_curves(obj):
    """ return base animation curve for given object

    :param obj: 'str' name of object
    :return: 'list' with base animation curves
    """
    base_curves = []
    obj_curves = get_obj_curves_from_layer(layer='BaseAnimation', obj=obj)
    if obj_curves:
        base_curves.extend(obj_curves)
    curves_not_in_layer = cmds.listConnections(obj, t='animCurve')
    if curves_not_in_layer:
        base_curves.extend(curves_not_in_layer)

    return base_curves


def get_selected_anim_layers():
    """ return all selected anim later in scene

    :return 'list' with all selected anim layers
    """
    selected = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)
    return selected


def get_objects_from_layer(layer, attributes=False):
    """ get all object in animation layer

    :param layer: 'str' animation layer
    :param attributes: 'bool' return object with attributes 'obj.translateX' or not 'obj'
    :return: 'list' with objects
    """
    objects_with_attributes = cmds.animLayer(layer, q=True, at=True)
    if not objects_with_attributes:
        return

    if attributes:
        return objects_with_attributes

    objects = list(set(attr.split('.')[0] for attr in objects_with_attributes))
    return objects


def get_obj_curves_from_layer(layer, obj):
    """ return anim curves only from layer

    :param layer: 'str' animation layer
    :param obj: 'str' animated object
    :return: 'list' list with animations curve nodes
    """
    all_attributes = ['.'.join([obj, a]) for a in cmds.listAttr(obj, k=True)]
    curves = []
    for attr in all_attributes:
        curve = cmds.animLayer(layer, q=True, fcv=attr)
        if curve:
            curves.extend(curve)

    return curves


def get_all_curves_from_layer(layer):
    """ return all animation curves for all objects in layer

    :param layer: 'str' animation layer
    :return: 'list' with animation curves
    """
    curves = cmds.animLayer(layer, anc=True, q=True)
    return curves


def object_in_layer(obj, layer):
    """ checks if there is an object in the layer

    Args:
        obj: 'str' name of object
        layer: 'str' name of animation layer

    Returns: 'bool' if in layer return True, if not return False

    """
    obj_layers = get_affected_anim_layer(obj=obj)
    if layer in obj_layers:
        return True
    return False

# def get_all_curves_from_layer(layer):
#     """ return all anim curves from layers for all objects
#
#     Args:
#         layer: 'str' layer name
#
#     Returns: 'list' animation curves
#
#     """
#     anim_curves = []
#     layer_objects = get_objects_from_layer(layer=layer)
#     if layer_objects:
#         for obj in layer_objects:
#             curves = get_obj_curves_from_layer(layer=layer, obj=obj)
#             anim_curves.extend(curves)
#
#     return anim_curves
