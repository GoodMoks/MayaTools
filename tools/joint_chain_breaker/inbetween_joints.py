import maya.cmds as cmds
import maya.OpenMaya as om

parent_flag = [False, ]
divide_point = [2, ]


class Add_Inbetween_UI(object):

    def __init__(self):
        pass

    @classmethod
    def close_window(cls, *args):
        cmds.deleteUI("jnt_between")

    @classmethod
    def add_between_jnt_ui(cls):
        if cmds.window("jnt_between", ex=True, wh=(200, 200)):
            cmds.deleteUI("jnt_between")

        cmds.window("jnt_between", t="Joint Between")
        cmds.columnLayout("Main_column")

        slider_layout = cmds.rowColumnLayout("slider_layout", adjustableColumn=True, numberOfColumns=1,
                                             columnAttach=(2, 'both', 2), columnWidth=[(1, 400)], parent="Main_column",
                                             columnSpacing=[(1, 10)], rowSpacing=[(1, 10)])
        cmds.separator(h=15, p=slider_layout, vis=False)
        cmds.text(l="Set number of inbetween joints", p=slider_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.separator(h=5, p=slider_layout)
        slider = cmds.intSliderGrp('slider', field=True, min=1, value=1, step=1, p=slider_layout, dc=int_field)
        cmds.separator(h=1, p=slider_layout, vis=False)
        checkbox = cmds.checkBox(label='   Create hierarchy', p=slider_layout, cc=check_box)
        cmds.separator(h=20, p=slider_layout)

        button_layout = cmds.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 200), (2, 200)], parent="Main_column",
                                             columnSpacing=[(1, 10), (2, 10)])
        cmds.separator(h=5, p=button_layout, vis=False)
        cmds.separator(h=5, p=button_layout, vis=False)
        cmds.button("add_inbetween", label='Add inbetween', width=100, h=30, c=joint_insert)
        cmds.button("close", label='Close', width=100, h=30, c=cls.close_window)
        cmds.separator(h=10, p=button_layout, vis=False)

        cmds.showWindow()


def check_box(*args):
    flag = args[0]
    parent_flag.pop()
    parent_flag.append(flag)

    return flag


def int_field(*args):
    dp = args[0] + 1
    divide_point.pop()
    divide_point.append(dp)

    return dp


def list_of_jnt():
    # returns list of selected objects

    sel_jnt = cmds.ls(sl=True, l=True)

    if len(sel_jnt) != 2:
        om.MGlobal.displayError("Select two joint to add joints between them")
        return

    return sel_jnt


def get_transform(obj=None):
    # returns transformation MVector of given object

    xtr = cmds.xform(obj, q=True, piv=True, ws=True)
    mv = om.MVector(xtr[0], xtr[1], xtr[2])

    return mv


def vector_divide(v, dp):
    div_distance = v / dp

    return div_distance


def get_oriente(obj):
    rotation = cmds.xform(obj, q=True, ro=True, ws=True)
    rv = om.MVector(rotation[0], rotation[1], rotation[2])

    return rv


def create_jnt(v, par):
    rv = get_oriente(par)
    cmds.select(cl=True)
    joint = cmds.joint(p=(v.x, v.y, v.z), o=(rv.x, rv.y, rv.z))
    return joint


def insert_jnt(v, div_dist, dp, par):
    added_jnt = []

    for i in range(dp - 1):
        v += div_dist
        jnt = create_jnt(v, par)
        added_jnt.append(jnt)

    return added_jnt


def parent_jnt(par, chain, ch):
    for i in range(len(chain) - 1):
        cmds.parent(chain[i], chain[i + 1])

    cmds.parent(chain[-1], par)
    cmds.parent(ch, chain[0])


def joint_insert(dp):
    dp = divide_point[-1]

    if list_of_jnt():

        par, ch = list_of_jnt()

        v1 = get_transform(par)
        v2 = get_transform(ch)

        distance = v1 - v2
        div_dist = vector_divide(distance, dp)

        added_jnt = insert_jnt(v2, div_dist, dp, par)

        if parent_flag[0]:
            parent_jnt(par, added_jnt, ch)


ui = Add_Inbetween_UI
ui.add_between_jnt_ui()
