import maya.cmds as cmds
import pymel.core as pm
import MayaTools.tools.rig.rivet.rivet as rivet

reload(rivet)

surf = 'Hydra_Skin_Rebuild_Surface'


def build():
    s = pm.selected()
    if not s:
        return

    nodes = []
    pm.undoInfo(openChunk=True)
    for obj in s:
        print(obj)

        r = rivet.RivetMatrix(str(obj), surf, True)
        dec_node = r.dec_node
        output_node = pm.createNode('transform', n='{}_rivetOut'.format(obj))
        pm.connectAttr('{}.outputTranslate'.format(dec_node), '{}.translate'.format(output_node))
        pm.connectAttr('{}.outputRotate'.format(dec_node), '{}.rotate'.format(output_node))
        pm.parentConstraint(output_node, obj, mo=True)
        nodes.append(output_node)

    pm.group(nodes)
    pm.undoInfo(closeChunk=True)

def build_single():
    s = pm.selected()
    if not s:
        return

    surf = s[1]
    obj = s[0]
    nodes = []
    pm.undoInfo(openChunk=True)

    r = rivet.RivetMatrix(str(obj), str(surf), True)
    dec_node = r.dec_node
    output_node = pm.createNode('transform', n='{}_rivetOut'.format(obj))
    pm.connectAttr('{}.outputTranslate'.format(dec_node), '{}.translate'.format(output_node))
    pm.connectAttr('{}.outputRotate'.format(dec_node), '{}.rotate'.format(output_node))
    pm.parentConstraint(output_node, obj, mo=True)

    pm.undoInfo(closeChunk=True)

def fix_axis():
    s = pm.selected()
    if not s:
        return


    for obj in s:
        buffer = pm.PyNode('{}_Buffer_Rivet_Loc'.format(obj.split('_CTRL')[0]))

        rot_comp = pm.createNode('composeMatrix')
        trans_comp = pm.createNode('composeMatrix')
        mult = pm.createNode('multMatrix')
        dec = pm.createNode('decomposeMatrix')
        blend = pm.createNode('animBlendNodeAdditiveRotation')

        buffer.rotate.connect(rot_comp.inputRotate)
        obj.translate.connect(trans_comp.inputTranslate)
        trans_comp.outputMatrix.connect(mult.matrixIn[0])
        rot_comp.outputMatrix.connect(mult.matrixIn[1])
        mult.matrixSum.connect(dec.inputMatrix)

        buffer.rotate.connect(blend.inputA)
        obj.rotate.connect(blend.inputB)
        blend.accumulationMode.set(1)

        


def mult_rot():
    sel = pm.selected()
    if not sel and not len(sel) == 3:
        return

    pm.undoInfo(closeChunk=True)


    control, wrapper, joint = sel
    compose_trans = pm.createNode('composeMatrix')
    compose_rotate = pm.createNode('composeMatrix')
    mult = pm.createNode('multMatrix')
    dec = pm.createNode('decomposeMatrix')
    anim_blend = pm.createNode('animBlendNodeAdditiveRotation')

    control.translate.connect(compose_trans.inputTranslate)
    wrapper.rotate.connect(compose_rotate.inputRotate)
    compose_trans.outputMatrix.connect(mult.matrixIn[0])
    compose_rotate.outputMatrix.connect(mult.matrixIn[1])
    mult.matrixSum.connect(dec.inputMatrix)
    dec.outputTranslate.connect(joint.translate, f=True)
    wrapper.rotate.connect(anim_blend.inputA)
    control.rotate.connect(anim_blend.inputB)
    anim_blend.output.connect(joint.rotate, f=True)
    anim_blend.accumulationMode.set(1)


    pm.undoInfo(openChunk=True)


