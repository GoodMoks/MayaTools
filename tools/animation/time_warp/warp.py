import maya.cmds as cmds

import MayaTools.core.animation
import MayaTools.core.animation as animation
import MayaTools.core.base as base
import MayaTools.core.layers
import MayaTools.core.layers as layers
import MayaTools.core.utils as utils
import maya.api.OpenMaya as om2

reload(animation)
reload(layers)
reload(base)
reload(utils)


class TimeWarp(object):
    @staticmethod
    def get_selected_curves():
        """ return selected objects in scene """
        objects = cmds.ls(sl=True, type='animCurve')
        if not objects:
            om2.MGlobal.displayError("Nothing selected animation curves")
        return objects

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
        """ add absolute warp for object

        :param obj: 'list' objects with animations
        :return: 'TimeWarpCurve' object
        """
        anim_curves = []
        for o in obj:
            curves = MayaTools.core.animation.get_all_anim_curves(o)
            if curves:
                anim_curves.extend(curves)

        if anim_curves:
            return TimeWarpCurve(curves=anim_curves)

    @staticmethod
    def warp_layers(layer):
        """ add timeWarp to all anim curves in layers

        Args:
            layer: 'list' animation layers

        Returns: 'TimeWarpCurve' object

        """
        anim_curves = []
        for l in layer:
            if l == 'BaseAnimation':
                om2.MGlobal.displayWarning('TimeWarp do not work for BaseAnimation layer')
                continue

            curves = layers.get_all_curves_from_layer(layer=l)
            if curves:
                anim_curves.extend(curves)

        if anim_curves:
            return TimeWarpCurve(curves=anim_curves)

    @staticmethod
    def warp_curves(curves):
        """ add timeWarp to given animation curves

        Args:
            curves: 'list' animation curves

        Returns: 'TimeWarpCurve' object

        """
        return TimeWarpCurve(curves=curves)

    @staticmethod
    def warp_objects_in_layer(obj, layer):
        """ add timeWarp to object in selected animation layer

        Args:
            obj: 'list' objects with animation
            layer: 'list' animation layers

        Returns: 'TimeWarpCurve' object

        """
        anim_curves = []
        for o in obj:
            for l in layer:
                if not layers.object_in_layer(obj=o, layer=l):
                    om2.MGlobal.displayInfo("{} don't have curves in {} layer".format(o, l))
                    continue

                curves = layers.get_obj_curves_from_layer(obj=o, layer=l)
                if curves:
                    anim_curves.extend(curves)

        return TimeWarpCurve(curves=anim_curves)

    @staticmethod
    def bake_time_warp(warp_node):
        """ bake timeWarp and delete node

        Args:
            warp_node: 'str' name of 'timeWarp' node

        """
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

    @staticmethod
    def warp_curves():
        selected_curves = TimeWarp.get_selected_curves()
        if not selected_curves:
            return

        TimeWarp.warp_curves(curves=selected_curves)

    @staticmethod
    def warp_objects_in_layer():
        selected_obj = TimeWarp.get_selected_object()
        selected_layer = TimeWarp.get_selected_layer()
        if not selected_obj or not selected_layer:
            return

        TimeWarp().warp_objects_in_layer(obj=selected_obj, layer=selected_layer)

    @staticmethod
    def warp_attributes():
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
