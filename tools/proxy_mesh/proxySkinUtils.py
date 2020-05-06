import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om

"""

import pymel.core as pm
import sys
sys.path.append(r'D:\Projects\ProxySkin')
import proxySkinUtils
reload (proxySkinUtils)

test_dup_face()
"""


def test_dup_face():
    face = DuplicateFace()



class Geo:
    def __init__(self):
        pass

    @classmethod
    def get_vertex_from_face(cls, face):
        return cmds.polyListComponentConversion(face, tv=True)

    @classmethod
    def get_face_from_mesh(cls, mesh):
        mesh = pm.PyNode(mesh)
        return mesh.f


class Skin:
    def __init__(self):
        pass

    @classmethod
    def get_history(cls, obj):
        history = cmds.listHistory(obj)
        if history:
            return history

    @classmethod
    def get_skinCluster(cls, obj):
        history = cls.get_history(obj)
        if history:
            skinCluster = [n for n in history if cmds.nodeType(n) == 'skinCluster']
            if skinCluster:
                return skinCluster


class ProxyUtils:
    def __init__(self):
        pass

    @classmethod
    def compareFaces(cls, proxy, source, compare=True):
        target_pos = list(cls.pos_face(pm.ls(source, fl=True)))
        p_pos = list(cls.pos_face(pm.ls(proxy, fl=True)))
        print target_pos
        for p in proxy:
            if compare:
                if list(cls.pos_face(p)) not in target_pos:
                    yield p



            else:
                if p_pos in target_pos:
                    print p, 'not equal', target_pos
                    yield p

    @classmethod
    def center_face(cls, face):
        pt = face.__apimfn__().center(om.MSpace.kWorld)
        return pm.datatypes.Point(pt)



    @classmethod
    def pos_face(cls, face):
        for f in face:
            pos = cls.center_face(f)
            yield pos

class DuplicateFace:

    PREFIX = 'proxy'

    def __init__(self):
        self.source_mesh = None
        self.source_face = None
        self.proxy_mesh = None
        self.proxy_face = None
        self.duplicate_face()

    def select_face(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            self.source_face = sel
            self.source_mesh = self.source_face[0].split('.')[0]

    def duplicate_face(self):
        # select faces
        self.select_face()

        # duplicate mesh
        self.proxy_mesh = cmds.duplicate(self.source_mesh, n='{}_{}'.format(self.source_mesh, 'proxy'))[0]
        self.proxy_face = Geo.get_face_from_mesh(self.proxy_mesh)
        delete_faces = list(ProxyUtils.compareFaces(self.proxy_face, self.source_face, compare=True))
        print delete_faces

        pm.delete(delete_faces)

    # def duplicateFace(self):
    #     """ Duplicate faces """
    #
    #     sel = cmds.ls(sl=True)
    #
    #     try:
    #         isFace = sel[0].split('.f')[1]
    #         if isFace:
    #             self.sourceFace = list(self.flattenList(sel))
    #     except:
    #         cmds.confirmDialog(title='Error', message='Select only polygon faces',
    #                            button=['OK'])
    #         return False
    #
    #     if self.sourceFace:
    #         # Gets name of source obj
    #         sourceObjName = self.sourceFace[0].split('.')[0]
    #         self.sourceMesh = sourceObjName
    #
    #         # Create new name for duplicate object
    #         newName = renamePrefix(name=sourceObjName, prefix='proxy')
    #
    #         # Duplicate obj and set name of duplicate mesh
    #         self.proxyMesh = cmds.duplicate(sourceObjName, n=newName)[0]
    #
    #         # Get all faces from duplicate obj
    #         self.proxyFace = self.getFace(self.proxyMesh)
    #
    #         # Gets faces to delete
    #         delFaces = list(self.compareFaces(self.proxyFace, compare=True, target=self.sourceFace))
    #
    #         cmds.select(delFaces)
    #         listDel = cmds.ls(sl=True)
    #
    #         if listDel:
    #             cmds.delete(listDel)
    #
    #         self.unlockAttr(self.proxyMesh)
    #         cmds.select(self.proxyMesh)
    #
    #         self.face_to_vtx(self.sourceFace, self.proxyFace)
    #
    #         return True
