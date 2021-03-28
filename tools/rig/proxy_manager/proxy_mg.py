from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm
import maya.mel as mel



class ProxyManagerUI(QtWidgets.QDialog):
    WINDOW_INSTANCE = None

    path_icon = r'\\design\Art_Department\Raid\Heroes\417_draconid\preview\417_draconid.png'

    maya_window = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self, parent=maya_window):
        super(ProxyManagerUI, self).__init__(parent)

        self.setWindowTitle('Proxy Manager')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setMinimumSize(150, 250)

        self.all_items = []
        self.selected_item = None

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.connect_widgets()
        self.fill()

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = ProxyManagerUI()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()

    def create_widgets(self):
        self.filter_field = QtWidgets.QLineEdit()
        self.filter_field.setPlaceholderText('Heroes ID')
        self.filter_field.setFixedHeight(20)
        self.filter_field.setMinimumWidth(130)

        self.list_wdg = QtWidgets.QListWidget()
        self.list_wdg.setMinimumSize(130, 80)
        self.list_wdg.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.load_btn = QtWidgets.QPushButton('Load')

        self.heroes_file_lb = QtWidgets.QLabel('Heroes:')
        self.heroes_path_lb = QtWidgets.QLabel('File:')

        self.heroes_file_name = QtWidgets.QLabel()
        self.heroes_path_name = QtWidgets.QLabel()

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.main_ly.setSpacing(10)

        self.heroes_main_ly = QtWidgets.QVBoxLayout()
        self.heroes_file_ly = QtWidgets.QHBoxLayout()
        self.heroes_file_ly.setAlignment(QtCore.Qt.AlignLeft)
        self.heroes_path_ly = QtWidgets.QHBoxLayout()
        self.heroes_path_ly.setAlignment(QtCore.Qt.AlignLeft)
        self.heroes_grp = QtWidgets.QGroupBox()
        self.heroes_grp.setTitle('Heroes')
        self.heroes_grp.setAlignment(QtCore.Qt.AlignCenter)

    def add_to_layout(self):
        self.main_ly.addWidget(self.filter_field)
        self.main_ly.addWidget(self.list_wdg)

        self.heroes_file_ly.addWidget(self.heroes_file_lb)
        self.heroes_file_ly.addWidget(self.heroes_file_name)

        self.heroes_path_ly.addWidget(self.heroes_path_lb)
        self.heroes_path_ly.addWidget(self.heroes_path_name)

        self.heroes_main_ly.addLayout(self.heroes_file_ly)
        self.heroes_main_ly.addLayout(self.heroes_path_ly)

        self.heroes_grp.setLayout(self.heroes_main_ly)

        self.main_ly.addWidget(self.heroes_grp)
        self.main_ly.addWidget(self.load_btn)

    def connect_widgets(self):
        self.list_wdg.itemSelectionChanged.connect(self.select_item)
        self.list_wdg.itemDoubleClicked.connect(self.reload_ref)
        self.load_btn.clicked.connect(self.reload_ref)
        self.filter_field.textChanged.connect(self.fill)

    def select_item(self):
        index = self.list_wdg.selectedIndexes()
        if index:
            item = self.all_items[index[0].row()]
            self.selected_item = item
        else:
            self.selected_item = None
        self.update_heroes()

    def fill(self, filter=None):
        self.all_items = []
        proxyMsg = self.get_all_node('proxyManager')
        if proxyMsg:
            if len(proxyMsg) == 1:
                proxy = self.get_proxy(proxyMsg[0])
                for p in proxy:
                    tag = p.proxyTag.get()
                    if filter:
                        if tag.startswith(filter):
                            self.all_items.append(p)
                    else:
                        self.all_items.append(p)
                self.list_wdg.clear()
                for item in self.all_items:
                    tag = item.proxyTag.get()
                    item = QtWidgets.QListWidgetItem(tag)
                    self.list_wdg.addItem(item)

    def update_heroes(self):
        if self.selected_item:
            path = self.get_ref_path(self.selected_item)
            if path:
                self.heroes_path_name.setText(path)
                file_name = path.split('/')[-1]
                self.heroes_file_name.setText(file_name)
        else:
            self.heroes_file_name.clear()
            self.heroes_path_name.clear()

    def get_all_node(self, type):
        return pm.ls(type=type) or []

    def get_file_name(self, node):
        return pm.referenceQuery(node, )

    def get_ref_path(self, node):
        return pm.referenceQuery(node, f=True)

    def get_ref_node(self, node):
        return pm.referenceQuery(node, rfn=True)

    def get_proxyMsg(refNode):
        return pm.listConnections(refNode + '.proxyMsg', s=True, d=False)

    def reload_ref(self):
        if self.selected_item:
            mel.eval('proxySwitch {}'.format(self.selected_item))

    def get_proxy(self, proxyMsg):
        return pm.listConnections('{}.proxyList'.format(proxyMsg), s=False, d=True) or []

    def start(self):
        manager = self.get_all_node('proxyManager')[0]
        proxy = self.get_proxy(manager)
        self.reload_ref(proxy[1])
