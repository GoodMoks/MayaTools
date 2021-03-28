import maya.cmds as cmds
import MayaTools.tools.nik.mirror.mirror as mirror

reload(mirror)


class MirrorUi(object):

    def __init__(self):
        self.rotate_checkbox = True
        self.scale_checkbox = False
        self.x_axis_checkbox = True
        self.y_axis_checkbox = None
        self.z_axis_checkbox = None
        self.original_side_label = 'L'
        self.mirror_side_label = 'R'
        self.orientation = False
        self.show()

    @classmethod
    def close_window(cls, *args):
        cmds.deleteUI("mirror_ctrl")

    def axis_check_box(self, *args):
        self.x_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v1=True)
        self.y_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v2=True)
        self.z_axis_checkbox = cmds.checkBoxGrp(self.axis_checkbox, q=True, v3=True)

    def original_side(self, *args):
        self.original_side_label = cmds.textField(self.original_side_tf, q=True, text=True)

    def mirror_side(self, *args):
        self.mirror_side_label = cmds.textField(self.mirror_side_tf, q=True, text=True)

    def orientation_check_box(self, *args):
        self.orientation = cmds.checkBox(self.orientation_checkbox, q=True, v=True)

    def build(self, *args):
        mirror.MirrorCtrl(None, self.original_side_label, self.mirror_side_label, self.x_axis_checkbox,
                          self.y_axis_checkbox, self.z_axis_checkbox, self.orientation)

    def show(self):
        if cmds.window("mirror_ctrl", ex=True, wh=(100, 100)):
            self.close_window()

        cmds.window("mirror_ctrl", t="Mirror Selected")
        cmds.columnLayout("Main_column")

        text_layout = cmds.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                           columnSpacing=[(1, 20)], rowSpacing=[(1, 10)])
        cmds.separator(h=5, p=text_layout, vis=False)
        cmds.text(l="1. Select objects you want to mirror", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.text(l="2. Specify the objects side identifier ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        cmds.separator(h=2, p=text_layout, vis=False)

        axis_separator_layout = cmds.rowColumnLayout("axis_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                     columnAttach=(2, 'both', 2),
                                                     columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                     parent="Main_column",
                                                     columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        cmds.separator(h=10, p=axis_separator_layout)
        cmds.text(l='axis', p=axis_separator_layout, fn='fixedWidthFont')
        cmds.separator(h=10, p=axis_separator_layout)
        cmds.separator(h=5, p=axis_separator_layout, vis=False)

        axis_layout = cmds.rowColumnLayout("axis_layout", adjustableColumn=True, numberOfColumns=1,
                                           columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                           columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])

        self.axis_checkbox = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v1=True,
                                              cc=self.axis_check_box)
        cmds.separator(h=5, p=axis_layout, vis=False)
        self.orientation_checkbox = cmds.checkBox(l='Preserve orientation', p=axis_layout, cc=self.orientation_check_box)
        cmds.separator(h=5, p=axis_layout, vis=False)

        side_separator_layout = cmds.rowColumnLayout("side_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                     columnAttach=(2, 'both', 2),
                                                     columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                     parent="Main_column",
                                                     columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        cmds.separator(h=10, p=side_separator_layout)
        cmds.text(l='side', p=side_separator_layout, fn='fixedWidthFont')
        cmds.separator(h=10, p=side_separator_layout)
        cmds.separator(h=5, p=side_separator_layout, vis=False)

        side_input_layout = cmds.rowColumnLayout("side_input_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                                 columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                                 columnSpacing=[(1, 20), (2, 20)], rowSpacing=[(1, 10)])

        cmds.text(l="Original side", p=side_input_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        self.original_side_tf = cmds.textField(p=side_input_layout, it='L', cc=self.original_side)

        cmds.text(l="Mirror side", p=side_input_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        self.mirror_side_tf = cmds.textField(p=side_input_layout, it='R', cc=self.mirror_side)

        button_layout = cmds.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                             columnSpacing=[(1, 20), (2, 20)])
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.separator(h=10, p=button_layout, vis=False)
        cmds.button("Align", label='Mirror', width=100, h=30, c=self.build)
        cmds.button("close", label='Close', width=100, h=30, c=self.close_window)
        cmds.separator(h=10, p=button_layout, vis=False)

        cmds.showWindow()