import maya.cmds as cmds
import attribute
import crv_new
import pymel.core as pm

def curve_iso(surface=None, curve=False, uniform=True, knot_mult=5):
    if surface and isinstance(surface, basestring):
        spans = cmds.getAttr('{}.spansU'.format(surface))
        iso_node = cmds.createNode('curveFromSurfaceIso', n='{}_iso'.format(surface))
        rebuild_node = cmds.createNode('rebuildCurve', n='{}_rebuild'.format(surface))
        cmds.connectAttr('{}.local'.format(surface), '{}.inputSurface'.format(iso_node))
        cmds.setAttr('{}.isoparmValue'.format(iso_node), 0.5)
        cmds.connectAttr('{}.outputCurve'.format(iso_node), '{}.inputCurve'.format(rebuild_node))
        cmds.setAttr('{}.spans'.format(rebuild_node), spans*knot_mult)
        cmds.setAttr('{}.isoparmDirection'.format(iso_node), 1)
        cmds.setAttr('{}.relativeValue'.format(iso_node), 1)

        if not uniform:
            cmds.setAttr('{}.rebuildType', 1)
        if curve:
            attrs = ['IsoparmValue', 'IsoparmDirection', 'RebuildType', 'Spans']

            curve_shape = cmds.createNode('nurbsCurve')
            curve_transform = cmds.listRelatives(curve_shape, type='transform', p=True)[0]
            curve = cmds.rename(curve_transform, '{}_iso_curve'.format(surface))
            cmds.setAttr('{}.dispCV'.format(curve), 1)
            cmds.connectAttr('{}.outputCurve'.format(rebuild_node), '{}.create'.format(curve))

            attribute.delete_attr(curve, attr=attrs)
            cmds.addAttr(curve, ln='IsoparmValue', dv=0.5, min=0, max=1, k=True)
            cmds.addAttr(curve, ln='IsoparmDirection', at='enum', en='U:V', dv=0, k=True)
            cmds.addAttr(curve, ln='RebuildType', at='enum', en='Uniform:Reduce', dv=0, k=True)
            cmds.addAttr(curve, ln='Spans', dv=spans*knot_mult, at='long', k=True)

            cmds.connectAttr('{}.IsoparmValue'.format(curve), '{}.isoparmValue'.format(iso_node))
            cmds.connectAttr('{}.IsoparmDirection'.format(curve), '{}.isoparmDirection'.format(iso_node))
            cmds.connectAttr('{}.RebuildType'.format(curve), '{}.rebuildType'.format(rebuild_node))
            cmds.connectAttr('{}.Spans'.format(curve), '{}.spans'.format(rebuild_node))


            return curve

        return rebuild_node

def loft_curve(crv=None, history=True, knot_mult=5):
    if crv and isinstance(crv, basestring):
        attrs = ['Distance', 'NormalX', 'NormalY', 'NormalZ', 'RebuildType', 'Spans']

        spans = cmds.getAttr('{}.spans'.format(crv))
        offset_node_first = cmds.createNode('offsetCurve', n='{}_offset_first'.format(crv))
        offset_rebuild_first = cmds.createNode('rebuildCurve', n='{}_rebuild_first'.format(crv))
        offset_node_second = cmds.createNode('offsetCurve', n='{}_offset_second'.format(crv))
        offset_rebuild_second = cmds.createNode('rebuildCurve', n='{}_rebuild_second'.format(crv))
        curve_shape = cmds.createNode('nurbsCurve')
        curve_transform = cmds.listRelatives(curve_shape, type='transform', p=True)[0]
        curve_first = cmds.rename(curve_transform, '{}_offset_crv_first'.format(crv))
        curve_second = cmds.duplicate(curve_first)[0]
        curve_second = cmds.rename(curve_second, '{}_offset_crv_second'.format(crv))


        for curve, offset, rebuild in zip([curve_first, curve_second],
                               [offset_node_first, offset_node_second],
                               [offset_rebuild_first, offset_rebuild_second]):

            cmds.connectAttr('{}.local'.format(crv), '{}.inputCurve'.format(offset))
            cmds.setAttr('{}.subdivisionDensity'.format(offset), 0)
            cmds.connectAttr('{}.outputCurve[0]'.format(offset), '{}.inputCurve'.format(rebuild))
            cmds.connectAttr('{}.outputCurve'.format(rebuild), '{}.create'.format(curve))
            cmds.setAttr('{}.dispCV'.format(curve), 1)



        loft = cmds.loft(curve_second, curve_first, ch=1, u=1, c=0, ar=1, d=1, ss=0, rn=0, po=0, rsn=True)


        cmds.addAttr(loft[0], ln='Distance', dv=1, k=True)
        cmds.addAttr(loft[0], ln='NormalX', dv=0, min=-1, max=1, k=True)
        cmds.addAttr(loft[0], ln='NormalY', dv=1, min=-1, max=1, k=True)
        cmds.addAttr(loft[0], ln='NormalZ', dv=0, min=-1, max=1, k=True)
        cmds.addAttr(loft[0], ln='RebuildType', at='enum', en='Uniform:Reduce', dv=1, k=True)
        cmds.addAttr(loft[0], ln='Spans', dv=spans * knot_mult, at='long', k=True)

        for node in [offset_rebuild_first, offset_rebuild_second]:

            cmds.connectAttr('{}.RebuildType'.format(loft[0]), '{}.rebuildType'.format(node))
            cmds.connectAttr('{}.Spans'.format(loft[0]), '{}.spans'.format(node))


        for node in [offset_node_first, offset_node_second]:

            cmds.connectAttr('{}.NormalX'.format(loft[0]), '{}.normalX'.format(node))
            cmds.connectAttr('{}.NormalY'.format(loft[0]), '{}.normalY'.format(node))
            cmds.connectAttr('{}.NormalZ'.format(loft[0]), '{}.normalZ'.format(node))

        cmds.connectAttr('{}.Distance'.format(loft[0]), '{}.distance'.format(offset_node_first))
        rev_dist = cmds.createNode('multDoubleLinear', n='{}_dist_rev'.format(curve_second))
        cmds.setAttr('{}.input2'.format(rev_dist), -1)
        cmds.connectAttr('{}.Distance'.format(loft[0]), '{}.input1'.format(rev_dist))
        cmds.connectAttr('{}.output'.format(rev_dist), '{}.distance'.format(offset_node_second))

        controls = crv_new.connect_cv(crv=crv)

        history_curve_grp = cmds.createNode('transform', n='{}_history_curves'.format(crv))
        cmds.parent(curve_first, curve_second, controls, history_curve_grp)

        cmds.setAttr('{}.visibility'.format(crv), 0)


        if not history:
            attribute.delete_attr(loft[0], attr=attrs, force=True)
            cmds.delete(curve_first, curve_second, offset_node_first, offset_node_second, loft[1])

        return loft

def build():
    sel = cmds.ls(sl=True)[0]
    if sel:
        loft = loft_curve(crv=sel, history=True)
        if loft:
            curve_iso(surface=loft[0], curve=True)