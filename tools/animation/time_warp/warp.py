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
    @staticmethod
    def get_selected_object():
        """ return selected objects in scene """
        objects = cmds.ls(sl=True)
        if not objects:
            om2.MGlobal.displayError("Nothing selected objects")
        return objects

    @staticmethod
    def get_selected_layer():
        """  return selected layer in scene """
        layer = layers.get_selected_anim_layers()
        if not layer:
            om2.MGlobal.displayError("Nothing selected layers")
        return layer

    @staticmethod
    def warp_objects(obj):
        """ add warp

        :param obj: 'list' objects with animations
        :return: 'TimeWarpCurve' object
        """
        anim_curves = []
        for o in obj:
            curves = animation.get_all_anim_curves(o)
            if curves:
                anim_curves.extend(curves)

        if anim_curves:
            return TimeWarpCurve(curves=anim_curves)

    @staticmethod
    def warp_layers(layer):
        anim_curves = []
        layer_objects = layers.get_objects_from_layer(layer=layer)
        if layer_objects:
            for obj in layer_objects:
                curves = layers.get_curves_object_from_layer(layer=layer, obj=obj)
                anim_curves.extend(curves)



    def bake(self, warp_node):
        curves = cmds.listConnections('{}.output'.format(warp_node))
        bake_attributes = [cmds.listConnections('{}.output'.format(curve), p=True) for curve in curves]
        flatten_list = [i for x in bake_attributes for i in x]
        time_range = TimeWarpCurve.get_time_range()
        cmds.bakeResults(flatten_list, time=[time_range], simulation=True, smart=True)


class TimeWarpController(object):
    @staticmethod
    def warp_objects():
        selected_obj = TimeWarp.get_selected_object()
        if not selected_obj:
            return

        TimeWarp.warp_objects(selected_obj)

    @staticmethod
    def warp_layers():
        selected_layers = TimeWarp.get_selected_layer()
        if not selected_layers:
            return

        TimeWarp.warp_layers(layer=selected_layers)

    def __init__(self):
        pass

    def warp_curves(self):
        pass

    def warp_objects_in_layer(self):
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
