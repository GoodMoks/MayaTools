import pymel.core as pm
import MayaTools.tools.joint_chain_breaker.joint_chain_breacker_controller as controller

reload(controller)


class AddInBetweenUI(object):

    def __init__(self):
        self.parent_flag = [False, ]
        self.divide_point = [2, ]
        self.show()

    @classmethod
    def close_window(cls):
        pm.deleteUI("jnt_between")

    def check_box(self, *args):
        flag = args[0]
        self.parent_flag.pop()
        self.parent_flag.append(flag)
        flag = self.parent_flag

        return flag

    def int_field(self, *args):
        dp = args[0] + 1
        self.divide_point.pop()
        self.divide_point.append(dp)
        dp = self.divide_point

        return dp

    def show(self):
        if pm.window("jnt_between", ex=True, wh=(200, 200)):
            pm.deleteUI("jnt_between")

        pm.window("jnt_between", t="Joint Between")
        pm.columnLayout("Main_column")

        slider_layout = pm.rowColumnLayout("slider_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 400)], parent="Main_column",
                                           columnSpacing=[(1, 10)], rowSpacing=[(1, 10)])
        pm.separator(h=15, p=slider_layout, vis=False)
        pm.text(l="Set number of inbetween joints", p=slider_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.separator(h=5, p=slider_layout)
        slider = pm.intSliderGrp('slider', field=True, min=1, value=1, step=1, p=slider_layout,
                                 dc=self.int_field)
        pm.separator(h=1, p=slider_layout, vis=False)
        checkbox = pm.checkBox(label='   Create hierarchy', p=slider_layout, cc=self.check_box)
        pm.separator(h=20, p=slider_layout)

        button_layout = pm.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                           columnWidth=[(1, 200), (2, 200)], parent="Main_column",
                                           columnSpacing=[(1, 10), (2, 10)])
        pm.separator(h=5, p=button_layout, vis=False)
        pm.separator(h=5, p=button_layout, vis=False)
        pm.button("add_inbetween", label='Add inbetween', width=100, h=30, c=controller.joint_insert)
        pm.button("close", label='Close', width=100, h=30, c=self.close_window)
        pm.separator(h=10, p=button_layout, vis=False)

        pm.showWindow()
