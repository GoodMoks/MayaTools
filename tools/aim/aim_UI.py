import maya.OpenMaya as om
import pymel.core as pm
import MayaTools.tools.aim.aim as aim

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
        pm.deleteUI("aim")

    def aim_axis_check_box(self):
        self.x_aim = pm.checkBoxGrp(self.aim_axis_checkbox, q=True, v1=True)
        self.y_aim = pm.checkBoxGrp(self.aim_axis_checkbox, q=True, v2=True)
        self.z_aim = pm.checkBoxGrp(self.aim_axis_checkbox, q=True, v3=True)

    def up_axis_check_box(self):
        self.x_up = pm.checkBoxGrp(self.up_axis_checkbox, q=True, v1=True)
        self.y_up = pm.checkBoxGrp(self.up_axis_checkbox, q=True, v2=True)
        self.z_up = pm.checkBoxGrp(self.up_axis_checkbox, q=True, v3=True)

    def build(self):
        sel = pm.selected()
        if not sel:
            om.MGlobal.displayError('Nothing is currently selected')
            return

        aim.AimObject(sel[0], sel[1], sel[2], self.x_aim, self.y_aim, self.z_aim, self.x_up, self.y_up, self.z_up)

    def show(self):
        if pm.window("aim", ex=True, wh=(100, 100)):
            self.close_window()

        pm.window("aim", t="AIM")
        pm.columnLayout("Main_column")

        axis_separator_layout = pm.rowColumnLayout("axis_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                   columnAttach=(2, 'both', 2),
                                                   columnWidth=[(1, 30), (2, 160), (3, 140)],
                                                   parent="Main_column",
                                                   columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        pm.separator(h=10, p=axis_separator_layout)
        pm.text(l='"To Do" sequence ', p=axis_separator_layout, fn='fixedWidthFont')
        pm.separator(h=10, p=axis_separator_layout)
        pm.separator(h=5, p=axis_separator_layout, vis=False)

        text_layout = pm.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                         columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 10)])
        pm.separator(h=5, p=text_layout, vis=False)
        pm.text(l="1. Select eye object", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.text(l="2. Select target object ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.text(l="3. Select up vector object ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.separator(h=2, p=text_layout, vis=False)

        aim_axis_separator_layout = pm.rowColumnLayout("aim_axis_separator_layout", adjustableColumn=True,
                                                       numberOfColumns=3,
                                                       columnAttach=(2, 'both', 2),
                                                       columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                       parent="Main_column",
                                                       columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        pm.separator(h=10, p=aim_axis_separator_layout)
        pm.text(l='AIM', p=aim_axis_separator_layout, fn='fixedWidthFont')
        pm.separator(h=10, p=aim_axis_separator_layout)
        pm.separator(h=5, p=aim_axis_separator_layout, vis=False)

        aim_axis_layout = pm.rowColumnLayout("aim_axis_layout", adjustableColumn=True, numberOfColumns=1,
                                             columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                             columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.aim_axis_checkbox = pm.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v1=True,
                                                cc=pm.Callback(self.aim_axis_check_box), p=aim_axis_layout)

        up_axis_separator_layout = pm.rowColumnLayout("up_axis_separator_layout", adjustableColumn=True,
                                                      numberOfColumns=3,
                                                      columnAttach=(2, 'both', 2),
                                                      columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                      parent="Main_column",
                                                      columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        pm.separator(h=10, p=up_axis_separator_layout)
        pm.text(l='Up', p=up_axis_separator_layout, fn='fixedWidthFont')
        pm.separator(h=10, p=up_axis_separator_layout)
        pm.separator(h=5, p=up_axis_separator_layout, vis=False)

        up_axis_layout = pm.rowColumnLayout("up_axis_layout", adjustableColumn=True, numberOfColumns=1,
                                            columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                            columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.up_axis_checkbox = pm.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v2=True,
                                               cc=pm.Callback(self.up_axis_check_box), p=up_axis_layout)

        button_layout = pm.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                           columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                           columnSpacing=[(1, 20), (2, 20)])
        pm.separator(h=10, p=button_layout, vis=False)
        pm.separator(h=10, p=button_layout, vis=False)
        pm.button("Align", label='Do AIM', width=100, h=30, c=pm.Callback(self.build))
        pm.button("close", label='Close', width=100, h=30, c=self.close_window)
        pm.separator(h=10, p=button_layout, vis=False)

        pm.showWindow()
