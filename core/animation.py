import maya.cmds as cmds
import MayaTools.core.layers as layers

def get_playback_range():
    """ get playback range

    :return: (start frame, end frame)
    """
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    return (start, end)


def get_all_anim_curves(obj):
    """ return all animation curves from all layers (BaseAnimation, ...)

    :param obj: 'str' object name
    :return: 'list' with animation curves
    """
    anim_curves = []
    layers_obj = layers.get_affected_anim_layer(obj=obj)
    if layers_obj:
        for layer in layers_obj:
            anim_curves.extend(layers.get_obj_curves_from_layer(layer=layer, obj=obj))

    curves_not_in_later = cmds.listConnections(obj, t='animCurve')
    if curves_not_in_later:
        anim_curves.extend(curves_not_in_later)

    return anim_curves