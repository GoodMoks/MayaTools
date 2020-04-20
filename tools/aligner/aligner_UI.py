import pymel.core as pm
import MayaTools.tools.aligner.aligner as aligner

reload(aligner)


class AlignerUi(object):

    def __init__(self):
        self.rotate_checkbox = True
        self.scale_checkbox = False
        self.x_axis_checkbox = True
        self.y_axis_checkbox = True
        self.z_axis_checkbox = True
        self.show()

    @classmethod
    def close_window(cls, *args):
        pm.deleteUI("plane_aligner")

    def rotate_check_box(self):
        self.rotate_checkbox = pm.checkBox(self.rotate_checkbox_ui, q=True, value=True)

    def scale_check_box(self):
        self.scale_checkbox = pm.checkBox(self.scale_checkbox_ui, q=True, value=True)

    def axis_check_box(self):
        self.x_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v1=True)
        self.y_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v2=True)
        self.z_axis_checkbox = pm.checkBoxGrp(self.axis_checkbox, q=True, v3=True)

    def build(self):
        aligner.Aligner(self.rotate_checkbox, self.scale_checkbox, self.x_axis_checkbox, self.y_axis_checkbox,
                        self.z_axis_checkbox)

    def show(self):
        if pm.window("plane_aligner", ex=True, wh=(100, 100)):
            pm.deleteUI("plane_aligner")

        pm.window("plane_aligner", t="Aligner")
        pm.columnLayout("Main_column")

        text_layout = pm.rowColumnLayout("text_layout", adjustableColumn=True, numberOfColumns=1,
                                         columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        pm.separator(h=5, p=text_layout, vis=False)
        pm.text(l="1. Select objects you want to align", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.text(l="2. Shift select object to be aligned to", p=text_layout, bgc=[0.2, 0.2, 0.28], fn="fixedWidthFont")
        pm.separator(h=5, p=text_layout)

        axis_layout = pm.rowColumnLayout("axis_layout", adjustableColumn=True, numberOfColumns=1,
                                         columnAttach=(2, 'both', 2), columnWidth=[(1, 300)], parent="Main_column",
                                         columnSpacing=[(1, 20)], rowSpacing=[(1, 20)])
        self.axis_checkbox = pm.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'], v2=True,
                                            cc=pm.Callback(self.axis_check_box))

        checkbox_layout = pm.rowColumnLayout("checkbox_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                             columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                             columnSpacing=[(1, 20), (2, 20)])
        pm.separator(h=10, p=checkbox_layout, vis=False)
        pm.separator(h=10, p=checkbox_layout, vis=False)
        self.rotate_checkbox_ui = pm.checkBox(label='   Rotate', p=checkbox_layout,
                                              cc=pm.Callback(self.rotate_check_box))
        self.scale_checkbox_ui = pm.checkBox(label='   Scale', p=checkbox_layout, cc=pm.Callback(self.scale_check_box))

        button_layout = pm.rowColumnLayout("button_layout", numberOfColumns=2, columnAttach=(2, 'both', 2),
                                           columnWidth=[(1, 150), (2, 150)], parent="Main_column",
                                           columnSpacing=[(1, 20), (2, 20)])
        pm.separator(h=10, p=button_layout, vis=False)
        pm.separator(h=10, p=button_layout, vis=False)
        pm.button("Align", label='Align', width=100, h=30, c=pm.Callback(self.build))
        pm.button("close", label='Close', width=100, h=30, c=self.close_window)
        pm.separator(h=10, p=button_layout, vis=False)

        pm.showWindow()
