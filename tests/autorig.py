import maya.cmds as cmds
import maya.OpenMaya as om


def base_group_structure(rig_name):
    # create base group structure of rig with  given name

    if not rig_name:
        rig_name = 'Setup'

    if rig_name:
        rig_grp = cmds.group(w=True, em=True, n='{}_RIG'.format(rig_name))
        no_transform_grp = cmds.group(em=True, n='DO_NOT_TOUCH', p=rig_grp)
        transform_grp = cmds.group(em=True, n='TRANSTORM', p=rig_grp)
        geometry_grp = cmds.group(em=True, n='{}_GEO_GRP'.format(rig_name), p='DO_NOT_TOUCH')
        extra_node_grp = cmds.group(em=True, n='{}_Extra_Node_GRP'.format(rig_name), p='DO_NOT_TOUCH')
        jnt_grp = cmds.group(em=True, n='JOINT_GRP', p='TRANSTORM')
        system_grp = cmds.group(em=True, n='SYSTEM_GRP', p='TRANSTORM')
        ctrl_grp = cmds.group(em=True, n='CONTROL_GRP', p='TRANSTORM')
        ik_grp = cmds.group(em=True, n='IK_GRP', p='TRANSTORM')


def set_rotation_order(obj, order):
    # set rotation order of selected object to given value

    if order == 'xyz':
        ord = 0
    if order == 'yzx':
        ord = 1
    if order == 'zxy':
        ord = 2
    if order == 'xzy':
        ord = 3
    if order == 'yxz':
        ord = 4
    if order == 'zyx':
        ord = 5
    for o in obj:
        cmds.setAttr('{}.rotateOrder'.format(o), ord)


def three_joint_chain_stretch(ik_ctrl, wrapper_ctrl, main_ctrl, shoulder_ik_jnt, elbow_ik_jnt, stretch_axis):
    # create stretch of three joint chain ik system

    db = cmds.createNode('distanceBetween', n='{}_DB'.format(ik_ctrl))
    md = cmds.createNode('multiplyDivide', n='{}_MD'.format(ik_ctrl))
    cmds.setAttr('{}.operation'.format(md), 2)
    mdl = cmds.createNode('multDoubleLinear', n='{}_MDL'.format(ik_ctrl))
    con = cmds.createNode('condition', n='{}_CON'.format(ik_ctrl))
    cmds.setAttr('{}.operation'.format(con), 2)
    cmds.setAttr('{}.colorIfFalseR'.format(con), 1)
    bc = cmds.createNode('blendColors', n='{}_BC'.format(ik_ctrl))
    cmds.setAttr('{}.color2R'.format(bc), 1)
    cmds.connectAttr('{}.worldMatrix'.format(ik_ctrl), '{}.inMatrix1'.format(db))
    cmds.connectAttr('{}.worldMatrix'.format(wrapper_ctrl), '{}.inMatrix2'.format(db))
    cmds.connectAttr('{}.rotatePivot'.format(ik_ctrl), '{}.point1'.format(db))
    cmds.connectAttr('{}.rotatePivot'.format(wrapper_ctrl), '{}.point2'.format(db))
    distance = cmds.getAttr('{}.distance'.format(db))

    if not cmds.objExists('{}.Global_Scale'.format(main_ctrl)):
        cmds.addAttr(main_ctrl, shortName='GS', longName='Global_Scale', attributeType='float', defaultValue=1.0,
                     h=False, k=True)
        om.MGlobal_displayError(
            'You do not have "Global_Scale" attrebute connected to your rig !'
            'It may generate problem with stretch, when rig will be scaled')
        return

    cmds.connectAttr('{}.Global_Scale'.format(main_ctrl), '{}.input1'.format(mdl))
    cmds.setAttr('{}.input2'.format(mdl), distance)
    cmds.connectAttr('{}.output'.format(mdl), '{}.input2.input2X'.format(md))
    cmds.connectAttr('{}.distance'.format(db), '{}.input1.input1X'.format(md))
    cmds.connectAttr('{}.distance'.format(db), '{}.firstTerm'.format(con))
    cmds.connectAttr('{}.output'.format(mdl), '{}.secondTerm'.format(con))
    cmds.connectAttr('{}.output.outputX'.format(md), '{}.colorIfTrue.colorIfTrueR'.format(con))
    cmds.connectAttr('{}.outColor.outColorR'.format(con), '{}.color1.color1R'.format(bc))

    if not cmds.objExists('{}.Stretch'.format(ik_ctrl)):
        cmds.addAttr(ik_ctrl, shortName='St', longName='Stretch', attributeType='float', defaultValue=1.0, minValue=0.0,
                     maxValue=1.0,
                     h=False, k=True)

    cmds.connectAttr('{}.Stretch'.format(ik_ctrl), '{}.blender'.format(bc))

    if stretch_axis == 'x':
        sa = 'scaleX'
    if stretch_axis == 'y':
        sa = 'scaleY'
    if stretch_axis == 'z':
        sa = 'scaleZ'

    cmds.connectAttr('{}.output.outputR'.format(bc), '{}.scale.{}'.format(shoulder_ik_jnt, sa))
    cmds.connectAttr('{}.output.outputR'.format(bc), '{}.scale.{}'.format(elbow_ik_jnt, sa))


def zero_out_grp(obj):
    position_grp = cmds.createNode('transform', n=obj + '_POS')
    constraint_grp = cmds.createNode('transform', n=obj + '_CON')
    # Query all transform
    translate = cmds.xform(obj, q=True, t=True, ws=True)
    rotate = cmds.xform(obj, q=True, ro=True, ws=True)
    scale = cmds.xform(obj, q=True, s=True, ws=True)
    # Parent null groups
    parent_grp = cmds.parent(constraint_grp, position_grp)[0]
    xform_grp = obj + '_POS'
    # Set transform on main position group
    cmds.xform(xform_grp, t=translate, ws=True)
    cmds.xform(xform_grp, ro=rotate, ws=True)
    cmds.xform(xform_grp, s=scale, ws=True)
    # Parent object to group
    cmds.parent(obj, parent_grp)


def duplicate_jnt(root_jnt, chain_number):
    new_jnt_chain = cmds.duplicate(root_jnt, rc=True)
    children = cmds.listRelatives(new_jnt_chain[chain_number - 1], c=True)

    for c in children:
        cmds.delete(c)

    return new_jnt_chain[0]


def rename_jnt(root_jnt, type='FK'):
    name = root_jnt.replace('JNT', '{}_JNT'.format(type))[:-1]
    cmds.rename(root_jnt, name)

    children_name = cmds.listRelatives(name, pa=True, ad=True, typ='joint')
    for c in children_name:
        c = c.split('|')[-1]
        new_children_name = c.replace('JNT', '{}_JNT'.format(type))[:-1]
        new_c_name = cmds.rename(c, new_children_name)

    return name


def clear_duplicated(obj, category):
    children = cmds.listRelatives(obj, ad=True)

    for c in children:
        if not cmds.objectType(c) == category:
            cmds.delete(c)


def jnt_size(jnt, r, mode):
    if mode == 'scale':
        root_r = cmds.getAttr('{}.radius'.format(jnt))
        r *= root_r
    cmds.setAttr('{}.radius'.format(jnt), r)
