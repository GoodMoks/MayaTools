import maya.cmds as cmds
import pymel.core as pm


class NameParser(object):
    @staticmethod
    def get_namespaces(name):
        all_namespace = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        print(all_namespace)
        in_name = [x for x in all_namespace if x in name]
        return in_name

    def __init__(self, name):
        self.name = name

        self.strip_namespace()

    def is_namespaces(self, name):
        if self.get_namespaces(name):
            return True
        return False

    def strip_namespace(self, level=0):
        maxsplit = level
        if level == 0:
            maxsplit = -1

        all_namespace = self.get_namespaces(self.name)
        print(all_namespace)
        split_name = self.name.split(':', maxsplit)
        print(split_name)
        dif_list = [x for x in split_name if x not in all_namespace]
        print(dif_list)


class IsolateSkeleton(object):
    def __init__(self, obj_top):
        self.obj_top = obj_top
        self.duplicate_objects = None
        self.isolate_parent = None

        self.ref_hierarchy(self.obj_top)
        # self.duplicate_special()

    def strip_namespace(self, obj):
        node = pm.PyNode(obj)
        name = node.stripNamespace()
        return name

    def is_exist_world_name(self, obj):
        root_name = cmds.ls(obj)
        print(root_name)

        if len(root_name):
            world_objects = [x for x in root_name if not cmds.listRelatives(x, ap=True)]
            if world_objects:
                return True
        return False

    def ref_hierarchy(self, top):
        pass

    def duplicate_special(self):
        absolute_name = self.strip_namespace(self.obj_top)
        world_name = self.is_exist_world_name(absolute_name)
        if world_name:
            response = cmds.confirmDialog(
                title='Duplicate?',
                message='There is an object with the same name as the skeleton - "{}"?'.format(absolute_name),
                button=['Okey', 'Ne Okey'],
            )
            if response == 'Ne Okey':
                return False

        self.duplicate_objects = pm.duplicate(self.obj_top, ilf=True, ic=True, po=False, rr=True)
        self.isolate_parent = self.duplicate_objects[0]

        cmds.connectAttr('{}.parentMatrix'.format(self.obj_top), '{}.offsetParentMatrix'.format(self.isolate_parent))
        cmds.parent(self.isolate_parent, w=True)
