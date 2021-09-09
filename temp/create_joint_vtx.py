import maya.cmds as cmds

def create_joint_vtx():
    cmds.undoInfo(openChunk=True)
    sel = cmds.ls(sl=True, fl=True)
    for s in sel:
        pos = cmds.xform(s, q=True, t=True, ws=True )
        joint = cmds.createNode('joint')
        cmds.xform(joint, t=pos)
    cmds.undoInfo(closeChunk=True)

create_joint_vtx()