import maya.cmds as cmds
import pymel.core as pm
import MayaTools.tools.rig.rivet.rivet as rivet
reload(rivet)
import MayaTools.tools.rig.slide.slide_controller as slide
reload(slide)

curve = 'Slide_crv'
surface = 'Hydra_Main_Surface'
def start():
    slide_build = slide.MakeSlide(curve)
    items = slide_build.items
    for item in items:
        driver, driven = item.driver, item.driven
        rivet_build = rivet.RivetMatrix(obj=driven, surface=surface)
        cmds.connectAttr('.outputRotate'.format(rivet_build.dec_node), '{}.rotate'.format(driven))

        cpos = cmds.createNode('closestPointOnSurface')
        cmds.connectAttr('{}.allCoordinates'.format(driver), '{}.inPosition'.format(cpos))
        cmds.connectAttr('{}.worldSpace'.format(surface), '{}.inputSurface'.format(cpos))
        cmds.connectAttr('{}.parameterU'.format(cpos), '{}.parameterU'.format(rivet_build.pos_node))

        bind_jnt = cmds.createNode('joint')
        cmds.delete(cmds.parentConstraint(driven, bind_jnt, mo=False))
        cmds.parent(bind_jnt, driven)