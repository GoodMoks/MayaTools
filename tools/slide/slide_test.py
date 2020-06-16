import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.curve as curve
import MayaTools.tools.rivet.new_rivet as rivet
import MayaTools.core.utils as utils

reload(utils)
reload(rivet)

reload(curve)


class SlideSurface(object):
    def __init__(self):
        self.surface = self.get_selected()
        self.fraction = True

        self.slide_controller = SlideController()

        self.build()

    def get_selected(self):
        selected = cmds.ls(sl=True)
        if not selected:
            om2.MGlobal.displayError('Nothing Selected')

        return selected[0]

    def create_iso_curve(self, value=1):
        print 'add_iso_node'
        self.curve_iso_node = cmds.createNode('curveFromSurfaceIso', n='{}_iso_curve_node'.format(self.surface))
        cmds.connectAttr('{}.worldSpace'.format(self.surface), '{}.inputSurface'.format(self.curve_iso_node))
        self.curve_iso = curve.Curve([1, 2], name='{}_iso_curve'.format(self.surface)).create_curve()
        cmds.connectAttr('{}.outputCurve'.format(self.curve_iso_node), '{}.create'.format(self.curve_iso))
        cmds.setAttr('{}.isoparmValue'.format(self.curve_iso_node), value)

    def create_slide_curve(self):
        self.slide = curve.SlideCurve(self.curve_iso)
        self.slide.create()

    def create_item(self):
        value = self.slide_controller.get_value_range(6, 1)
        for number, v in enumerate(value):
            item = SlideItem(curve=self.curve_iso, parameter=v, prefix=number)
            r = rivet.RivetMatrix(item.driven, self.surface, normalize=False)
            closest_point = cmds.createNode('closestPointOnSurface')
            cmds.connectAttr('{}.worldSpace'.format(self.surface), '{}.inputSurface'.format(closest_point))
            cmds.connectAttr('{}.allCoordinates'.format(item.driver), '{}.inPosition'.format(closest_point))
            cmds.connectAttr('{}.parameterU'.format(closest_point), '{}.parameterU'.format(r.pos_node))
            cmds.connectAttr('{}.outputRotate'.format(r.dec_node), '{}.r'.format(item.driven))
            self.slide.set_item(item)

    def build(self):
        print 'build'
        self.create_iso_curve()
        self.create_slide_curve()
        self.create_item()


class MakeSlide(object):
    def __init__(self, curve):
        self.curve = curve

        self.build()

    def create_slide_curve(self):
        self.slide = curve.SlideCurve(self.curve)
        self.slide.create()

    def create_item(self):
        value = utils.get_value_range(7, 1)
        for number, v in enumerate(value):
            item = curve.SlideItem(curve=self.curve, parameter=v, prefix=str(number))
            self.slide.set_item(item)

    def build(self):
        print 'build'

        self.create_slide_curve()
        self.create_item()
        #self.slide.set_global_scale_ctrl('curve1_CTRL', 'scaleX')



