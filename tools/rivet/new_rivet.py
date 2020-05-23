import maya.cmds as cmds
import MayaTools.core.utils as utils
import MayaTools.core.mesh as mesh
import MayaTools.core.surface as surface_utils
import MayaTools.core.curve as curve

reload(curve)
reload(mesh)


class RivetFollicle(object):
    def __init__(self, obj, surface):
        self.obj = obj
        self.surface = surface

        self.name = None
        self.follicle = None
        self.shape = None
        self.param = None

        self.rivet()

    def rivet(self):
        self.name = '{}_{}_flcs'.format(self.surface, self.obj)
        self.follicle, self.shape = utils.create_follicle(self.name)
        try:
            cmds.connectAttr('{}.outMesh'.format(self.surface), '{}.inputMesh'.format(self.shape))
        except:
            cmds.connectAttr('{}.local'.format(self.surface), '{}.inputSurface'.format(self.shape))

        cmds.connectAttr('{}.worldMatrix'.format(self.surface), '{}.inputWorldMatrix'.format(self.shape))
        self.param = mesh.get_closest_UV_mesh(self.surface, cmds.xform(self.obj, q=True, ws=True, rp=True))
        cmds.setAttr('{}.parameterU'.format(self.shape), self.param[0])
        cmds.setAttr('{}.parameterV'.format(self.shape), self.param[1])


class RivetMatrix(object):
    def __init__(self, obj, surface, normalize=True):
        self.obj = obj
        self.surface = surface
        self.normalize = normalize

        self.pos_nod = None
        self.four_node = None
        self.dec_node = None
        self.param = None

        self.rivet()

    def rivet(self):
        self.pos_node = cmds.createNode('pointOnSurfaceInfo', n='{}_pos_node'.format(self.obj))
        self.four_node = cmds.createNode('fourByFourMatrix', n='{}_four_node'.format(self.obj))
        self.dec_node = cmds.createNode('decomposeMatrix', n='{}_dec_node'.format(self.obj))

        cmds.connectAttr('{}.worldSpace'.format(self.surface), '{}.inputSurface'.format(self.pos_node))
        self.param = surface_utils.get_closest_UV_surface(self.surface, cmds.xform(self.obj, q=True, ws=True, rp=True))
        cmds.setAttr('{}.parameterU'.format(self.pos_node), self.param[0])
        cmds.setAttr('{}.parameterV'.format(self.pos_node), self.param[1])

        cmds.setAttr('{}.turnOnPercentage'.format(self.pos_node), self.normalize)

        four_attr = ['normalizedNormal', 'normalizedTangentU', 'normalizedTangentV', 'position']
        for item_attr, attr in enumerate(four_attr):
            coord_list = ['X', 'Y', 'Z']
            for item_coord, coord in enumerate(coord_list):
                cmds.connectAttr('{}.{}{}'.format(self.pos_node, attr, coord),
                                 '{}.in{}{}'.format(self.four_node, item_attr, item_coord))

        cmds.connectAttr('{}.output'.format(self.four_node), '{}.inputMatrix'.format(self.dec_node))


class RivetMotionPath(object):
    def __init__(self, obj, surface, fraction=False):
        self.surface = surface
        self.obj = obj
        self.fraction = fraction

        self.param = None
        self.node = None

    def rivet(self):
        point = cmds.xform(self.obj, q=True, ws=True, rp=True)
        self.param = curve.get_closest_U_param(self.surface, point, self.fraction)
        self.node = cmds.createNode('motionPath', n='{}_{}_mPath'.format(self.surface, self.obj))
        cmds.setAttr('{}.fractionMode'.format(self.node), self.fraction)
        cmds.setAttr('{}.uValue'.format(self.node), self.param)
        cmds.connectAttr('{}.worldSpace'.format(self.surface), '{}.geometryPath'.format(self.node))


class RivetPointOnCurve(object):
    def __init__(self, obj, surface, fraction=False):
        self.surface = surface
        self.obj = obj
        self.fraction = fraction

        self.param = None
        self.node = None

    def rivet(self):
        point = cmds.xform(self.obj, q=True, ws=True, rp=True)
        self.param = curve.get_closest_U_param(self.surface, point, self.fraction)
        self.node = cmds.createNode('pointOnCurveInfo', n='{}_{}_pointOnCrv'.format(self.surface, self.obj))
        cmds.setAttr('{}.turnOnPercentage'.format(self.node), self.fraction)
        cmds.setAttr('{}.parameter'.format(self.node), self.param)
        cmds.connectAttr('{}.worldSpace'.format(self.surface), '{}.inputCurve'.format(self.node))