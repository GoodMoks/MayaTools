import maya.cmds as cmds
import MayaTools.tools.chain_breaker.chain_breaker as controller

reload(controller)


class AddInBetweenUI(object):

    def __init__(self):
        self.parent_flag = False
        self.divide_point = 1
        self.show()

    @classmethod
    def close_window(cls, *args):
        cmds.deleteUI("jnt_between")

    def check_box(self, *args):
        self.parent_flag = cmds.checkBox(self.checkbox, q=True, value=True)

    def int_field(self):
        self.divide_point = cmds.intSliderGrp(self.slider, q=True, value=True)

    def build(self, *args):
        self.int_field()
        controller.JointBreaker(self.divide_point, self.parent_flag)

    def show(self):
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
        self.slider = cmds.intSliderGrp('slider', field=True, min=1, value=1, step=1, p=slider_layout)
        cmds.separator(h=1, p=slider_layout, vis=False)
        self.checkbox = cmds.checkBox(label='   Create hierarchy', p=slider_layout, cc=self.check_box)
        cmds.separator(h=20, p=slider_layout)

        button_layout = cmds.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 200), (2, 200)], parent="Main_column",
                                             columnSpacing=[(1, 10), (2, 10)])
        cmds.separator(h=5, p=button_layout, vis=False)
        cmds.separator(h=5, p=button_layout, vis=False)
        cmds.button("add_inbetween", label='Add inbetween', width=100, h=30, c=self.build)
        cmds.button("close", label='Close', width=100, h=30, c=self.close_window)
        cmds.separator(h=10, p=button_layout, vis=False)

        cmds.showWindow()
