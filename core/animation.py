import pymel.core as pm

def get_playback_range():
    """ get playback range

    :return:
    """
    start = pm.playbackOptions(q=True, min=True)
    end = pm.playbackOptions(q=True, max=True)
    return (start, end)