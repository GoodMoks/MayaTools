from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import os

import proxy_mg


class PreviewWindow(QtWidgets.QDialog):
    def __init__(self, parent, icon):
        super(PreviewWindow, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Popup)
        self.main_ly = QtWidgets.QHBoxLayout(self)
        self.main_ly.setMargin(5)
        self.image = QtGui.QImage(icon).scaled(600, 450, QtCore.Qt.KeepAspectRatio)
        self.pix_map = QtGui.QPixmap.fromImage(self.image)

        self.pix_map_lb = QtWidgets.QLabel()
        self.pix_map_lb.setPixmap(self.pix_map)
        self.main_ly.addWidget(self.pix_map_lb)


class ProxyManagerPlariumUI(proxy_mg.ProxyManagerUI):
    WINDOW_INSTANCE = None

    def __init__(self):
        super(ProxyManagerPlariumUI, self).__init__()
        self.list_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_wdg.customContextMenuRequested.connect(self.show_preview)

    @classmethod
    def showUI(cls):
        if not cls.window_instance:
            cls.window_instance = ProxyManagerPlariumUI()

        if cls.window_instance.isHidden():
            cls.window_instance.show()
        else:
            cls.window_instance.raise_()
            cls.window_instance.activateWindow()

    def get_preview_icon(self):
        path_ref = self.get_ref_path(self.selected_item)
        heroes_dir = os.path.dirname(os.path.split(path_ref)[0])
        preview_dir = os.path.join(heroes_dir, 'preview')
        if os.path.isdir(preview_dir):
            files = os.listdir(preview_dir)
            if files:
                return os.path.join(preview_dir, files[0])

    def show_preview(self, pos):
        if self.selected_item:
            path = self.get_preview_icon()
            if path:
                self.preview = PreviewWindow(self, path)
                pos = self.list_wdg.mapToGlobal(QtCore.QPoint(pos.x() + 200, pos.y() - 150))
                self.preview.move(pos)
                self.preview.show()
