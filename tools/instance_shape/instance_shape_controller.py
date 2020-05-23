import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.dag as dag

import instance_shape


class InstanceShapeController(object):
    @staticmethod
    def get_selected():
        selected = pm.selected()
        if not selected:
            om.MGlobal.displayError('Nothing selected')
            return

        return selected

    @staticmethod
    def input_shape_name():
        try:
            input = raw_input()
        except:
            om.MGlobal.displayError('You did not enter an object name')
            return None

        return input

    @staticmethod
    def get_full_path(instance):
        objects = pm.ls(instance, ap=True)
        if len(objects) == 1:
            parent = dag.get_parent('{}'.format(objects[0]))
            if parent:
                return ['{}|{}'.format(parent[0], instance)]
        return objects

    @staticmethod
    def delete_instance(items):
        for i in items:
            pm.delete(i.text())

    @staticmethod
    def select_item(items):
        pm.select(cl=True)
        for item in items:
            try:
                pm.select(item.text(), add=True)
            except:
                pass

    @staticmethod
    def get_shapes_instance(obj):
        return [x.split('|')[-1] for x in dag.get_shapes('{}'.format(obj))]

    def __init__(self):
        pass

    def make_instance(self):
        selected = self.get_selected()
        if selected:
            name = self.input_shape_name()
            if not name:
                return

            instance_shape.InstanceShape(selected, name)

    def delete_object(self, objects, instance):
        for obj in objects:
            if instance in self.get_shapes_instance(obj.text()):
                path = '{}|{}'.format(obj.text(), instance)
                pm.parent(path, rm=True, s=True)

    def add_instance(self, objects, instance):
        for obj in objects:
            if instance not in self.get_shapes_instance(obj):
                instance_shape.Instance(obj, instance)
