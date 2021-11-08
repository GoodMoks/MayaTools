import maya.cmds as cmds

# testing #
objects = cmds.ls(sl=1)
start = int(cmds.playbackOptions(q=1, min=1))
end = int(cmds.playbackOptions(q=1, max=1))


def bakeTimeWarp(objects, start, end, killWarp=True):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe
    for i in objects:
        dupe = cmds.duplicate(i, po=1)[0]
        if not cmds.attributeQuery('bakeTimeWarpConnection', node=i, ex=1):
            cmds.addAttr(i, ln='bakeTimeWarpConnection', at='message')
        cmds.connectAttr(dupe + '.message', i + '.bakeTimeWarpConnection')
    for x in range(start, end + 1):
        cmds.currentTime(x)
        outTime = cmds.getAttr('time1.outTime')
        unwarpedTime = cmds.getAttr('time1.unwarpedTime')
        for i in objects:
            # build a list of all keyed channels.
            keyables = cmds.listAttr(i, k=1)
            keyedChans = [f for f in keyables if cmds.keyframe(i + '.' + f, q=1, n=1)]
            dupe = cmds.listConnections(i + '.bakeTimeWarpConnection')[0]
            for chan in keyedChans:
                val = cmds.getAttr(i + '.' + chan, t=outTime)
                cmds.setAttr(dupe + '.' + chan, val)
                cmds.setKeyframe(dupe + '.' + chan, t=unwarpedTime)
    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        dupe = cmds.listConnections(i + '.bakeTimeWarpConnection')[0]
        chans = [f for f in cmds.listAttr(dupe, k=1) if cmds.keyframe(dupe + '.' + f, q=1, n=1)]
        for chan in chans:
            animCurve = cmds.keyframe(dupe + '.' + chan, q=1, n=1)[0]
            oldCurve = cmds.keyframe(i + '.' + chan, q=1, n=1)
            cmds.connectAttr(animCurve + '.output', i + '.' + chan, f=1)
            cmds.delete(oldCurve)
        cmds.delete(dupe)
        cmds.deleteAttr(i + '.bakeTimeWarpConnection')
    if killWarp:
        timeWarp = cmds.listConnections('time1.timewarpIn_Raw')[0]
        cmds.delete(timeWarp)
