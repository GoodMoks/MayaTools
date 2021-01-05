import pymel.core as pm
import aim_chain_controller

reload(aim_chain_controller)

class AimChainUI(object):
    WINDOW_NAME = 'AimChaim'

    def __init__(self):
        self.showUI()
        self.controller = aim_chain_controller.AimChainController()

    def showUI(self):
        if pm.window(self.WINDOW_NAME, exists=True):
            pm.deleteUI(self.WINDOW_NAME)

        with pm.window(self.WINDOW_NAME, title='Aim Chain', s=False, rtf=True, wh=(250, 200)) as self.window:
            with pm.verticalLayout():
                with pm.horizontalLayout(bgc=[0.24, 0.24, 0.24]):
                    pm.text('Rotate Axis', fn='fixedWidthFont')
                    with pm.horizontalLayout():
                        self.radio_col = pm.radioCollection()
                        self.axis_x = pm.radioButton('X')
                        self.axis_y = pm.radioButton('Y')
                        self.axis_z = pm.radioButton('Z')
                        self.axis_x.setSelect()
                with pm.horizontalLayout():
                    self.proxy_btn = pm.button('Proxy', c=pm.Callback(self.add_proxy_chain))
                    self.bake_proxy = pm.button('Bake Proxy', c=pm.Callback(self.bake_proxy))
                with pm.horizontalLayout():
                    self.aim_chain_btn = pm.button('Aim Chain', c=pm.Callback(self.build_aim_chain))
                    self.bake_btn = pm.button('Bake', c=pm.Callback(self.bake_chain))

    def bake_proxy(self):
        self.controller.bake_proxy()

    def bake_chain(self):
        self.controller.bake_chain()

    def build_aim_chain(self):
        axis = self.get_axis()
        if axis:
            self.controller.build_aim_chain(axis=axis)

    def add_proxy_chain(self):
        self.controller.proxy_chain()

    def get_axis(self):
        axis = self.radio_col.getSelect()
        if axis == 'NONE':
            pm.confirmDialog(t='Rotate Axis', message='Select rotate axis',
                             button=['OK'], defaultButton='OK', p=self.window)
            return
        return axis
