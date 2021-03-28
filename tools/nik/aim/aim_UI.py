import maya.OpenMaya as om
import maya.cmds as cmds
import MayaTools.tools.nik.aim.aim as aim

reload(aim)


class AimUi(object):

    def __init__(self):
        self.x_aim = True
        self.y_aim = False
        self.z_aim = False
        self.x_up = False
        self.y_up = True
        self.z_up = False
        self.show()

    @classmethod
    def close_window(cls, *args):
        cmds.deleteUI("aim")

    def aim_axis_check_box(self, *args):
        self.x_aim = cmds.checkBoxGrp(self.aim_axis_checkbox, q=True, v1=True)
        self.y_aim = cmds.checkBoxGrp(self.aim_axis_checkbox, q=True, v2=True)
        self.z_aim = cmds.checkBoxGrp(self.aim_axis_checkbox, q=True, v3=True)

    def up_axis_check_box(self, *args):
        self.x_up = cmds.checkBoxGrp(self.up_axis_checkbox, q=True, v1=True)
        self.y_up = cmds.checkBoxGrp(self.up_axis_checkbox, q=True, v2=True)
        self.z_up = cmds.checkBoxGrp(self.up_axis_checkbox, q=True, v3=True)

    def build(self, *args):
        sel = cmds.ls(sl=True)
        if not sel:
            om.MGlobal.displayError('Nothing is currently selected')
            return

        aim.AimObject(sel[0], sel[1], sel[2], self.x_aim, self.y_aim, self.z_aim, self.x_up, self.y_up, self.z_up)

    def show(self):
        if cmds.window("aim", ex=True, wh=(100, 100)):
            self.close_window()

        cmds.window("aim", t="AIM")
        cmds.columnLayout("Main_column")

        axis_separator_layout = cmds.rowColumnLayout("axis_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                     columnAttach=(2, 'both', 2),
                                                     columnWidth=[(1, 30), (2, 160), (3, 140)],
                                                     parent="Main_column",
                                                     columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        cmds.separator(h=10, p=axis_separator_layout)
        cmds.text(l='"To Do" sequence ', p=axis_separator_layout, fn='fixedWidthFont')
        cmds.separator(h=10, p=axis_separator_layout)
        cmds.separator(h=5, p=axis_separator_layout, vis=False)

        text_layout = cmds.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                           columnSpacing=[(1, 20)], rowSpacing=[(1, 10)])
        cmds.separator(h=5, p=text_layout, vis=False)
        cmds.text(l="1. Select eye object", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.text(l="2. Select target object ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.text(l="3. Select up vector object ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.separator(h=2, p=text_layout, vis=False)

        aim_axis_separator_layout = cmds.rowColumnLayout("aim_axis_separator_layout", adjustableColumn=True,
                                                         numberOfColumns=3,
                                                         columnAttach=(2, 'both', 2),
                                                         columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                         parent="Main_column",
                                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        cmds.separator(h=10, p=aim_axis_separator_layout)
        cmds.text(l='AIM', p=aim_axis_separator_layout, fn='fixedWidthFont')
        cmds.separator(h=10, p=aim_axis_separator_layout)
        cmds.separator(h=5, p=aim_axis_separator_layout, vis=False)

        aim_axis_layout = cmds.rowColumnLayout("aim_axis_layout", adjustableColumn=True, numberOfColumns=1,
                                               columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                               columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.aim_axis_checkbox = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v1=True,
                                                  cc=self.aim_axis_check_box, p=aim_axis_layout)

        up_axis_separator_layout = cmds.rowColumnLayout("up_axis_separator_layout", adjustableColumn=True,
                                                        numberOfColumns=3,
                                                        columnAttach=(2, 'both', 2),
                                                        columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                        parent="Main_column",
                                                        columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        cmds.separator(h=10, p=up_axis_separator_layout)
        cmds.text(l='Up', p=up_axis_separator_layout, fn='fixedWidthFont')
        cmds.separator(h=10, p=up_axis_separator_layout)
        cmds.separator(h=5, p=up_axis_separator_layout, vis=False)

        up_axis_layout = cmds.rowColumnLayout("up_axis_layout", adjustableColumn=True, numberOfColumns=1,
                                              columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                              columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.up_axis_checkbox = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v2=True,
                                                 cc=self.up_axis_check_box, p=up_axis_layout)

        button_layout = cmds.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                             columnSpacing=[(1, 20), (2, 20)])
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.button("Align", label='Do AIM', width=100, h=30, c=self.build)
        cmds.button("close", label='Close', width=100, h=30, c=self.close_window)
        cmds.separator(h=10, p=button_layout, vis=False)

        cmds.showWindow()
