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



class TimeWarp(object):
    wrap_curves = None

    def get_selected_object(self):
        objects = cmds.ls(sl=True)
        if not objects:
            om2.MGlobal.displayError("Nothing selected objects")
        return objects

    def get_selected_layer(self):
        """  """
        layer = layers.get_selected_anim_layers()
        if not layer:
            om2.MGlobal.displayError("Nothing selected layers")
        return layer

    def warp_object_in_scene(self, obj):
        anim_curves = []
        layers_obj = layers.get_affected_layer(obj=obj)
        if not layers_obj:
            return

        for layer in layers_obj:
            anim_curves.extend(layers.get_anim_curves_from_layer(layer=layer, obj=obj))

        anim_curves.extend(cmds.listConnections(obj, t='animCurve'))

        self.warp_curves = TimeWarpCurve(curves=anim_curves)

    def test(self):
        obj = self.get_selected_object()
        if not obj:
            return

        layers.get_base_anim_layer_curves(obj[0])

    def warp_layer(self):
        objects = []
        selected_layers = self.get_selected_layer()
        if not selected_layers:
            return

        print(selected_layers)

        for layer in selected_layers:
            layer_objects = layers.get_objects_from_layer(layer=layer)
            print(layer_objects)
            objects.extend(objects)

    def bake(self):
        if not self.warp_curves:
            return

        warp_node = self.warp_curves.timewarp_node

        curves = cmds.listConnections('{}.output'.format(warp_node))
        bake_attributes = [cmds.listConnections('{}.output'.format(curve), p=True) for curve in curves]
        flatten_list = [i for x in bake_attributes for i in x]
        time_range = TimeWarpCurve.get_time_range()
        cmds.bakeResults(flatten_list, time=[time_range], simulation=True, smart=True)


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
    @staticmethod
    def get_time_range(wrapped=False):
        return animation.get_playback_range()

    @utils.undoable
    def __init__(self, curves):
        self.curves = curves
        self.start, self.end = self.get_time_range()

        self.create_animCurveTT()
        self.create_timewarp_node()
        self.apply_timewarp()

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
