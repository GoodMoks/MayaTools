import maya.cmds as cmds
import MayaTools.core.mesh as mesh

class DuplicateFace(object):
    @staticmethod
    def filter_face(faces):
        for f in faces:
            if cmds.filterExpand(faces, sm=34):
                yield f

    def __init__(self, faces, prefix='proxy', subtract=False):
        self.faces = faces
        self.prefix = prefix
        self.subtract = subtract

        self.source_mesh = None
        self.source_face = None
        self.proxy_mesh = None
        self.proxy_face = None

        self.start()

    def get_source_components(self):
        source_face = list(self.filter_face(self.faces))
        if source_face:
            self.source_face = source_face
            self.source_mesh = cmds.ls(source_face[0], o=True)[0]

    def start(self):
        """ main """
        self.get_source_components()
        self.duplicate_mesh()
        self.delete_faces()

    def delete_faces(self):
        faces = list(mesh.compare_faces(self.source_face, self.proxy_face, compare=self.subtract))
        cmds.delete(faces)

    def duplicate_mesh(self):
        self.proxy_mesh = cmds.duplicate(self.source_mesh, n='{}_{}'.format(self.source_mesh, self.prefix))[0]
        self.proxy_face = mesh.convert_to_face(self.proxy_mesh)
