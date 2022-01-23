import maya.cmds as cmds
import MayaTools.core.animation as animation
import MayaTools.core.utils as utils


# @utils.undoable
# def build():
#     aim_jnt = cmds.createNode('joint', n=aim_jnt_name)
#     cmds.parent(aim_jnt, 'Root_Jnt')
#     cmds.parent(['R_Mace_Jnt', 'L_Mace_Jnt'], aim_jnt_name)
#     bake_locs()


def bake_locs():
    locs = []
    jnts = [u'Back_Neck_Top_Armor', u'Back_Neck_Armor', u'R_Back_Chest_Jnt', u'C_Back_Chest_Jnt', u'L_Back_Chest_Jnt',
            u'R_Front_Shoulder_Armor_Jnt', u'R_Front_Neck_Armor_Jnt', u'L_Front_Neck_Armor_Jnt',
            u'L_Front_Shoulder_Armor_Jnt', u'L_Front_Chest_Armor', u'Front_Chest_Armor', u'R_Front_Chest_Armor']
    for jnt in jnts:
        loc = cmds.spaceLocator(n='{}_bakeLoc'.format(jnt))[0]
        locs.append(loc)
        cmds.parentConstraint(jnt, loc, mo=False)

    time = animation.get_playback_range()
    cmds.bakeSimulation(locs, t=time)

    for loc, jnt in zip(locs, jnts):
        cmds.parentConstraint(loc, jnt, mo=False)
        cmds.parent(jnt, 'Body_Jnt')

    cmds.bakeSimulation(jnts, t=time)
    cmds.delete(locs)

# def start():
#     locs = bake_locs()
#     time = animation.get_playback_range()
#     cmds.bakeSimulation(locs, t=time)
#
#     for jnt, loc in zip(jnt_list, locs):
#         cmds.parentConstraint(loc, jnt, mo=False)
#         cmds.parent(jnt, 'Root_Jnt')
#
#     cmds.bakeSimulation(jnt_list, t=time)
