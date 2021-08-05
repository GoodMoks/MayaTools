

import pymel.core as pm
import maya.cmds as cmds

import os




def build():
    sel = pm.selected()
    if not sel:
        return
    pm.undoInfo(openChunk=True)

    main_ctrl = pm.PyNode('Hydra_Options_CTRL')

    space = 0.5

    index = 1.0 / len(sel)
    print(index)
    value = 0


    for obj in sel:
        remap = pm.createNode('remapValue')
        value += index

        #dec = pm.createNode('decomposeMatrix')
        parent = obj.getParent()
        if not parent:
            continue

        # parent.worldInverseMatrix.connect(dec.inputMatrix)
        #
        # compose_matrix = pm.createNode('composeMatrix')
        # dec.outputScale.connect(compose_matrix.inputScale)
        # compose_matrix.outputMatrix.connect(obj.offsetParentMatrix)

        main_ctrl.Scale_Position.connect(remap.inputValue)

        main_ctrl.Scale.connect(remap.outputMax)
        remap.outputMin.set(1)

        remap.value[0].value_Position.set(value)
        remap.value[0].value_FloatValue.set(1)
        main_ctrl.Interpolation.connect(remap.value[0].value_Interp)

        start_space_node = pm.createNode('floatMath')
        start_space_node.floatA.set(value - 0.001)
        main_ctrl.Space.connect(start_space_node.floatB)
        start_space_node.outFloat.connect(remap.value[1].value_Position)
        main_ctrl.Interpolation.connect(remap.value[1].value_Interp)

        remap.value[1].value_FloatValue.set(0)


        end_space_node = pm.createNode('floatMath')
        end_space_node.operation.set(1)
        end_space_node.floatA.set(value + 0.001)
        main_ctrl.Space.connect(end_space_node.floatB)
        end_space_node.outFloat.connect(remap.value[2].value_Position)
        main_ctrl.Interpolation.connect(remap.value[2].value_Interp)

        remap.value[2].value_FloatValue.set(0)

        constraint = pm.PyNode('{}_scaleConstraint1'.format(obj))


        # scale Y
        obj_scale_norm_X = pm.createNode('floatMath')
        obj_scale_norm_X.floatB.set(1)
        obj_scale_norm_X.operation.set(1)
        remap.outValue.connect(obj_scale_norm_X.floatA)

        blend_scale_X = pm.createNode('animBlendNodeAdditiveScale')

        obj_scale_norm_X.outFloat.connect(blend_scale_X.inputA)
        constraint.constraintScaleX.connect(blend_scale_X.inputB)

        main_ctrl.ScaleX_Factor.connect(blend_scale_X.weightA)

        blend_scale_X.output.connect(obj.scaleX)

        # scale Y
        obj_scale_norm_Y = pm.createNode('floatMath')
        obj_scale_norm_Y.floatB.set(1)
        obj_scale_norm_Y.operation.set(1)
        remap.outValue.connect(obj_scale_norm_Y.floatA)

        blend_scale_Y = pm.createNode('animBlendNodeAdditiveScale')

        obj_scale_norm_X.outFloat.connect(blend_scale_Y.inputA)
        constraint.constraintScaleY.connect(blend_scale_Y.inputB)

        main_ctrl.ScaleY_Factor.connect(blend_scale_Y.weightA)

        blend_scale_Y.output.connect(obj.scaleY)

        factor_mult = pm.createNode('multiplyDivide')

        obj_scale_norm_X.outFloat.connect(factor_mult.input1X)
        main_ctrl.FactorX.connect(factor_mult.input2X)

        obj_scale_norm_Y.outFloat.connect(factor_mult.input1Y)
        main_ctrl.FactorY.connect(factor_mult.input2Y)

        factor_mult.outputX.connect(obj.translateX)
        factor_mult.outputY.connect(obj.translateY)

        # subtract_node = pm.createNode('floatMath')
        # subtract_node.operation.set(1)
        # subtract_node.floatB.set(1)
        #
        # remap.outValue.connect(subtract_node.floatA)
        #
        # add_node = pm.createNode('floatMath')
        # add_node.operation.set(0)

        # subtract_node.outFloat.connect(add_node.floatA)
        # dec.outputScaleY.connect(add_node.floatB)
        # add_node.outFloat.connect(obj.scaleY)
        # add_node.outFloat.connect(obj.scaleZ)



    pm.undoInfo(closeChunk=True)
