import maya.cmds as cmds
import MayaTools.core.utils as utils
import maya.api.OpenMaya as om2


sel = cmds.ls()


child = cmds.listRelatives(sel, ad=True)
print len(child)


@utils.time_info
def list_comp(child):
    print len(child)
    [get_transform(x) for x in child if x]

@utils.time_info
def loop(child):
    for x in child:
        if x:
            get_transform(x)

@utils.time_info
def map_loop(child):
    map(get_transform, child)

@utils.time_info
def api_loop():
    dagIt = om2.MItDag(om2.MItDag.kDepthFirst)
    count = 0
    while not dagIt.isDone():
        count += 1
        depNode = om2.MFnDependencyNode(dagIt.currentItem())
        try:
            get_transform(depNode.name())
        except:
            pass

        dagIt.next()

    print count

def get_transform(obj):
    try:
        cmds.xform(obj, piv=True, q=True, ws=True)
    except:
        pass

api_loop()