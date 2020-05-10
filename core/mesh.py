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