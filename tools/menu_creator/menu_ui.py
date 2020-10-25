import pymel.core as pm
from PySide2 import QtWidgets
import MayaTools.core.data as data
from PySide2 import QtCore
from PySide2 import QtGui


class CustomTreeWidget(QtWidgets.QTreeWidget):
    pass


class MenuEditor(QtWidgets.QDialog):
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    PATH = r'E:\Work\Pipeline\MayaTools\tools\menu_creator\menu'

    def __init__(self, parent=MAYA):
        super(MenuEditor, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.make_connections()

    def create_widgets(self):
        self.menu_tree = QtWidgets.QTreeWidget()
        self.menu_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.menu_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.menu_tree.setHeaderHidden(True)

        self.add_item_btn = QtWidgets.QPushButton('Item')
        self.add_submenu_btn = QtWidgets.QPushButton('Submenu')
        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/deleteActive.png'))
        self.delete_btn.setIcon(icon)

        self.label = QtWidgets.QLineEdit()

        self.divider = QtWidgets.QCheckBox()

        self.python_radio = QtWidgets.QRadioButton('Python')
        self.python_radio.setChecked(True)
        self.mel_radio = QtWidgets.QRadioButton('MEL')

        self.languages_btn = QtWidgets.QButtonGroup()
        self.languages_btn.addButton(self.python_radio)
        self.languages_btn.addButton(self.mel_radio)

        self.scripts_edit = QtWidgets.QTextEdit()

        self.execute_btn = QtWidgets.QPushButton('Execute All')
        self.save_btn = QtWidgets.QPushButton('Save')

        self.menu_tree_base = QtWidgets.QWidget()
        self.options_base = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter(self)

    def create_layout(self):
        self.main_ly = QtWidgets.QHBoxLayout(self)
        self.main_ly.setContentsMargins(1, 1, 1, 1)
        self.menu_ly = QtWidgets.QVBoxLayout()

        self.options_ly = QtWidgets.QVBoxLayout()
        self.options_ly.setAlignment(QtCore.Qt.AlignTop)

        self.label_ly = QtWidgets.QFormLayout()
        self.label_ly.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.label_ly.addRow('Label:', self.label)

        self.languages_ly = QtWidgets.QHBoxLayout()
        self.languages_ly.setSpacing(50)
        self.languages_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.languages_ly.addWidget(self.mel_radio)
        self.languages_ly.addWidget(self.python_radio)

        self.scripts_ly = QtWidgets.QVBoxLayout()
        self.scripts_ly.addLayout(self.languages_ly)
        self.scripts_ly.addWidget(self.scripts_edit)

        self.scripts_btn_ly = QtWidgets.QHBoxLayout()
        self.scripts_btn_ly.addWidget(self.save_btn)
        self.scripts_btn_ly.addWidget(self.execute_btn)

        self.scripts_ly.addLayout(self.scripts_btn_ly)

        self.scripts_tab = QtWidgets.QGroupBox('Command')
        self.scripts_tab.setAlignment(QtCore.Qt.AlignCenter)
        self.scripts_tab.setLayout(self.scripts_ly)


        self.options_ly.addLayout(self.label_ly)
        self.options_ly.addWidget(self.scripts_tab)

        # splitter

        self.add_btn_ly = QtWidgets.QHBoxLayout()
        self.add_btn_ly.addWidget(self.add_item_btn)
        self.add_btn_ly.addWidget(self.add_submenu_btn)
        self.add_btn_ly.addWidget(self.delete_btn)

        self.menu_ly.addLayout(self.add_btn_ly)
        self.menu_ly.addWidget(self.menu_tree)
        self.menu_tree_base.setLayout(self.menu_ly)
        self.options_base.setLayout(self.options_ly)

        self.splitter.addWidget(self.menu_tree_base)
        self.splitter.addWidget(self.options_base)
        self.main_ly.addWidget(self.splitter)

    def make_connections(self):
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_submenu_btn.clicked.connect(self.add_submenu)
        self.menu_tree.itemSelectionChanged.connect(self.select_item)
        self.languages_btn.buttonClicked.connect(self.change_language)

    def change_language(self, *args):
        print args

    def enabled_widgets(self, state):
        widgets = [self.python_radio, self.mel_radio]
        for w in widgets:
            w.setEnabled(state)

    def get_selected(self):
        selected = self.menu_tree.selectedItems()
        if not len(selected) == 1:
            return
        return selected[0]

    def select_item(self, *args):
        selected = self.get_selected()
        if not selected:
            self.label.setText('')
            self.enabled_widgets(False)
            return
        self.label.setText(selected.data(0, QtCore.Qt.UserRole))
        self.enabled_widgets(True)

    def add_item(self):
        item = QtWidgets.QTreeWidgetItem(['Item'])
        item.setFlags(
            QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
            QtCore.Qt.ItemIsDragEnabled)
        item.setTextColor(0, QtGui.QColor(0, 255, 0))
        item.setData(0, QtCore.Qt.UserRole, 'Item')
        self.menu_tree.addTopLevelItem(item)

    def add_submenu(self):
        item = QtWidgets.QTreeWidgetItem(['Sub Menu'])
        item.setFlags(
            QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        item.setTextColor(0, QtGui.QColor(255, 0, 0))
        item.setData(0, QtCore.Qt.UserRole, 'sunmenu')
        self.menu_tree.addTopLevelItem(item)

    def showUI(self):
        try:
            ui.close()
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = MenuEditor()
        ui.show()
