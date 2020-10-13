import maya.api.OpenMaya as om2
import maya.cmds as cmds
from MayaTools.core.utils import time_info
import pymel.core as pm


def gen_locs(range):
    locs = [cmds.spaceLocator()[0] for i in xrange(range)]
    return locs


@time_info
def api_matrix():
    locs = gen_locs(10)
    for loc in locs:
        if not isinstance(loc, basestring):
            continue
        cmds.setAttr('{}.translate'.format(loc), 2, 10, 40)
        x_form = cmds.xform(loc, q=True, ws=True, matrix=True)
        # x_form_pm = pm.xform(loc, q=True, ws=True, matrix=True)
        # world = cmds.getAttr('{}.worldMatrix'.format(loc))
        # world_pm = pm.getAttr('{}.worldMatrix'.format(loc))
        matrix = om2.MMatrix(x_form)
        matrix_inverse = matrix.inverse()
        new_matrix = recompose_matrix(matrix_inverse)
        print new_matrix
        cmds.setAttr('{}.worldMatrix'.format(loc), new_matrix, type='matrix')

        # matrix_pm = pm.datatypes.Matrix(x_form).inverse()
    #cmds.delete(locs)



