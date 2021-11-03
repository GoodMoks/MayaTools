import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.tools.skin.proxy_mesh.duplicate_face as duplicate_face
import MayaTools.core.skin as skin
import MayaTools.core.mesh as mesh

'''
import maya.cmds as cmds
import MayaTools.tools.proxy_mesh.proxy as proxy
reload(proxy)

proxy.Proxy().get_selected_face()


'''


class ProxyController(object):

    @staticmethod
    def get_selected_face():
        selected = cmds.filterExpand(sm=34)
        if not selected:
            om2.MGlobal.displayError('Nothing selected')
            return None
        return selected

    @staticmethod
    def get_selected():
        selected = cmds.ls(sl=True, o=True)
        if not selected:
            om2.MGlobal.displayError('Nothing selected')
            return None
        if not len(selected) == 2:
            om2.MGlobal.displayError('Please select 2 objects, first source mesh, second target mesh')
            return None

        return selected

    @staticmethod
    def restore_skin(source, target):
        skin.restore_skin(source, target)

    @staticmethod
    def transfer_skin(source, target):
        source_faces = mesh.convert_to_face(source)
        target_faces = mesh.convert_to_face(target)
        compare_faces = list(mesh.compare_faces(source_faces, target_faces, compare=True))

        source_vertex = mesh.convert_to_vrt(source_faces)
        target_vertex = mesh.convert_to_vrt(compare_faces)

        skin.copy_skin(source_vertex, target_vertex)

    def __init__(self):
        pass

    def get_different_joints(self):
        selected = self.get_selected()
        if not selected:
            return False

        source, target = selected
        source_joints = set(skin.get_influence_joint(source))
        target_joints = set(skin.get_influence_joint(target))
        source_dif = list(source_joints.difference(target_joints))
        target_dif = list(target_joints.difference(source_joints))
        return [[source, source_dif], [target, target_dif]]

    def get_dif_face(self):
        pass

    def copy_skin(self):
        selected = self.get_selected()
        if selected:
            if not skin.get_skinCluster(selected[0]):
                om2.MGlobal.displayError('{} since it is not a skinned object'.format(selected[0]))
                return False

            if not skin.get_skinCluster(selected[1]):
                om2.MGlobal.displayError('{} since it is not a skinned object'.format(selected[1]))
                return False

            if not skin.compare_influence_joints(selected[0], selected[1]):
                om2.MGlobal.displayError('Skinned joints is not equal')
                return False

            self.transfer_skin(selected[0], selected[1])

        cmds.select(selected)

    def duplicate_faces(self):
        faces = self.get_selected_face()
        if not faces:
            cmds.select(faces)
            return False

        new_mesh = duplicate_face.DuplicateFace(faces)
        self.restore_skin(new_mesh.source_mesh, new_mesh.proxy_mesh)

        cmds.select(new_mesh.proxy_mesh)
