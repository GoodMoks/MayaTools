import maya.cmds as cmds
import MayaTools.tools.aligner.aligner as aligner

reload(aligner)


class AlignerUi(object):

    def __init__(self):
        self.rotate_checkbox = False
        self.scale_checkbox = False
        self.x_axis_checkbox = False
        self.y_axis_checkbox = True
        self.z_axis_checkbox = False
        self.show()

    @classmethod
    def close_window(cls, *args):
        cmds.deleteUI("plane_aligner")

    def rotate_check_box(self, *args):
        self.rotate_checkbox = cmds.checkBox(self.rotate_checkbox_ui, q=True, value=True)

    def scale_check_box(self, *args):
        self.scale_checkbox = cmds.checkBox(self.scale_checkbox_ui, q=True, value=True)

    def axis_check_box(self, *args):
        self.x_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v1=True)
        self.y_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v2=True)
        self.z_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v3=True)

    def build(self, *args):
        aligner.Aligner(self.rotate_checkbox, self.scale_checkbox, self.x_axis_checkbox, self.y_axis_checkbox,
                        self.z_axis_checkbox)

    def show(self):
        if cmds.window("plane_aligner", ex=True, wh=(100, 100)):
            cmds.deleteUI("plane_aligner")

        cmds.window("plane_aligner", t="Aligner")
        cmds.columnLayout("Main_column")

        text_layout = cmds.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                           columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        cmds.separator(h=5, p=text_layout, vis=False)
        cmds.text(l="1. Select objects you want to align", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.text(l="2. Shift select object to be aligned to", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.separator(h=5, p=text_layout)

        axis_layout = cmds.rowColumnLayout("axis_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                           columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.axis_checkbox = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v2=True,
                                              cc=self.axis_check_box)

        checkbox_layout = cmds.rowColumnLayout("checkbox_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                               columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                               columnSpacing=[(1, 20), (2, 20)])
        cmds.separator(h=10, p=checkbox_layout, vis=False)
        cmds.separator(h=10, p=checkbox_layout, vis=False)
        self.rotate_checkbox_ui = cmds.checkBox(label='   Rotate', p=checkbox_layout,
                                                cc=self.rotate_check_box)
        self.scale_checkbox_ui = cmds.checkBox(label='   Scale', p=checkbox_layout, cc=self.scale_check_box)

        button_layout = cmds.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                             columnSpacing=[(1, 20), (2, 20)])
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.button("Align", label='Align', width=100, h=30, c=self.build)
        cmds.button("close", label='Close', width=100, h=30, c=self.close_window)
        cmds.separator(h=10, p=button_layout, vis=False)

        cmds.showWindow()
