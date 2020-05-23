import maya.cmds as cmds
import math
import transform
import attribute


def connect_to_cv(crv=None, step=1, obj_type='joint'):
    if crv:
        curve_info = cmds.createNode('curveInfo', n='{}_info'.format(crv))
        cmds.connectAttr('{}.local'.format(crv), '{}.inputCurve'.format(curve_info))
        points = cmds.getAttr('{}.controlPoints[*]'.format(curve_info))

        objs = []

        if points:
            for point in range(0, len(points), step):
                connect_obj = cmds.createNode(obj_type, n='{}_crv_cv{}'.format(crv, point))
                objs.append(connect_obj)
                cmds.connectAttr('{}.controlPoints[{}]'.format(curve_info, point), '{}.translate'.format(connect_obj))

        group = cmds.createNode('transform', n='{}_crv_objs_grp'.format(crv))
        cmds.parent(objs, group)

        return objs


def merge_cv(surface=None, controls=None):
    """ Merge to one neighborhoods cv's

    :param surface: 'str' surface name
    :param controls: 'list' of controls
    :return:
    """
    if surface and controls:
        len_controls = len(controls)
        pairs_range = range(0, len_controls, 2)
        cv_range = range(len_controls/2)
        for cv, number in zip(pairs_range, cv_range):
            merge_loc = cmds.spaceLocator(n='{}_CTRL_{}'.format(surface, number))
            pos = transform.between_two_object(controls[cv], controls[cv+1])
            cmds.xform(merge_loc, t=(pos[0], pos[1], pos[2]))
            cmds.parent(controls[cv], controls[cv+1], merge_loc)
            attribute.set_attr([controls[cv], controls[cv+1]], 'visibility', 0)

def connect_cv(crv=None, obj=None, merge=False):
    """ Connect cv's to locator or objects

    :param crv: 'list' of cv's
    :param obj: 'list' of controls to connect
    :param merge: 'bool' if crv is loft nurbs, merge cv's to one
    :return: 'list' of controls
    """
    if not crv:
        crv = cmds.ls(sl=True, fl=True)

    if crv:
        if isinstance(crv, basestring):
            crv = [crv]

        controls = []
        for c in crv:
            points = cmds.getAttr('{}.controlPoints[*]'.format(c))
            for cv in range(len(points)):
                if obj and isinstance(obj, list) and len(obj) == len(points):
                    ctrl = obj[cv]
                else:
                    ctrl = cmds.spaceLocator(n='{}_cv{}_loc'.format(c, cv))[0]
                    cv_pos = cmds.xform('{}.cv[{}]'.format(c, cv),
                                       ws=True, t=True, q=True)
                    cmds.xform(ctrl, t=cv_pos)

                controls.append(ctrl)

                decompose = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(ctrl))
                cmds.connectAttr('{}.worldMatrix'.format(ctrl),
                                 '{}.inputMatrix'.format(decompose))
                cmds.connectAttr('{}.outputTranslate'.format(decompose),
                                 '{}.cv[{}]'.format(c, cv))

        if merge:
            merge_cv(surface=crv[0], controls=controls)

        if controls:
            return controls

def curve_from_objects(obj=None):
    """ Create curve from select objects, cv on center obj

    :param obj: 'list' list of objects
    :return: 'str' name os new curve
    """
    if obj:
        num_obj = len(obj)
        if num_obj >= 4:
            degree = 3
        else:
            degree = num_obj - 1

        if degree:
            points = [(0, 0, 0) for x in range(num_obj)]
            curve = cmds.curve(p=points, degree=degree)
            for point, cv in zip(obj, range(num_obj)):
                point_pos = cmds.xform(point, ws=True, t=True, q=True)
                cmds.setAttr('{}.controlPoints[{}]'.format(curve, cv), point_pos[0],
                             point_pos[1],
                             point_pos[2],
                             type='double3')

            if curve:
                return curve

def attach_obj(type='joint', nodes=None, objects=None):
    """ Connect motionPath node to object(locator, joint, pCube, ...)

    :param type: 'str' type nodes
    :param nodes: 'list' of motionPath nodes
    :param objects: 'list' of custom objects to connect
    :return: 'list' attached nodes
    """
    if nodes:
        attach_obj = []
        for node, count in zip(nodes, range(len(nodes))):
            if not objects:
                base_name = node.split('_mPath')[0]
                if not type:
                    type = 'joint'
                obj = cmds.createNode(type, n='{}_Driver'.format(base_name))

                cmds.connectAttr('{}.allCoordinates'.format(node), '{}.translate'.format(obj))
                attach_obj.append(obj)
            else:
                cmds.connectAttr('{}.allCoordinates'.format(node), '{}.translate'.format(objects[count]))
                attach_obj.append(objects[count])

        if attach_obj:
            return attach_obj


# def rebuild_curve(smooth=1, crv=None):
#     if not crv:
#         crv = cmds.ls(sl=True)[0]
#
#     low_CVs = len(cmds.getAttr('{}.controlPoints[*]'.format(crv)))
#     degree = cmds.getAttr('{}.degree'.format(crv))
#     high_CVs = (low_CVs * smooth)
#     high_CVs = math.ceil(high_CVs)
#     points = [(0, 0, 0) for x in range(int(high_CVs))]
#     create_curve = cmds.curve(p=points, degree=degree)
#
#     return create_curve



def rebuild_curve(smooth=1, crv=None):
    low_CVs = len(cmds.getAttr('{}.controlPoints[*]'.format(crv)))
    degree = cmds.getAttr('{}.degree'.format(crv))
    high_CVs = (low_CVs * smooth)
    high_CVs = math.ceil(high_CVs)
    coeff = 1 / float(high_CVs - 1)
    points = [(0, 0, 0) for x in range(int(high_CVs))]
    print '{} points ==============================='.format(len(points))
    create_curve = cmds.curve(p=points, degree=degree)
    slide_curve = cmds.rename(create_curve, '{}_slideCurve'.format(crv))

    u_value = 0
    blend_nodes = []
    mPath= []
    for cv in range(int(high_CVs)):
        motion_path = cmds.createNode('motionPath', n='{}_cv{}_mPath'.format(crv, cv))
        mPath.append(motion_path)
        cmds.setAttr('{}.fractionMode'.format(motion_path), 1)
        cmds.connectAttr('{}.worldSpace'.format(crv), '{}.geometryPath'.format(motion_path))
        cmds.connectAttr('{}.allCoordinates'.format(motion_path), '{}.controlPoints[{}]'.format(slide_curve, cv))
        anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(crv, cv))
        blend_nodes.append(anim_blend)
        cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
        cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(motion_path))
        u_value += coeff

    return_list = dict(
        nodes=blend_nodes,
        curve=slide_curve,
        mPath=mPath
    )

    return return_list
