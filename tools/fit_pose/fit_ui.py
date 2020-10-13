import pymel.core as pm
import fit_controller
import MayaTools.core.ui.separator as separator

reload(fit_controller)

class FitUI(object):
    WINDOW_NAME = 'FitPose'
    WIDTH = 150

    def __init__(self):
        self.controller = fit_controller.FitController()
        self.showUI()

    def showUI(self):
        if pm.window(self.WINDOW_NAME, exists=True):
            pm.deleteUI(self.WINDOW_NAME)

        with pm.window(self.WINDOW_NAME, title='Fit T-pose', s=True, rtf=True, wh=(self.WIDTH, 100)) as self.window:
            with pm.autoLayout() as main_ly:
                separator.Separator('Pose', parent=main_ly, w=self.WIDTH, h=20)
                with pm.horizontalLayout():
                    update_btn = pm.button(label='Update', c=pm.Callback(self.controller.update),
                                           ann='Select Fit geometry to delete all fit joint and set new pose')
                    reset_btn = pm.button(label='Reset', c=pm.Callback(self.controller.reset),
                                          ann='Select Fit geometry to reset all fit changes')
                    check_btn = pm.button(label='Check', c=pm.Callback(self.controller.check, self.window),
                                          ann='Select Fit geometry to check for changes ')
                    # bindPose_btn = pm.button(label='bindPose', c=pm.Callback(self.controller.go_to_bindPose),
                    #                       ann='Select Fit geometry to check for changes ')
                    # reset_bindPose = pm.button(label='reset_bindPose', c=pm.Callback(self.controller.reset_bidnPose),
                    #                          ann='Select Fit geometry to check for changes ')
                    separator.Separator('Joints', parent=main_ly, w=self.WIDTH, h=20)
                with pm.horizontalLayout():
                    add_btn = pm.button(label='Add', c=pm.Callback(self.controller.add),
                                        ann='Select joint and mesh')
                    add_modified_btn = pm.button(label='Modified', c=pm.Callback(self.controller.add_modified),
                                        ann='Select joint and mesh')

