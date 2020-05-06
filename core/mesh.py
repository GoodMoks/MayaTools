import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.base as base
import re


def is_face(component):
    return cmds.filterExpand(component, ex=True, sm=34)


def get_faces_from_mesh(obj):
    faces = cmds.polyListComponentConversion(obj, tf=True)
    return cmds.ls(faces, fl=True)


def get_center_face(face):
    index = re.findall(r"[\w]+", face)[2]
    m_obj = base.get_MObject(face)
    face_iter = om2.MItMeshPolygon(m_obj)
    face_iter.setIndex(int(index))
    vector = face_iter.center()
    return [vector.x, vector.y, vector.z]
