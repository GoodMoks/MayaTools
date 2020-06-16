import maya.cmds as cmds
import math





def rebuild_curve(crv, smooth=1):
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
