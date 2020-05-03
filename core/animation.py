import maya.cmds as cmds


def get_playback_range():
    """ get playback range

    :return:
    """
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    return (start, end)