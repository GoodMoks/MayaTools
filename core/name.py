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


def strip_namespace(obj):
    node = pm.PyNode(obj)
    name = node.stripNamespace()
    return str(name)
