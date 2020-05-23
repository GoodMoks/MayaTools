import maya.cmds as cmds


class SlideCurve(object):
    def __init__(self, curve, fraction=True):
        self.curve = curve
        self.fraction = fraction



        self.slide_system()


        #self.node_on_curve()
        #self.slide_curve()


    def slide_system(self):
        info_node = cmds.createNode('curveInfo', n='{}_infoCurve'.format(self.curve))
        cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.inputCurve'.format(info_node))
        length = cmds.getAttr('{}.arcLength'.format(info_node))

        scale_mult = cmds.createNode('multiplyDivide', n='{}_lengthScale'.format(self.curve))
        cmds.setAttr('{}.input1Y'.format(scale_mult), length)
        cmds.connectAttr('{}.arcLength'.format(info_node), '{}.input1X'.format(scale_mult))

        length_div = cmds.createNode('multiplyDivide', n='{}_lengthDiv'.format(self.curve))
        cmds.setAttr('{}.operation'.format(length_div), 2)

        cmds.connectAttr('{}.outputX'.format(scale_mult), '{}.input1Y'.format(length_div))
        cmds.connectAttr('{}.outputX'.format(scale_mult), '{}.input2X'.format(length_div))
        cmds.connectAttr('{}.outputY'.format(scale_mult), '{}.input1X'.format(length_div))
        cmds.connectAttr('{}.outputY'.format(scale_mult), '{}.input2Y'.format(length_div))

        min_cond = cmds.createNode('condition', n='{}_minCond'.format(self.curve))
        max_cond = cmds.createNode('condition', n='{}_maxCond'.format(self.curve))
        main_cond = cmds.createNode('condition', n='{}_mainCond'.format(self.curve))

        # min node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.secondTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.curve), '{}.firstTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.curve), '{}.colorIfTrueR'.format(min_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(min_cond))
        cmds.setAttr('{}.operation'.format(min_cond), 3)

        # max node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.curve), '{}.secondTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.curve), '{}.colorIfTrueR'.format(max_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(max_cond))
        cmds.setAttr('{}.operation'.format(max_cond), 3)

        # main node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(min_cond), '{}.colorIfFalseR'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(max_cond), '{}.colorIfTrueR'.format(main_cond))
        cmds.setAttr('{}.secondTerm'.format(main_cond), 1)
        cmds.setAttr('{}.operation'.format(main_cond), 2)

        length_negative = cmds.createNode('addDoubleLinear', n='{}_LengthNegative'.format(self.curve))
        cmds.connectAttr('{}.Length'.format(self.curve), '{}.input1'.format(length_negative))
        cmds.setAttr('{}.input2 '.format(length_negative), -1)

        length_sum = cmds.createNode('addDoubleLinear', n='{}_LengthSum'.format(self.curve))
        cmds.connectAttr('{}.outColorR'.format(main_cond), '{}.input1'.format(length_sum))
        cmds.connectAttr('{}.output'.format(length_negative), '{}.input2'.format(length_sum))

        mult_coef = cmds.createNode('multDoubleLinear', n='{}_multCoeff'.format(self.curve))
        cmds.connectAttr('{}.outputX'.format(length_div), '{}.input1'.format(mult_coef))
        cmds.connectAttr('{}.output'.format(length_sum), '{}.input2'.format(mult_coef))

        rev_node = cmds.createNode('reverse', n='{}_weightRev'.format(self.curve))
        cmds.connectAttr('{}.output'.format(mult_coef), '{}.inputX'.format(rev_node))


    def node_on_curve(self, count=3):
        coeff = 1 / float(count - 1)
        u_value = 0

        self.blend_nodes = []
        self.mPath = []
        for cv in range(int(count)):
            node = cmds.createNode('motionPath', n='{}_mPath_{}'.format(self.curve, cv))
            self.mPath.append(node)
            cmds.setAttr('{}.fractionMode'.format(node), self.fraction)
            cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.geometryPath'.format(node))
            anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(self.curve, cv))
            self.blend_nodes.append(anim_blend)
            cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
            cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(node))
            u_value += coeff


            loc = cmds.spaceLocator()[0]
            cmds.connectAttr('{}.allCoordinates'.format(node), '{}.translate'.format(loc))
    def slide_curve(self):
        # add attributes
        attr_list = ['StretchMax', 'StretchMin', 'Length', 'Position']
        try:
            cmds.addAttr(self.curve, ln=attr_list[0], at='double', min=1, dv=1, k=True)
            cmds.addAttr(self.curve, ln=attr_list[1], at='double', min=0, max=1, dv=1, k=True)
            cmds.addAttr(self.curve, ln=attr_list[2], at='double', dv=1, k=True)
            cmds.addAttr(self.curve, ln=attr_list[3], at='double', min=0, max=1, dv=0, k=True)
        except:
            pass

        # create curveInfo node
        info_node = cmds.createNode('curveInfo', n='{}_infoCurve'.format(self.curve))
        cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.inputCurve'.format(info_node))

        length_div = cmds.createNode('multiplyDivide', n='{}_lengthDiv'.format(self.curve))
        length = cmds.getAttr('{}.arcLength'.format(info_node))
        cmds.setAttr('{}.operation'.format(length_div), 2)
        cmds.setAttr('{}.input1X'.format(length_div), length)
        cmds.setAttr('{}.input2Y'.format(length_div), length)
        cmds.connectAttr('{}.arcLength'.format(info_node), '{}.input1Y'.format(length_div))
        cmds.connectAttr('{}.arcLength'.format(info_node), '{}.input2X'.format(length_div))
        min_cond = cmds.createNode('condition', n='{}_minCond'.format(self.curve))
        max_cond = cmds.createNode('condition', n='{}_maxCond'.format(self.curve))
        main_cond = cmds.createNode('condition', n='{}_mainCond'.format(self.curve))

        # min node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.secondTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.curve), '{}.firstTerm'.format(min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.curve), '{}.colorIfTrueR'.format(min_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(min_cond))
        cmds.setAttr('{}.operation'.format(min_cond), 3)

        # max node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.curve), '{}.secondTerm'.format(max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.curve), '{}.colorIfTrueR'.format(max_cond))
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.colorIfFalseR'.format(max_cond))
        cmds.setAttr('{}.operation'.format(max_cond), 3)

        # main node build
        cmds.connectAttr('{}.outputY'.format(length_div), '{}.firstTerm'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(min_cond), '{}.colorIfFalseR'.format(main_cond))
        cmds.connectAttr('{}.outColorR'.format(max_cond), '{}.colorIfTrueR'.format(main_cond))
        cmds.setAttr('{}.secondTerm'.format(main_cond), 1)
        cmds.setAttr('{}.operation'.format(main_cond), 2)

        length_AddMinus = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(self.curve))
        cmds.connectAttr('{}.Length'.format(self.curve), '{}.input1'.format(length_AddMinus))
        cmds.setAttr('{}.input2 '.format(length_AddMinus), -1)

        length_AddDouble = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(self.curve))
        cmds.connectAttr('{}.outColorR'.format(main_cond), '{}.input1'.format(length_AddDouble))
        cmds.connectAttr('{}.output'.format(length_AddMinus), '{}.input2'.format(length_AddDouble))

        mult_coef = cmds.createNode('multDoubleLinear', n='{}_multCoeff'.format(self.curve))
        cmds.connectAttr('{}.outputX'.format(length_div), '{}.input1'.format(mult_coef))
        cmds.connectAttr('{}.output'.format(length_AddDouble), '{}.input2'.format(mult_coef))

        rev_node = cmds.createNode('reverse', n='{}_weightRev'.format(self.curve))
        cmds.connectAttr('{}.output'.format(mult_coef), '{}.inputX'.format(rev_node))

        for node in self.blend_nodes:
            cmds.connectAttr('{}.output'.format(mult_coef), '{}.weightA'.format(node))
            cmds.connectAttr('{}.outputX'.format(rev_node), '{}.weightB'.format(node))
            cmds.connectAttr('{}.Position'.format(self.curve), '{}.inputB'.format(node))


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
