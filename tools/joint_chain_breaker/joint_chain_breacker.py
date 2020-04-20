import pymel.core as pm
import maya.OpenMaya as om


def list_of_jnt():
    # returns list of selected objects

    sel_jnt = pm.selected()

    if len(sel_jnt) != 2:
        om.MGlobal.displayError("Select two joint to add joints between them")
        return

    return sel_jnt


def get_transform(obj=None):
    # returns transformation MVector of given object

    xtr = pm.xform(obj, q=True, piv=True, ws=True)
    mv = om.MVector(xtr[0], xtr[1], xtr[2])

    return mv


def vector_divide(v, dp):
    # divide given vector
    div_distance = v / dp

    return div_distance


def get_oriente(obj):
    # returns orient of given object
    rotation = pm.xform(obj, q=True, ro=True, ws=True)
    rv = om.MVector(rotation[0], rotation[1], rotation[2])

    return rv


def create_jnt(v, par):
    rv = get_oriente(par)
    pm.select(cl=True)
    joint = pm.joint(p=(v.x, v.y, v.z), o=(rv.x, rv.y, rv.z))
    return joint


def insert_jnt(v, div_dist, dp, par):
    added_jnt = []

    for i in range(dp - 1):
        v += div_dist
        jnt = create_jnt(v, par)
        added_jnt.append(jnt)

    return added_jnt


def parent_jnt(par, chain, ch):
    for i in range(len(chain) - 1):
        pm.parent(chain[i], chain[i + 1])

    pm.parent(chain[-1], par)
    pm.parent(ch, chain[0])
