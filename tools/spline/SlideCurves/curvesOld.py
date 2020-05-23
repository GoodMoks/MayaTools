import maya.cmds as cmds


def info_Node(crv=None):
    if crv and cmds.objExists(crv):
        name_node = '{}_Info'.format(crv)
        if not cmds.objExists(name_node):
            node = cmds.createNode('curveInfo', n=name_node)
            cmds.connectAttr('{}.worldSpace'.format(crv), '{}.inputCurve'.format(node))
            return node
        else:
            print '{} already exists'.format(name_node)
            return name_node


def stretch_build(low=None, high=None, nodes=None):
    if low and high and nodes:

        Control = low

        cmds.addAttr(Control, ln='StretchMax', at='double', min=1, dv=1, k=True)
        cmds.addAttr(Control, ln='StretchMin', at='double', min=0, max=1, dv=1, k=True)
        cmds.addAttr(Control, ln='Length', at='double', dv=1, k=True)
        cmds.addAttr(Control, ln='Position', at='double', min=0, max=1, dv=0, k=True)

        low_info_node = info_Node(low)
        length_div = cmds.createNode('multiplyDivide', n='{}_lengthDiv'.format(low))
        length = cmds.getAttr('{}.arcLength'.format(low_info_node))
        cmds.setAttr('{}.operation'.format(length_div), 2)
        cmds.setAttr('{}.input1X'.format(length_div), length)
        cmds.setAttr('{}.input2Y'.format(length_div), length)
        cmds.connectAttr('{}.arcLength'.format(low_info_node), '{}.input1Y'.format(length_div))
        cmds.connectAttr('{}.arcLength'.format(low_info_node), '{}.input2X'.format(length_div))
        min_cond = cmds.createNode('condition', n='{}_minCond'.format(low))
        max_cond = cmds.createNode('condition', n='{}_maxCond'.format(low))
        main_cond = cmds.createNode('condition', n='{}_mainCond'.format(low))

        #min node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.secondTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(Control), '{}.firstTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(Control), '{}.colorIfTrueR'.format(min_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(min_cond))
        cmds.setAttr('{}.operation'.format(min_cond), 3)

        #max node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(Control), '{}.secondTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(Control), '{}.colorIfTrueR'.format(max_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(max_cond))
        cmds.setAttr('{}.operation'.format(max_cond), 3)

        #main node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(min_cond), '{}.colorIfFalseR'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(max_cond), '{}.colorIfTrueR'.format(main_cond))
        cmds.setAttr('{}.secondTerm'.format(main_cond), 1)
        cmds.setAttr('{}.operation'.format(main_cond), 2)

        length_AddMinus = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(low))
        cmds.connectAttr('{}.Length'.format(Control), '{}.input1'.format(length_AddMinus))
        cmds.setAttr('{}.input2 '.format(length_AddMinus), -1)

        length_AddDouble = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(low))
        cmds.connectAttr('{}.outColorR'.format(main_cond), '{}.input1'.format(length_AddDouble))
        cmds.connectAttr('{}.output'.format(length_AddMinus), '{}.input2'.format(length_AddDouble))

        mult_coef = cmds.createNode('multDoubleLinear', n='{}_multCoeff'.format(low))
        cmds.connectAttr('{}.outputX'.format(length_div), '{}.input1'.format(mult_coef))
        cmds.connectAttr('{}.output'.format(length_AddDouble), '{}.input2'.format(mult_coef))

        rev_node = cmds.createNode('reverse', n='{}_weightRev'.format(low))
        cmds.connectAttr('{}.output'.format(mult_coef), '{}.inputX'.format(rev_node))

        for node in nodes:
            cmds.connectAttr('{}.output'.format(mult_coef), '{}.weightA'.format(node))
            cmds.connectAttr('{}.outputX'.format(rev_node), '{}.weightB'.format(node))
            cmds.connectAttr('{}.Position'.format(Control), '{}.inputB'.format(node))


def curves_create(smooth=1, degree=3, src=None):
    if not src:
        src = cmds.ls(sl=True)[0]

    low_CVs = len(cmds.getAttr('{}.controlPoints[*]'.format(src)))

    if smooth == 1:
        high_CVs = (low_CVs * int(smooth))-1
    else:
        high_CVs = (low_CVs * int(smooth))

    coeff = 1/float(high_CVs-1)
    points = [(0, 0, 0) for x in range(high_CVs)]

    high_curve = cmds.curve(p=points, degree=degree)

    u_value = 0

    blend_nodes = []

    for cv in range(high_CVs):
        motion_path = cmds.createNode('motionPath', n='{}_cv{}_mPath'.format(src, cv))
        cmds.setAttr('{}.fractionMode'.format(motion_path), 1)
        cmds.connectAttr('{}.worldSpace'.format(src), '{}.geometryPath'.format(motion_path))
        cmds.connectAttr('{}.allCoordinates'.format(motion_path), '{}.controlPoints[{}]'.format(high_curve, cv))
        anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(src, cv))
        blend_nodes.append(anim_blend)
        cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
        cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(motion_path))
        u_value += coeff

    if blend_nodes:
        stretch_build(low=src, high=high_curve, nodes=blend_nodes)

