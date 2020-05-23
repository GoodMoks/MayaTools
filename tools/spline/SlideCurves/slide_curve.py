import maya.cmds as cmds
import crv_new
import attribute
import connect
import rivet


def build_test(crv=None, surface=None):
    if crv:
        nodes = node_on_curve(count=10, crv=crv)
        slide_build(crv=crv, nodes=nodes['blend'])
        for m_path in nodes['nodes']:
            obj = cmds.spaceLocator()[0]
            rivet.apply_rivet(surface=surface, obj=[obj], translate=False)
            closest_param(m_path=m_path, surface=surface, obj=obj)
            cmds.connectAttr('{}.allCoordinates'.format(m_path), '{}.translate'.format(obj))


def rebuild_curve(crv=None, knot_mult=2):
    if crv and isinstance(crv, basestring):
        spans = cmds.getAttr('{}.spans'.format(crv))
        cmds.addAttr(crv, ln='RebuildType', at='enum', en='Uniform:Reduce', dv=0, k=True)
        cmds.addAttr(crv, ln='Spans', dv=spans * knot_mult, at='long', k=True)

        rebuild_node = cmds.createNode('rebuildCurve', n='{}_rebuild'.format(crv))

        cmds.connectAttr('{}.RebuildType'.format(crv), '{}.rebuildType'.format(rebuild_node))
        cmds.connectAttr('{}.Spans'.format(crv), '{}.spans'.format(rebuild_node))



def closest_param(m_path=None, surface=None, obj=None):
    """ Add closest node to slide system

    :param m_path: 'str' motionPath node
    :param surface: 'str' nurbs surface
    :param obj: 'str' object to connect
    :return:
    """
    if m_path and surface and obj:
        closest_node = cmds.createNode('closestPointOnSurface', n='{}_cpos'.format(obj))
        cmds.connectAttr('{}.allCoordinates'.format(m_path), '{}.inPosition'.format(closest_node))
        cmds.connectAttr('{}.local'.format(surface), '{}.inputSurface'.format(closest_node))
        cmds.connectAttr('{}.result.parameterU'.format(closest_node), '{}.Parameter_U'.format(obj))
        cmds.connectAttr('{}.result.parameterV'.format(closest_node), '{}.Parameter_V'.format(obj))

        return closest_node


def node_on_curve(count=None, crv=None, fraction=1):
    """ Create follow motionPath node on curve or surface

    :param count: 'int' number of node on curve
    :param crv: 'str' curve name
    :param fraction: 'bool' parametric path or not
    :return: 'dict' nodes{'blend': blend nodes, 'curve': curve, 'nodes': nodes}
    """
    if count and crv:
        # process var
        coeff = 1 / float(count - 1)
        u_value = 0

        # return var
        blend_nodes = []
        nodes = []
        for cv in range(int(count)):
            node = cmds.createNode('motionPath', n='{}_mPath_{}'.format(crv, cv))
            nodes.append(node)
            cmds.setAttr('{}.fractionMode'.format(node), fraction)
            cmds.connectAttr('{}.worldSpace'.format(crv), '{}.geometryPath'.format(node))
            anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(crv, cv))
            blend_nodes.append(anim_blend)
            cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
            cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(node))
            u_value += coeff

        return_dict = dict(
            blend=blend_nodes,
            surface=crv,
            nodes=nodes
        )
        return return_dict


def slide_build(crv=None, nodes=None, control=None):
    """ Builds slide node system

    :param crv: 'str' name of curve or nurbs surface
    :param nodes: 'list' blend nodes
    :param control: 'str' object for add attribute
    """
    if crv and nodes:
        if not control:
            control = crv

        # add attributes
        attr_list = ['StretchMax', 'StretchMin', 'Length', 'Position']
        attribute.delete_attr(control, attr=attr_list, force=True)
        cmds.addAttr(control, ln=attr_list[0], at='double', min=1, dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[1], at='double', min=0, max=1, dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[2], at='double', dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[3], at='double', min=0, max=1, dv=0, k=True)

        # create curveInfo node
        info_node = cmds.createNode('curveInfo', n='{}_infoCurve'.format(crv))
        cmds.connectAttr('{}.worldSpace'.format(crv), '{}.inputCurve'.format(info_node))

        length_div = cmds.createNode('multiplyDivide', n='{}_lengthDiv'.format(crv))
        length = cmds.getAttr('{}.arcLength'.format(info_node))
        cmds.setAttr('{}.operation'.format(length_div), 2)
        cmds.setAttr('{}.input1X'.format(length_div), length)
        cmds.setAttr('{}.input2Y'.format(length_div), length)
        cmds.connectAttr('{}.arcLength'.format(info_node), '{}.input1Y'.format(length_div))
        cmds.connectAttr('{}.arcLength'.format(info_node), '{}.input2X'.format(length_div))
        min_cond = cmds.createNode('condition', n='{}_minCond'.format(crv))
        max_cond = cmds.createNode('condition', n='{}_maxCond'.format(crv))
        main_cond = cmds.createNode('condition', n='{}_mainCond'.format(crv))

        # min node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.secondTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(control), '{}.firstTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(control), '{}.colorIfTrueR'.format(min_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(min_cond))
        cmds.setAttr('{}.operation'.format(min_cond), 3)

        # max node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(control), '{}.secondTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(control), '{}.colorIfTrueR'.format(max_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(max_cond))
        cmds.setAttr('{}.operation'.format(max_cond), 3)

        # main node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(min_cond), '{}.colorIfFalseR'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(max_cond), '{}.colorIfTrueR'.format(main_cond))
        cmds.setAttr('{}.secondTerm'.format(main_cond), 1)
        cmds.setAttr('{}.operation'.format(main_cond), 2)

        length_AddMinus = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(crv))
        cmds.connectAttr('{}.Length'.format(control), '{}.input1'.format(length_AddMinus))
        cmds.setAttr('{}.input2 '.format(length_AddMinus), -1)

        length_AddDouble = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(crv))
        cmds.connectAttr('{}.outColorR'.format(main_cond), '{}.input1'.format(length_AddDouble))
        cmds.connectAttr('{}.output'.format(length_AddMinus), '{}.input2'.format(length_AddDouble))

        mult_coef = cmds.createNode('multDoubleLinear', n='{}_multCoeff'.format(crv))
        cmds.connectAttr('{}.outputX'.format(length_div), '{}.input1'.format(mult_coef))
        cmds.connectAttr('{}.output'.format(length_AddDouble), '{}.input2'.format(mult_coef))

        rev_node = cmds.createNode('reverse', n='{}_weightRev'.format(crv))
        cmds.connectAttr('{}.output'.format(mult_coef), '{}.inputX'.format(rev_node))

        for node in nodes:
            cmds.connectAttr('{}.output'.format(mult_coef), '{}.weightA'.format(node))
            cmds.connectAttr('{}.outputX'.format(rev_node), '{}.weightB'.format(node))
            cmds.connectAttr('{}.Position'.format(control), '{}.inputB'.format(node))
