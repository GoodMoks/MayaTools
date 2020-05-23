import maya.cmds as cmds
import attribute


def find_param(surface=None, position=None, normalize=True):
    """ Get parameter from a position on curve/surface/mesh

    :param surface: 'string' name of surface or curve
    :param position: 'list of float' Represents the position in worldSpace
           exp: [1.4, 3.55, 42.6]
    :return: 'dict' parameters and position in world
           exp: {'position': [(-0.5, 0.0, -0.5)],
                 'v_param': None,
                 'u_param': None,
                 'param': 1.0} - 'param' only for curves
    """
    if surface and position:
        if isinstance(surface, basestring) and isinstance(position, list):
            type_obj = cmds.objectType(cmds.listRelatives(surface, shapes=True)[0])
            node_dict = dict(
                nurbsCurve=['nearestPointOnCurve', '.worldSpace',
                            '.inputCurve', '.parameter'],
                nurbsSurface=['closestPointOnSurface', '.local',
                              '.inputSurface', '.parameterU', '.parameterV'],
                mesh=['closestPointOnMesh', '.outMesh',
                      '.inMesh', '.parameterU', '.parameterV']
            )
            param_dict = dict(
                param=None,
                u_param=None,
                v_param=None,
                position=None,
                object_type=type_obj
            )

            nodes = [value for x, value in node_dict.iteritems() if type_obj == x][0]
            node = cmds.createNode(nodes[0])
            cmds.connectAttr('{}{}'.format(surface, nodes[1]), '{}{}'.format(node, nodes[2]))
            cmds.setAttr('{}.inPosition'.format(node), position[0], position[1], position[2], type='double3')

            if len(nodes) == 5:
                # normalize uv
                u_param = cmds.getAttr('{}{}'.format(node, nodes[3]))
                v_param = cmds.getAttr('{}{}'.format(node, nodes[4]))

                if type_obj == 'nurbsSurface' and normalize:
                    min_max_u = cmds.getAttr('{}.minMaxRangeU'.format(surface))[0]
                    min_max_v = cmds.getAttr('{}.minMaxRangeV'.format(surface))[0]
                    u_param = abs((u_param - min_max_u[0]) / (min_max_u[1] - min_max_u[0]))
                    v_param = abs((v_param - min_max_v[0]) / (min_max_v[1] - min_max_v[0]))

                param_dict['u_param'] = u_param
                param_dict['v_param'] = v_param
            else:
                param_dict['param'] = cmds.getAttr('{}{}'.format(node, nodes[3]))

            param_dict['position'] = cmds.getAttr('{}.position'.format(node))
            cmds.delete(node)
            return param_dict


def follicle_rivet(surface=None, obj=None):
    """ Create follicle on the surface and connect to obj

    :param surface: 'str' name of surface
    :param obj: 'str' transform obj
    :return: 'str' created follicle on surface
    """
    flc_group = '{}_flc_grp'.format(surface)
    if not cmds.objExists(flc_group):
        flc_group = cmds.createNode('transform', n=flc_group)
    flc = cmds.createNode('transform', n='{}_{}_flcs'.format(surface, obj), p=flc_group)
    flc_shape = cmds.createNode('follicle', n='{}Shape'.format(flc), p=flc)
    cmds.connectAttr('{}.outTranslate'.format(flc_shape), '{}.translate'.format(flc))
    cmds.connectAttr('{}.outRotate'.format(flc_shape), '{}.rotate'.format(flc))
    cmds.setAttr('{}.inheritsTransform'.format(flc), 0)

    # connect surface to follicle
    try:
        cmds.connectAttr('{}.outMesh'.format(surface), '{}.inputMesh'.format(flc_shape))
    except:
        cmds.connectAttr('{}.local'.format(surface), '{}.inputSurface'.format(flc_shape))

    cmds.connectAttr('{}.worldMatrix'.format(surface), '{}.inputWorldMatrix'.format(flc_shape))
    cmds.connectAttr('{}.Parameter_U'.format(obj), '{}.parameterU'.format(flc_shape))
    cmds.connectAttr('{}.Parameter_V'.format(obj), '{}.parameterV'.format(flc_shape))

    # return follicle
    return flc


def matrix_rivet(surface=None, obj=None, normalize=True):
    """ Create rivet based on fourByFour node

    :param surface: 'str' name of surface
    :param obj: 'str' transform obj
    :return: 'str' decompose node
    """
    # create nodes
    pos_node = cmds.createNode('pointOnSurfaceInfo', n='{}_pos_node'.format(obj))
    four_node = cmds.createNode('fourByFourMatrix', n='{}_four_node'.format(obj))
    dec_node = cmds.createNode('decomposeMatrix', n='{}_dec_node'.format(obj))

    # connect surface and obj attr
    cmds.connectAttr('{}.worldSpace'.format(surface), '{}.inputSurface'.format(pos_node))
    cmds.connectAttr('{}.Parameter_U'.format(obj), '{}.parameterU'.format(pos_node))
    cmds.connectAttr('{}.Parameter_V'.format(obj), '{}.parameterV'.format(pos_node))

    cmds.setAttr('{}.turnOnPercentage'.format(pos_node), normalize)

    # connect four nodes
    four_attr = ['normalizedNormal', 'normalizedTangentU', 'normalizedTangentV', 'position']
    for item_attr, attr in enumerate(four_attr):
        coord_list = ['X', 'Y', 'Z']
        for item_coord, coord in enumerate(coord_list):
            cmds.connectAttr('{}.{}{}'.format(pos_node, attr, coord),
                             '{}.in{}{}'.format(four_node, item_attr, item_coord))

    # connect obj
    cmds.connectAttr('{}.output'.format(four_node), '{}.inputMatrix'.format(dec_node))

    # return decompose node
    return dec_node


def surface_rivet(surface=None, obj=None,
                  rotate=True, translate=True,
                  offset=False, offsetParent=False,
                  follicle=False, normalize=True):
    if surface and obj:
        if follicle:
            normalize = True
        else:
            normalize = False

        nodes = []
        # get closest point and parameters on mesh
        pos = cmds.xform(obj, q=True, ws=True, rp=True)
        param = find_param(surface=surface, position=pos, normalize=normalize)
        if offset and not follicle and not param['object_type'] == 'mesh':
            offset_group_name = '{}_rivet_grp'.format(surface)
            if not cmds.objExists(offset_group_name):
                cmds.createNode('transform', n=offset_group_name)
            cmds.setAttr('{}.inheritsTransform'.format(offset_group_name), 0)
            connect_obj = cmds.createNode('transform', n='{}_{}_rivet'.format(surface, obj), p=offset_group_name)
        else:
            connect_obj = obj

        # add attr
        attr_list = ['Parameter_U', 'Parameter_V']
        attribute.delete_attr(obj, attr_list, force=True)
        cmds.addAttr(obj, ln=attr_list[0], at='double', dv=param['u_param'], k=True)
        cmds.addAttr(obj, ln=attr_list[1], at='double', dv=param['v_param'], k=True)

        # only for nurbsSurface
        if not follicle and not param['object_type'] == 'mesh':
            node = matrix_rivet(surface=surface, obj=obj, normalize=normalize)
            nodes.append(node)
            if node:
                if translate:
                    cmds.connectAttr('{}.outputTranslate'.format(node), '{}.translate'.format(connect_obj))
                if rotate:
                    cmds.connectAttr('{}.outputRotate'.format(node), '{}.rotate'.format(connect_obj))

        if follicle or param['object_type'] == 'mesh':
            follicle = follicle_rivet(surface=surface, obj=obj)
            nodes.append(follicle)
            if not offset:
                if translate:
                    cmds.connectAttr('{}.translate'.format(follicle), '{}.translate'.format(connect_obj))
                if rotate:
                    cmds.connectAttr('{}.rotate'.format(follicle), '{}.rotate'.format(connect_obj))

        if offset and not offsetParent:
            if follicle:
                cmds.parent(obj, follicle)
            else:
                cmds.parent(obj, connect_obj)

        if offset and offsetParent:
            if follicle:
                cmds.parentConstraint(follicle, obj, mo=True)
            else:
                cmds.parentConstraint(connect_obj, obj, mo=True)

        return nodes


def length_param(curve=None, value=None):
    if curve:
        arc_node = cmds.createNode('arcLengthDimension', n='arc_node')
        max_value_u = list(cmds.getAttr('{}.minMaxValue'.format(curve)))[0]
        cmds.connectAttr('{}.local'.format(curve), '{}.nurbsGeometry'.format(arc_node))
        cmds.setAttr('{}.uParamValue'.format(arc_node), value)
        arc_length = cmds.getAttr('{}.arcLength'.format(arc_node))
        cmds.setAttr('{}.uParamValue'.format(arc_node), max_value_u[1])
        length = cmds.getAttr('{}.arcLength'.format(arc_node))
        non_uniform_value = arc_length / length
        cmds.delete('arc_node')
        cmds.delete('arcLengthDimension1')
        return non_uniform_value


def m_path_rivet(curve=None,
                 obj=None, fraction=False,
                 offset=False, offsetParent=False):
    """ Attach object for nurbsCurve

    :param curve: 'str' curve
    :param obj: 'str' transform obj
    :param fraction: 'bool' parametric length or not
    :param offset: 'bool' attach with offset group
    :param offsetParent: 'bool' use parentConstraint
    :return: 'list' list of motionPath nodes
    """
    pos = cmds.xform(obj, q=True, ws=True, rp=True)
    parameters = find_param(surface=curve, position=pos)
    param = length_param(curve=curve, value=parameters['param'])
    fraction_value = 1
    if fraction:
        param = parameters['param']
        fraction_value = 0

    attr_list = ['Parameter_U']
    attribute.delete_attr(obj, attr_list, force=True)
    cmds.addAttr(obj, ln=attr_list[0], at='double', dv=param, k=True)

    if offset:
        offset_group_name = '{}_rivet_grp'.format(curve)
        if not cmds.objExists(offset_group_name):
            cmds.createNode('transform', n=offset_group_name)
        cmds.setAttr('{}.inheritsTransform'.format(offset_group_name), 0)
        connect_obj = cmds.createNode('transform', n='{}_{}_rivet'.format(curve, obj), p=offset_group_name)
    else:
        connect_obj = obj

    m_path = cmds.createNode('motionPath', n='{}_mPath'.format(obj))
    cmds.setAttr('{}.fractionMode'.format(m_path), fraction_value)
    cmds.connectAttr('{}.worldSpace'.format(curve), '{}.geometryPath'.format(m_path))
    cmds.connectAttr('{}.Parameter_U'.format(obj), '{}.uValue'.format(m_path))
    cmds.connectAttr('{}.allCoordinates'.format(m_path), '{}.translate'.format(connect_obj))

    if offset and not offsetParent:
        cmds.parent(obj, connect_obj)

    if offset and offsetParent:
        cmds.parentConstraint(connect_obj, obj, mo=True)

    return m_path


def apply_rivet(surface=None, obj=None,
                rotate=True, translate=True,
                offset=False, offsetParent=False,
                follicle=False, fraction=False):
    """ Main process module

    Create rivet on any surface

    :param surface: 'str' surface
    :param obj: 'list' objects
    :param rotate: 'bool' connect rotate channel or not
    :param translate: 'bool' connect translate channel or not
    :param offset: 'bool' rivet with group offset
    :param offsetParent: 'bool' parentConstraint offset (if True offset)
    :param follicle: 'bool' use follicle or not
    :param fraction: 'bool' parametrize node (only for mPath build)
    :return: 'list' list of rivet nodes
    """
    if not surface and not obj:
        sel = cmds.ls(sl=True, fl=True)
        if sel >= 2:
            obj = sel[:-1]
            surface = sel[-1]

    if surface and obj:
        nodes = []
        surface_type = cmds.objectType(cmds.listRelatives(surface, shapes=True)[0])
        if not surface_type == 'nurbsCurve':
            for o in obj:
                node = surface_rivet(surface=surface, obj=o,
                                     rotate=rotate, translate=translate,
                                     offset=offset, offsetParent=offsetParent,
                                     follicle=follicle)
                nodes.append(node)
        if surface_type == 'nurbsCurve':
            for o in obj:
                node = m_path_rivet(curve=surface,
                                    obj=o, fraction=fraction,
                                    offset=offset, offsetParent=offsetParent)
                nodes.append(node)

        if nodes:
            return nodes
