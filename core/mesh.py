import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.base as base
import re


def is_face(component):
    """ check component for face

    :param component: 'list' of components
    :return: new 'list' only with faces
    """
    return cmds.filterExpand(component, ex=True, sm=34)


def get_center_face(face):
    """ get world position given face

    :param face: 'str' face component
    :return: [x, y, z] vector
    """
    index = re.findall(r"[\w]+", face)[2]
    m_obj = base.get_MObject(face)
    face_iter = om2.MItMeshPolygon(m_obj)
    face_iter.setIndex(int(index))
    vector = face_iter.center()
    return [round(vector.x, 5), round(vector.y, 5), round(vector.z, 5)]


def compare_faces(source, target, compare=True):
    """ compare two list of faces

    :param source: 'list' faces
    :param target: 'list' faces
    :param compare: 'bool' True: return different, False: return identical faces
    :return: 'generator'
    """
    source_position = list(get_position_faces(source))
    target_position = list(get_position_faces(target))
    for index, face_position in enumerate(target_position):
        if compare:
            if face_position in source_position:
                yield target[index]
        else:
            if face_position not in source_position:
                yield target[index]


def get_position_faces(faces):
    """ get list of all position faces

    :param faces: 'list' faces
    :return: 'generator' with all position
    """
    for face in faces:
        position = get_center_face(face)
        yield position


def convert_to_face(faces):
    """ convert any poly object to face

    :param faces: 'list' or 'str' object
    :return: 'list' with faces
    """
    return cmds.ls(cmds.polyListComponentConversion(faces, tf=True), fl=True)


def convert_to_vrt(faces):
    """ convert any poly object to vtx

        :param faces: 'list' or 'str' object
        :return: 'list' with vtx
    """
    return cmds.ls(cmds.polyListComponentConversion(faces, tv=True), fl=True)


def get_closest_UV_mesh(mesh, point):
    """ get UV parameter from closest point

    :param surface: 'str' mesh
    :param point: 'vector' (1.0, 1.0, 1.0)
    :return:
    """
    new_mesh = cmds.duplicate(mesh)[0]
    cmds.makeIdentity(mesh, apply=True)
    surface_dag_path = base.get_dagPath(new_mesh)
    surface_fn = om2.MFnMesh(surface_dag_path)
    cmds.delete(new_mesh)
    return surface_fn.getUVAtPoint(om2.MPoint(point), om2.MSpace.kWorld)


def get_closest_face_index(mesh, point):
    """ get closest index face and closest world point on mesh

    :param mesh: 'str' mesh
    :param point: 'list' [1.0, 1.0, 1.0]
    :return: MPoint 'tuple' (maya.api.OpenMaya.MPoint(0.31351384520530700684, 0.94919389486312866211, 0, 1), 338)
    """
    point = cmds.xform(point, q=True, ws=True, rp=True)
    surface_dag_path = base.get_dagPath(mesh)
    surface_fn = om2.MFnMesh(surface_dag_path)
    point = om2.MPoint(point)
    face = surface_fn.getClosestPoint(point, om2.MSpace.kWorld)
    return face


class ClosestMeshComponent(object):
    def __init__(self, mesh, point, space=om2.MSpace.kWorld):
        self.mesh = mesh
        self.point = om2.MPoint(point)
        self.space = space

        self.create_MFnMesh()

    def create_MFnMesh(self):
        self.mesh_dag_path = base.get_dagPath(self.mesh)
        self.mesh_fn = om2.MFnMesh(self.mesh_dag_path)
        return self.mesh_fn

    def closest_face(self):
        self.face = self.mesh_fn.getClosestPoint(self.point, om2.MSpace.kWorld)
        return self.face

    def get_closest_perimeter_edge(self):
        face = self.closest_face()
        face_iter = om2.MItMeshPolygon(self.mesh_dag_path)
        face_iter.setIndex(face[1])
        self.edges_perimeter = face_iter.getEdges()
        return self.edges_perimeter

    def closest_edge(self):
        edges = self.get_closest_perimeter_edge()
        self.edge_MItEdge = om2.MItMeshEdge(self.mesh_dag_path)
        self.closest_edge_index = None
        distance = 99999
        for e in edges:
            self.edge_MItEdge.setIndex(e)
            edge_center = self.edge_MItEdge.center(om2.MSpace.kWorld)
            edge_dist = (edge_center - self.point).length()
            if edge_dist < distance:
                self.closest_edge_index = e
                distance = edge_dist
        return self.closest_edge_index

    def get_opposite_closest_edge(self):
        self.closest_edge()
        self.edge_MItEdge.setIndex(self.closest_edge_index)
        self.opposite_edge = None
        for e in self.edges_perimeter:
            if not e == self.closest_edge_index:
                self.opposite_edge = e
            if not self.edge_MItEdge.connectedToEdge(e):
                break

        return self.opposite_edge