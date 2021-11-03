import maya.cmds as cmds

namespace = 'H3'

def get_playback_range():
    """ get playback range

    :return: (start frame, end frame)
    """
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    return (start, end)



def get_average_pos():
    all_pos = []

    jnt = '{}:Jaw_Jnt'.format(namespace)
    world = '{}:Hydra_World_CTRL'.format(namespace)

    time = get_playback_range()
    for time in range(int(time[0]), int(time[1]+1)):
        cmds.currentTime(time)
        pos = cmds.xform(jnt, q=True, t=True, ws=True)
        all_pos.append(pos)


    x_list = []
    y_list = []
    z_list = []
    for pos in all_pos:
        x_list.append(pos[0])
        y_list.append(pos[1])
        z_list.append(pos[2])

    average_x = get_average(x_list)
    average_y = get_average(y_list)
    average_z = get_average(z_list)

    world_z = cmds.getAttr('{}.tz'.format(world))
    print(world_z)
    new_pos = [average_x, 0, average_z ]

    print(new_pos)
    print('{}:Local_CTRL'.format(namespace))
    #cmds.xform('{}:Local_CTRL'.format(namespace), t=new_pos, ws=True)


def get_high(list):
    max = None
    for value in list:
        if not sum:
            max = value[2]
        if value < value[2]:
            max = value[2]
    return max


def get_average(list):
    sum = None
    for value in list:
        if not sum:
            sum = value
        sum += value
    average = sum / len(list)

    return average



get_average_pos()


def align():
    namespace = 'H1'
    pos = [-492.1665946369425, 0, 1313.279584172812]
    cmds.xform('{}:Local_CTRL'.format(namespace), t=pos, ws=True)

#align()

