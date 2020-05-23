import maya.cmds as cmds
import MayaTools.core.base as base
import maya.api.OpenMaya as om2


def merge_cv(surface=None, controls=None):  # WIP
    """ Merge to one neighborhoods cv's

    :param surface: 'str' surface name
    :param controls: 'list' of controls
    :return:
    """
    if surface and controls:
        len_controls = len(controls)
        pairs_range = range(0, len_controls, 2)
        cv_range = range(len_controls / 2)
        for cv, number in zip(pairs_range, cv_range):
            merge_loc = cmds.spaceLocator(n='{}_CTRL_{}'.format(surface, number))
            pos = transform.between_two_object(controls[cv], controls[cv + 1])
            cmds.xform(merge_loc, t=(pos[0], pos[1], pos[2]))
            cmds.parent(controls[cv], controls[cv + 1], merge_loc)
            attribute.set_attr([controls[cv], controls[cv + 1]], 'visibility', 0)






def get_closest_UV_surface(surface, point, normalize=True):
    """ get UV parameter from closest point

    :param surface: 'str' nurbs surface
    :param point: 'vector' (1.0, 1.0, 1.0)
    :return:
    """
    new_surface = cmds.duplicate(surface)[0]
    cmds.makeIdentity(new_surface, apply=True)

    surface_dag_path = base.get_dagPath(new_surface)
    surface_fn = om2.MFnNurbsSurface(surface_dag_path)
    point = om2.MPoint(point)
    param = surface_fn.getParamAtPoint(point, True, tolerance=100, space=om2.MSpace.kWorld)

    cmds.delete(new_surface)
    if not normalize:
        return param

    min_max_u = cmds.getAttr('{}.minMaxRangeU'.format(surface))[0]
    min_max_v = cmds.getAttr('{}.minMaxRangeV'.format(surface))[0]
    u_param = abs((param[0] - min_max_u[0]) / (min_max_u[1] - min_max_u[0]))
    v_param = abs((param[1] - min_max_v[0]) / (min_max_v[1] - min_max_v[0]))
    return u_param, v_param
