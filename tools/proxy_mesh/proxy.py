import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.base as base
import MayaTools.core.mesh as mesh

reload(mesh)

'''
import maya.cmds as cmds
import MayaTools.tools.proxy_mesh.proxy as proxy
reload(proxy)

proxy.Proxy().get_selected_face()


'''


class Proxy(object):
    PREFIX = 'proxy'

    @staticmethod
    def get_selected_face():
        selected = cmds.filterExpand(sm=34)
        if not selected:
            om2.MGlobal.displayError('Nothing selected')

        return selected

    @staticmethod
    def get_position_faces(faces):
        for face in faces:
            position = mesh.get_center_face(face)
            yield position

    def __init__(self):
        self.source_mesh = None
        self.source_face = None
        self.proxy_mesh = None
        self.proxy_face = None

        self.get_source_components()
        self.start()

    def get_source_components(self):
        source_face = self.get_selected_face()
        if source_face:
            self.source_face = source_face
            self.source_mesh = cmds.ls(source_face[0], o=True)[0]

    def start(self):
        """ main """
        self.get_source_components()
        self.duplicate_mesh()
        self.delete_faces()

    def delete_faces(self):
        faces = list(self.compare_faces(self.source_face, self.proxy_face, compare=True))
        cmds.delete(faces)

    def duplicate_mesh(self):
        self.proxy_mesh = cmds.duplicate(self.source_mesh, n='{}_{}'.format(self.source_mesh, self.PREFIX))[0]
        self.proxy_face = mesh.get_faces_from_mesh(self.proxy_mesh)

    def compare_faces(self, source, target, compare=True):
        source_position = list(self.get_position_faces(source))
        target_position = list(self.get_position_faces(target))
        for index, face_position in enumerate(target_position):
            if compare:
                if face_position not in source_position:
                    yield target[index]
            else:
                if face_position in source_position:
                    yield target[index]
