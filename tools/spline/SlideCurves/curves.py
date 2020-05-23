import maya.cmds as cmds
import math

# def cv_to_loc(crv=None, obj=None):
#     """ Connect cvs to locator
#     :param crv: 'list' of cv's
#     :param obj: 'list' of controls to connect
#     :return:
#     """
#     if not crv:
#         crv = cmds.ls(sl=True, fl=True)
#
#     if crv:
#         if isinstance(crv, basestring):
#             crv = [crv]
#
#         controls = []
#         for c in crv:
#             points = cmds.getAttr('{}.controlPoints[*]'.format(c))
#             for cv in range(len(points)):
#                 if obj and isinstance(obj, list) and len(obj) == len(points):
#                     ctrl = obj[cv]
#                 else:
#                     ctrl = cmds.spaceLocator(n='{}_cv{}_loc'.format(c, cv))[0]
#                     cvPos = cmds.xform('{}.cv[{}]'.format(c, cv),
#                                        ws=True, t=True, q=True)
#                     cmds.xform(ctrl, t=cvPos)
#
#                 controls.append(ctrl)
#
#                 decompose = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(ctrl))
#                 cmds.connectAttr('{}.worldMatrix'.format(ctrl),
#                                  '{}.inputMatrix'.format(decompose))
#                 cmds.connectAttr('{}.outputTranslate'.format(decompose),
#                                  '{}.cv[{}]'.format(c, cv))
#
#         if controls:
#             return controls


# def delete_attr(obj=None, attr_list=None, force=True):
#     if attr_list and obj:
#         for attr in attr_list:
#             exist = cmds.attributeQuery(attr, node=obj, ex=True)
#             if exist:
#                 connect = cmds.listConnections('{}.{}'.format(obj, attr), c=True)
#                 if connect:
#                     if force:
#                         cmds.deleteAttr('{}.{}'.format(obj, attr))
#                 else:
#                     cmds.deleteAttr('{}.{}'.format(obj, attr))


# def curve_obj(obj=None):
#     if obj:
#         num_obj = len(obj)
#         if num_obj >= 4:
#             degree = 3
#         else:
#             degree = num_obj - 1
#
#         if degree:
#             points = [(0, 0, 0) for x in range(num_obj)]
#             curve = cmds.curve(p=points, degree=degree)
#             for point, cv in zip(obj, range(num_obj)):
#                 point_pos = cmds.xform(point, ws=True, t=True, q=True)
#                 cmds.setAttr('{}.controlPoints[{}]'.format(curve, cv), point_pos[0],
#                              point_pos[1],
#                              point_pos[2],
#                              type='double3')
#
#             if curve:
#                 return curve


def slide_build(low=None, nodes=None, control=None):
    if low and nodes:
        if not control:
            control = low

        attr_list = ['StretchMax', 'StretchMin', 'Length', 'Position']

        delete_attr(control, attr_list, force=True)

        cmds.addAttr(control, ln=attr_list[0], at='double', min=1, dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[1], at='double', min=0, max=1, dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[2], at='double', dv=1, k=True)
        cmds.addAttr(control, ln=attr_list[3], at='double', min=0, max=1, dv=0, k=True)

        low_info_node = cmds.createNode('curveInfo', n='{}_infoCurve'.format(low))
        cmds.connectAttr('{}.worldSpace'.format(low), '{}.inputCurve'.format(low_info_node))

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

        length_AddMinus = cmds.createNode('addDoubleLinear', n='{}_LengthAdd'.format(low))
        cmds.connectAttr('{}.Length'.format(control), '{}.input1'.format(length_AddMinus))
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
            cmds.connectAttr('{}.Position'.format(control), '{}.inputB'.format(node))




# def rebuild_curve(smooth=1, crv=None):
#     if not crv:
#         crv = cmds.ls(sl=True)[0]
#
#     low_CVs = len(cmds.getAttr('{}.controlPoints[*]'.format(crv)))
#     degree = cmds.getAttr('{}.degree'.format(crv))
#     high_CVs = (low_CVs * smooth)
#     high_CVs = math.ceil(high_CVs)
#     coeff = 1 / float(high_CVs - 1)
#     points = [(0, 0, 0) for x in range(int(high_CVs))]
#     print '{} points ==============================='.format(len(points))
#     create_curve = cmds.curve(p=points, degree=degree)
#     slide_curve = cmds.rename(create_curve, '{}_slideCurve'.format(crv))
#
#     u_value = 0
#     blend_nodes = []
#     mPath= []
#     for cv in range(int(high_CVs)):
#         motion_path = cmds.createNode('motionPath', n='{}_cv{}_mPath'.format(crv, cv))
#         mPath.append(motion_path)
#         cmds.setAttr('{}.fractionMode'.format(motion_path), 1)
#         cmds.connectAttr('{}.worldSpace'.format(crv), '{}.geometryPath'.format(motion_path))
#         cmds.connectAttr('{}.allCoordinates'.format(motion_path), '{}.controlPoints[{}]'.format(slide_curve, cv))
#         anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(crv, cv))
#         blend_nodes.append(anim_blend)
#         cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
#         cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(motion_path))
#         u_value += coeff
#
#     return_list = dict(
#         nodes=blend_nodes,
#         curve=slide_curve,
#         mPath=mPath
#     )
#
#     return return_list


# def fraction(curve=None, add=True):
#     if not curve:
#         curve = cmds.ls(sl=True)[0]
#
#     if curve:
#         mPath_nodes = [x for x in cmds.listConnections('{}.controlPoints[*]'.format(curve))
#                        if cmds.objectType(x, isType='motionPath')]
#         control = []
#         fraction_mult = []
#         for path in mPath_nodes:
#             fraction_bool = 0
#             fraction_coeff = 2
#             if not add:
#                 fraction_bool = 1
#                 fraction_coeff = 0.5
#             cmds.setAttr('{}.fractionMode'.format(path), fraction_bool)
#             spans = cmds.getAttr('{}.spans'.format(curve))
#             if spans > 5:
#                 blend_node = cmds.listConnections('{}.uValue'.format(path))[0]
#                 inputA = cmds.getAttr('{}.inputA'.format(blend_node))
#                 cmds.setAttr('{}.inputA'.format(blend_node), inputA*fraction_coeff)
#
#                 position_mult = '{}_fractionMult'.format(curve)
#
#                 if add:
#                     control = cmds.listConnections('{}.inputB'.format(blend_node))[0]
#                     if not cmds.objExists(position_mult):
#                         position_mult = cmds.createNode('multDoubleLinear', n=position_mult)
#                         cmds.connectAttr('{}.Position'.format(control), '{}.input1'.format(position_mult))
#
#                 if position_mult:
#                     fraction_mult.insert(0, position_mult)
#
#                 if add:
#                     cmds.setAttr('{}.input2'.format(position_mult), 2)
#                     cmds.connectAttr('{}.output'.format(position_mult), '{}.inputB'.format(blend_node), force=True)
#                 else:
#                     try:
#                         control_node = cmds.listConnections('{}.input1'.format(position_mult))[0]
#                         control.append(control_node)
#                     except:
#                         pass
#                     cmds.connectAttr('{}.Position'.format(control[0]), '{}.inputB'.format(blend_node), force=True)
#         if not add:
#             cmds.delete(fraction_mult)

#
# def connect_obj(type='joint', nodes=None, objects=None):
#     if nodes:
#         connectObj = []
#         for node, count in zip(nodes, range(len(nodes))):
#             if not objects:
#                 base_name = node.split('_mPath')[0]
#                 if not type:
#                     type = 'joint'
#                 obj = cmds.createNode(type, n='{}_Driver'.format(base_name))
#
#                 cmds.connectAttr('{}.allCoordinates'.format(node), '{}.translate'.format(obj))
#                 connectObj.append(obj)
#             else:
#                 cmds.connectAttr('{}.allCoordinates'.format(node), '{}.translate'.format(objects[count]))
#                 connectObj.append(objects[count])
#
#         if connectObj:
#             return connectObj



def slide_curve(curve=None, smooth=2, points=None, connect=False, fraction_mode=False, type_obj=''):
    if not points:
        points = cmds.ls(sl=True, fl=True)

    if points:
        if not curve:
            curve = curve_obj(points)

        if curve:
            if connect:
                controls = cv_to_loc(curve, obj=points)
            else:
                controls = cv_to_loc(curve)

            slide = rebuild_curve(smooth=smooth, crv=curve)

            if slide['nodes']:
                slide_build(low=curve, nodes=slide['nodes'], control=controls[0])

            if fraction_mode and slide['curve']:
                fraction(curve=slide['curve'], add=True)

            if type_obj:
                connect_obj(type=type_obj, nodes=slide['mPath'])
#
# def obj_parameter(curve=None, obj=None):
#     if curve and obj:
#         if isinstance(curve, basestring) and isinstance(obj, basestring):
#             node = cmds.createNode('nearestPointOnCurve', n='{}_nearPoint'.format(curve))
#             pos = cmds.xform(obj, ws=True, t=True, q=True)
#             cmds.connectAttr('{}.worldSpace'.format(curve), '{}.inputCurve'.format(node))
#             cmds.setAttr('{}.inPosition'.format(node), pos[0], pos[1], pos[2], type='double3')
#             parameter = cmds.getAttr('{}.parameter'.format(node))
#             cmds.delete(node)
#             return parameter


def apply_curve(low_curve=None, obj=None, connect=True, fraction_mode=False):
    if not low_curve:
        low_curve = cmds.ls(sl=True, fl=True)[-1]
    if not obj:
        obj = cmds.ls(sl=True, fl=True)[:-1]
    if low_curve and obj:
        apply_crv = curve_obj_slide(crv=low_curve, obj=obj)
        if connect:
            controls = cv_to_loc(crv=low_curve, obj=obj)
        else:
            controls = cv_to_loc(crv=low_curve)

        if apply_crv['nodes']:
            slide_build(low=low_curve, nodes=apply_crv['nodes'], control=controls[0])

        if fraction_mode and apply_crv['curve']:
            fraction(curve=apply_crv['curve'], add=True)


        connect_obj(objects=obj, nodes=apply_crv['mPath'])


# def curve_obj_slide(crv=None, obj=None):
#     if not obj:
#         obj = cmds.ls(sl=True, fl=True)
#     if crv:
#         max_length = cmds.getAttr('{}.maxValue'.format(crv))
#
#         CVs = len(obj)
#         degree = cmds.getAttr('{}.degree'.format(crv))
#         points = [(0, 0, 0) for x in range(CVs)]
#         create_curve = cmds.curve(p=points, degree=degree)
#         slide_curve = cmds.rename(create_curve, '{}_slideCurve'.format(crv))
#
#         blend_nodes = []
#         mPath = []
#         for obj, cv in zip(obj, range(CVs)):
#             motion_path = cmds.createNode('motionPath', n='{}_cv{}_mPath'.format(crv, cv))
#             mPath.append(motion_path)
#             cmds.setAttr('{}.fractionMode'.format(motion_path), 1)
#             cmds.connectAttr('{}.worldSpace'.format(crv), '{}.geometryPath'.format(motion_path))
#             cmds.connectAttr('{}.allCoordinates'.format(motion_path), '{}.controlPoints[{}]'.format(slide_curve, cv))
#             anim_blend = cmds.createNode('animBlendNodeAdditive', n='{}_cv{}_addOffset'.format(crv, cv))
#             blend_nodes.append(anim_blend)
#             parameter = obj_parameter(curve=crv, obj=obj)
#             u_value = float(parameter)/float(max_length)
#             cmds.setAttr('{}.inputA'.format(anim_blend), u_value)
#             cmds.connectAttr('{}.output'.format(anim_blend), '{}.uValue'.format(motion_path))
#
#         return_list = dict(
#             nodes=blend_nodes,
#             curve=slide_curve,
#             mPath=mPath
#         )
#
#         return return_list

def rivet_curve(curve=None, objects=None, offset=True):
    if not curve:
        curve = cmds.ls(sl=True, fl=True)[-1]
    if not objects:
        objects = cmds.ls(sl=True, fl=True)[:-1]

    print curve
    print objects
    if curve and objects:
        max_length = cmds.getAttr('{}.maxValue'.format(curve))
        for obj in objects:
            mPath = cmds.createNode('motionPath', n='{}_mPath_{}'.format(curve, obj))
            cmds.setAttr('{}.fractionMode'.format(mPath), 1)
            cmds.connectAttr('{}.worldSpace'.format(curve), '{}.geometryPath'.format(mPath))

            parameter = obj_parameter(curve=curve, obj=obj)
            u_value = float(parameter) / float(max_length)

            cmds.setAttr('{}.uValue'.format(mPath), u_value)
            compose = cmds.createNode('composeMatrix', n='{}_compMatrix'.format(mPath))
            cmds.connectAttr('{}.allCoordinates'.format(mPath), '{}.inputTranslate'.format(compose))

            if offset:
                decMatrix_offset = cmds.createNode('decomposeMatrix', n='{}_offsetMatrix'.format(mPath))
                cmds.connectAttr('{}.outputMatrix'.format(compose), '{}.inputMatrix'.format(decMatrix_offset))
                offset_obj = cmds.createNode('transform', n='{}_offset_grp'.format(mPath))
                cmds.connectAttr('{}.outputTranslate'.format(decMatrix_offset), '{}.translate'.format(offset_obj))
                mult_offset = cmds.createNode('multMatrix', n='{}_offsetMult'.format(mPath))
                cmds.connectAttr('{}.worldInverseMatrix'.format(offset_obj), '{}.matrixIn[1]'.format(mult_offset))
                cmds.connectAttr('{}.worldMatrix'.format(obj), '{}.matrixIn[2]'.format(mult_offset))
                offset_matrix = cmds.getAttr('{}.matrixSum'.format(mult_offset))

                mult_matrix = cmds.createNode('multMatrix', n='{}_multMatrix_{}'.format(curve, obj))
                cmds.setAttr('{}.matrixIn[1]'.format(mult_matrix), offset_matrix, type='matrix')
                cmds.connectAttr('{}.outputMatrix'.format(compose), '{}.matrixIn[2]'.format(mult_matrix))
                decMatrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix_{}'.format(curve, obj))
                cmds.connectAttr('{}.matrixSum'.format(mult_matrix), '{}.inputMatrix'.format(decMatrix))
                cmds.connectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(obj))

                cmds.delete(decMatrix_offset, mult_offset, offset_obj)

            else:
                mult_matrix = cmds.createNode('multMatrix', n='{}_multMatrix_{}'.format(curve, obj))
                cmds.connectAttr('{}.outputMatrix'.format(compose), '{}.matrixIn[1]'.format(mult_matrix))
                cmds.connectAttr('{}.parentInverseMatrix'.format(obj), '{}.matrixIn[2]'.format(mult_matrix))
                decMatrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix_{}'.format(curve, obj))
                cmds.connectAttr('{}.matrixSum'.format(mult_matrix), '{}.inputMatrix'.format(decMatrix))
                cmds.connectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(obj))
















