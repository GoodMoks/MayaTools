import pymel.core as pm
import fit_controller
import MayaTools.core.ui.separator


class FitUI(object):
    WINDOW_NAME = 'FitPose'
    WIDTH = 150

    def __init__(self):
        self.controller = fit_controller.FitController()
        self.showUI()

    def showUI(self):
        if pm.window(self.WINDOW_NAME, exists=True):
            pm.deleteUI(self.WINDOW_NAME)

        with pm.window(self.WINDOW_NAME, title='Fit T-pose', s=False, rtf=True, wh=(self.WIDTH, 100)) as self.window:
            with pm.columnLayout(adj=True) as main_ly:
                MayaTools.utils.ui.separator.Separator('Pose', parent=main_ly, w=self.WIDTH, h=20)
                with pm.horizontalLayout() as pose_ly:
                    update_btn = pm.button(label='Update', c=pm.Callback(self.controller.update_mesh),
                                           ann='Select Fit geometry to delete all fit joint and set new pose')
                    reset_btn = pm.button(label='Reset', c=pm.Callback(self.controller.reset_mesh),
                                          ann='Select Fit geometry to reset all fit changes')
                    check_btn = pm.button(label='Check', c=pm.Callback(self.controller.check_mesh, self.window),
                                          ann='Select Fit geometry to check for changes ')
                    MayaTools.utils.ui.separator. Separator('Joints', parent=main_ly, w=self.WIDTH, h=20)
                with pm.horizontalLayout() as joint_ly:
                    add_btn = pm.button(label='Add', c=pm.Callback(self.controller.add_fit),
                                        ann='Select joint and mesh')
                    delete_btn = pm.button(label='Delete', c=pm.Callback(self.controller.delete_fit),
                                           ann='Select mesh to delete all fit joint and changes')
