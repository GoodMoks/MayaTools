import maya.cmds as cmds
import MayaTools.core.animation as animation
import MayaTools.core.base as base
import MayaTools.core.layers as layers
import MayaTools.core.utils as utils
import maya.api.OpenMaya as om2
import pymel.core as pm

reload(animation)
reload(layers)
reload(base)
reload(utils)


# todo 1. Find method bake only anim curve
# todo 2. fix layers core (добавить возможность забирать кривые только для выделенного обьекта)

def build():
    sel = cmds.ls(sl=True)

    TimeWrap().warp_object_in_scene()
    # # layer = cmds.animLayer(sel, afl=True, q=True)[0]
    # # curves = cmds.animLayer(layer, anc=True, q=True)
    # layer =
    # print(layer)
    # attr = layers.get_objects_from_anim_layer(layer[0])
    # print(attr)
    # # TimeWarp(sel)


class TimeWrap(object):

    def get_selected_object(self):
        objects = cmds.ls(sl=True)
        if not objects:
            om2.MGlobal.displayError("Nothing selected objects")
        return objects

    def get_selected_layer(self):
        layer = layers.get_selected_anim_layers()
        if not layer:
            om2.MGlobal.displayError("Nothing selected layers")

    def warp_object_in_scene(self):
        anim_curves = []
        obj = self.get_selected_object()
        layers_obj = layers.get_affected_layer(obj)
        print(layers_obj)
        if layers_obj:
            for layer in layers_obj:
                layer_curves = layers.get_anim_curves_from_layer(layer)
                anim_curves.append(layer_curves)



class TimeWarpController(object):
    def __init__(self):
        pass

    def warp_curve(self):
        pass

    def warp_layer(self):
        pass

    def warp_object(self):
        pass

    def warp_object_in_layer(self):
        pass


class TimeWarpCurve(object):
    @utils.undoable
    def __init__(self, curves):
        self.curves = curves
        self.start, self.end = self.get_time_range()

        self.create_animCurveTT()
        self.create_timewarp_node()
        self.apply_timewarp()

    def get_time_range(self, wrapped=False):
        return animation.get_playback_range()

    def create_animCurveTT(self):
        self.timewarp_curve = cmds.createNode('animCurveTT', n='timewarp_curve')
        cmds.setKeyframe(self.timewarp_curve, time=self.start, value=self.start, ott='linear')
        cmds.setKeyframe(self.timewarp_curve, time=self.end, value=self.end, itt='linear')
        return self.timewarp_curve

    def create_timewarp_node(self):
        self.timewarp_node = cmds.createNode('timeWarp', n='timewarp_node')
        cmds.connectAttr('{}.output'.format(self.timewarp_curve), '{}.input'.format(self.timewarp_node))
        return self.timewarp_node

    def apply_timewarp(self):
        for curve in self.curves:
            cmds.connectAttr('{}.output'.format(self.timewarp_node), '{}.input'.format(curve))
