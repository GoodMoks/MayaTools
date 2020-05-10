import pymel.core as pm
import MayaTools.tools.proxy_mesh.proxy_mesh as proxy_mesh

class ProxyMeshUI(object):
    MAIN_NAME = 'ProxyMesh'
    JOINTS_WINDOW = 'JointsCheck'

    def __init__(self):
        self.controller = proxy_mesh.ProxyController()

    def showUI(self):
        if pm.window(self.MAIN_NAME, exists=True):
            pm.deleteUI(self.MAIN_NAME)

        with pm.window(self.MAIN_NAME, s=True, rtf=True, title='Proxy Mesh') as self.main:
            with pm.verticalLayout():
                with pm.horizontalLayout():
                    pm.iconTextButton(style='iconAndTextVertical', image1='duplicateCurve.png', label='Duplicate',
                                      c=pm.duplicate)
                    pm.iconTextButton(style='iconAndTextVertical', image1='polyReduce.png', label='Reduce',
                                      c=pm.mel.ReducePolygon)
                    pm.iconTextButton(style='iconAndTextVertical', image1='paintSkinWeights.png', label='Paint',
                                      c=pm.mel.ArtPaintSkinWeightsTool)
                    pm.iconTextButton(style='iconAndTextVertical', image1='copySkinWeight.png', label='Copy Skin',
                                      c=pm.mel.CopySkinWeights)

                with pm.autoLayout(orientation='horizontal', spacing=2, reversed=False, ratios=None):
                    pm.button('Duplicate Faces', c=pm.Callback(self.controller.duplicate_faces))
                    pm.button('Copy Skin', c=pm.Callback(self.controller.copy_skin))
                    pm.button('Check Joints', c=pm.Callback(self.check_joints))

    def show_joints_check_UI(self):
        if pm.window(self.JOINTS_WINDOW, exists=True):
            pm.deleteUI(self.JOINTS_WINDOW)

        with pm.window(self.JOINTS_WINDOW, s=True, rtf=True, title='Influences Joints', p=self.main) as self.inf_window:
            with pm.verticalLayout() as self.vertical_ly:
                with pm.tabLayout() as self.tab_ly:
                    self.source_list = pm.iconTextScrollList(allowMultiSelection=True,
                                                             sc=lambda: self.select_items(self.source_list))
                    self.target_list = pm.iconTextScrollList(allowMultiSelection=True,
                                                             sc=lambda: self.select_items(self.target_list))

    def select_items(self, scroll):
        selected = scroll.getSelectItem()
        pm.select(selected)

    def check_joints(self):
        different_joints = self.controller.get_different_joints()
        if different_joints:
            self.show_joints_check_UI()
            self.tab_ly.setTabLabel((self.source_list, different_joints[0][0]))
            self.tab_ly.setTabLabel((self.target_list, different_joints[1][0]))

            for scroll_list, value in zip([self.source_list, self.target_list], different_joints):
                mesh, value = value
                if value:
                    scroll_list.append(value)