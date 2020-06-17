import maya.cmds as cmds
import MayaTools.core.surface as surface
reload(surface)


def test_uv():
    sel = cmds.ls(sl=True)

    if sel:
        points = surface.get_closest_UV_surface(sel[1], cmds.xform(sel[0], q=True, ws=True, rp=True), False)
        print points




class SurfaceSlide(object):
    def __init__(self, surface, fraction=True):
        pass




