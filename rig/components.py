import maya.cmds as cmds
import utilities as utility


def twist_ext(control=None, axis='Y', destination=None):
    if not control or destination:
        select = cmds.ls(sl=True, fl=True)
        if select:
            control = select[0]
            if len(select)==2:
                destination = select[1]

    if control and axis:
        rotate_order = cmds.getAttr('{}.rotateOrder'.format(control))

        control_grp = cmds.createNode('transform', n=utility.renamePrefix(control, prefix='Driver'))
        control_grp_pos = utility.nullGrp(obj=[control_grp], prefix='Pos')[0]

        utility.align(source=[control_grp_pos], target=control)

        cmds.setAttr('{}.rotateOrder'.format(control_grp), rotate_order)
        cmds.setAttr('{}.rotateOrder'.format(control_grp_pos), rotate_order)



        cmds.parentConstraint(control, control_grp, mo=True)

        #joints
        base_jnt = cmds.createNode('joint', n='{}_baseExtJnt'.format(control))
        tip_jnt = cmds.createNode('joint', n='{}_tipExtJnt'.format(control))
        cmds.parent(tip_jnt, base_jnt)

        utility.align([base_jnt], control)
        cmds.makeIdentity(base_jnt, apply=True, t=1, r=1, s=1, n=0)
        cmds.setAttr('{}.rotateOrder'.format(base_jnt), rotate_order)
        cmds.setAttr('{}.translate{}'.format(tip_jnt, axis), 1)
        cmds.pointConstraint(control, base_jnt)


        #ik handle
        ik = cmds.ikHandle(n='{}_twist_IK'.format(control), sj=base_jnt, ee=tip_jnt, sol='ikRPsolver')[0]
        cmds.setAttr('{}.poleVector'.format(ik), 0, 0, 0, type='double3')
        cmds.parentConstraint(control_grp, ik, mo=True)


        twist_grp = cmds.createNode('transform', n='{}_twist{}'.format(control, axis))
        twist_grp_pos = utility.nullGrp([twist_grp], prefix='Pos')[0]
        cmds.setAttr('{}.rotateOrder'.format(twist_grp), rotate_order)
        cmds.setAttr('{}.rotateOrder'.format(twist_grp_pos), rotate_order)

        utility.align([twist_grp_pos], control)
        cmds.setAttr('{}.rotateOrder'.format(twist_grp_pos), rotate_order)

        cmds.orientConstraint(base_jnt, control_grp, twist_grp)

        mult_node = cmds.createNode('multDoubleLinear', n='{}_multExtRot'.format(control))
        cmds.setAttr('{}.input2'.format(mult_node), -2)
        cmds.connectAttr('{}.rotate{}'.format(twist_grp, axis), '{}.input1'.format(mult_node))


        mult_matrix = cmds.createNode('multMatrix', n='{}_multMatrix'.format(control))
        decompose_matrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(control))
        cmds.setAttr('{}.inputRotateOrder'.format(decompose_matrix), rotate_order)
        cmds.connectAttr('{}.worldMatrix'.format(control), '{}.matrixIn[0]'.format(mult_matrix))
        cmds.connectAttr('{}.parentInverseMatrix'.format(base_jnt), '{}.matrixIn[1]'.format(mult_matrix))
        cmds.connectAttr('{}.matrixSum'.format(mult_matrix), '{}.inputMatrix'.format(decompose_matrix))

        cmds.connectAttr('{}.outputTranslate'.format(decompose_matrix), '{}.translate'.format(twist_grp_pos))
        cmds.connectAttr('{}.outputRotate'.format(decompose_matrix), '{}.rotate'.format(twist_grp_pos))

        cmds.setAttr('{}.inheritsTransform'.format(base_jnt), 0)
        cmds.setAttr('{}.inheritsTransform'.format(twist_grp_pos), 0)
        cmds.setAttr('{}.inheritsTransform'.format(ik), 0)

        #main group
        main_grp = cmds.createNode('transform', n='{}_twistExtractor'.format(control))
        cmds.setAttr('{}.visibility'.format(main_grp), 0)
        cmds.parent(base_jnt, twist_grp_pos, control_grp_pos, ik, main_grp)

        if destination:
            cmds.connectAttr('{}.output'.format(mult_node), '{}.rotate{}'.format(destination, axis))

        cmds.select(twist_grp)
