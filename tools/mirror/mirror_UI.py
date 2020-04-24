import pymel.core as pm
import MayaTools.tools.mirror.mirror as mirror

reload(mirror)


class MirrorUi(object):

    def __init__(self):
        self.rotate_checkbox = True
        self.scale_checkbox = False
        self.x_axis_checkbox = True
        self.y_axis_checkbox = None
        self.z_axis_checkbox = None
        self.show()

    @classmethod
    def close_window(cls, *args):
        pm.deleteUI("mirror_ctrl")

    def rotate_check_box(self):
        self.rotate_checkbox = pm.checkBox(self.rotate_checkbox_ui, q=True, value=True)

    def scale_check_box(self):
        self.scale_checkbox = pm.checkBox(self.scale_checkbox_ui, q=True, value=True)

    def axis_check_box(self):
        self.x_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v1=True)
        self.y_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v2=True)
        self.z_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v3=True)

    def build(self):
        mirror.MirrorCtrl(None, 'L_', 'R_', self.x_axis_checkbox, self.y_axis_checkbox, self.z_axis_checkbox)

    def show(self):
        if pm.window("mirror_ctrl", ex=True, wh=(100, 100)):
            self.close_window()

        pm.window("mirror_ctrl", t="Mirror")
        pm.columnLayout("Main_column")

        text_layout = pm.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                         columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 10)])
        pm.separator(h=5, p=text_layout, vis=False)
        pm.text(l="1. Select objects you want to mirror", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.text(l="2. Specify the objects side identifier ", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.separator(h=2, p=text_layout, vis=False)

        axis_separator_layout = pm.rowColumnLayout("axis_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                   columnAttach=(2, 'both', 2),
                                                   columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                   parent="Main_column",
                                                   columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        pm.separator(h=10, p=axis_separator_layout)
        pm.text(l='axis', p=axis_separator_layout, fn='fixedWidthFont')
        pm.separator(h=10, p=axis_separator_layout)
        pm.separator(h=5, p=axis_separator_layout, vis=False)

        axis_layout = pm.rowColumnLayout("axis_layout", adjustableColumn=True, numberOfColumns=1,
                                         columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])

        self.axis_checkbox = pm.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v1=True,
                                            cc=pm.Callback(self.axis_check_box))
        pm.separator(h=5, p=axis_layout, vis=False)

        side_separator_layout = pm.rowColumnLayout("side_separator_layout", adjustableColumn=True, numberOfColumns=3,
                                                   columnAttach=(2, 'both', 2),
                                                   columnWidth=[(1, 30), (2, 70), (3, 200)],
                                                   parent="Main_column",
                                                   columnSpacing=[(1, 20)], rowSpacing=[(1, 5)])
        pm.separator(h=10, p=side_separator_layout)
        pm.text(l='side', p=side_separator_layout, fn='fixedWidthFont')
        pm.separator(h=10, p=side_separator_layout)
        pm.separator(h=5, p=side_separator_layout, vis=False)

        side_input_layout = pm.rowColumnLayout("side_input_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                               columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                               columnSpacing=[(1, 20), (2, 20)], rowSpacing=[(1, 10)])

        pm.text(l="Original side", p=side_input_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        self.original_side = pm.textField(p=side_input_layout, it='L_')

        pm.text(l="Mirror side", p=side_input_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        self.mirror_side = pm.textField(p=side_input_layout, it='R_')

        button_layout = pm.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                           columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                           columnSpacing=[(1, 20), (2, 20)])
        pm.separator(h=10, p=button_layout, vis=False)
        pm.separator(h=10, p=button_layout, vis=False)
        pm.button("Align", label='Mirror', width=100, h=30, c=pm.Callback(self.build))
        pm.button("close", label='Close', width=100, h=30, c=self.close_window)
        pm.separator(h=10, p=button_layout, vis=False)

        pm.showWindow()
