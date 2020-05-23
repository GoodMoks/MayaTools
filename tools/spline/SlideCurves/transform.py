import maya.cmds as cmds


def between_two_object(first=None, second=None):
    if first and second:
        first_pos = cmds.xform(first, q=True, ws=True, rp=True)
        second_pos = cmds.xform(second, q=True, ws=True, rp=True)
        between_pos = []
        for axis in range(3):
            between = (float(first_pos[axis]) + float(second_pos[axis])) / 2
            between_pos.append(between)

        if between_pos:
            return between_pos
