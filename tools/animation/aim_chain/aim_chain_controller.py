import re
import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.animation as animation
import MayaTools.core.dag as dag
import aim_chain


class AimChainController(object):
    @staticmethod
    def bake_result(obj):
        pm.bakeResults(obj, t=(animation.get_playback_range()), simulation=True)

    @staticmethod
    def make_locator(obj, prefix):
        loc = pm.spaceLocator(n='{}_{}_loc'.format(obj, prefix))
        return loc

    @staticmethod
    def get_selected():
        sel = pm.selected()
        if not sel:
            om.MGlobal.displayError('Nothing selected')
            return None
        return sel

    def bake_chain(self):
        selected = self.get_selected()
        if selected:
            self.bake_result(selected)
            try:
                pm.delete('aim_chain')
                pm.delete('{}_proxy_1'.format(selected[0]))
            except:
                pass

    def bake_proxy(self):
        selected = self.get_selected()
        if selected:
            origin_joints = []
            proxy_joints = []
            for proxy in selected:
                match = re.findall(pattern='proxy', string=str(proxy))
                if match:
                    splits = proxy.split('_proxy_')
                    joint = splits[0]
                    if pm.objExists(joint):
                        origin_joints.append(joint)

                    proxy_joints.append(proxy)

            self.bake_result(origin_joints)
            pm.delete(proxy_joints)
            try:
                pm.delete('aim_chain')
            except:
                pass

    def build_aim_chain(self, axis):
        selected = self.get_selected()
        if selected:
            aim_chain.AimChain(controls=selected, axis=axis)

    def proxy_chain(self, objects=None):
        if not objects:
            objects = self.get_selected()

        if objects:
            new_objects = []
            temp_constraints = []
            for index in range(len(objects)):
                obj_name = '{}_{}_{}'.format(objects[index], 'proxy', index + 1)
                if pm.objExists(obj_name):
                    continue
                obj = pm.createNode('joint', n=obj_name)
                pm.setAttr('{}.radius'.format(obj), 1.5)

                new_objects.append(obj)
                try:
                    pm.parent(obj, new_objects[index - 1])
                except:
                    pass

                temp_constraints.append(pm.parentConstraint(objects[index], obj, mo=False))

            parent = dag.get_parent(str(objects[0]))
            print(parent)
            pm.parent(new_objects[0], parent)
            self.bake_result(new_objects)
            pm.delete(temp_constraints)

            for index in range(len(new_objects)):
                try:
                    pm.parentConstraint(new_objects[index], objects[index], mo=True)
                except:
                    pass

            return new_objects