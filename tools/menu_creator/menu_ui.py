import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import MayaTools.core.ui.utils_qt as utils_qt



class MenuEditor(QtWidgets.QDialog):

    @staticmethod
    def get_script_editor(python=False):
        pm.window()
        pm.columnLayout()
        executer = pm.cmdScrollFieldExecuter()
        if python:
            executer = pm.cmdScrollFieldExecuter(sourceType="python")

        qt_obj = utils_qt.convert_pymel_to_qt(executer)
        return executer, qt_obj

    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    PATH = r'E:\Work\Pipeline\MayaTools\tools\menu_creator\menu'

    def __init__(self, parent=MAYA):
        super(MenuEditor, self).__init__(parent)
        self.setWindowTitle('Menu Manager')
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(':/menuIconBookmarks.png')
        icon.addPixmap(pixmap)
        self.setWindowIcon(icon)

        self.create_widgets()
        self.create_layout()
        self.make_connections()

        print '__init__'

    def create_widgets(self):
        self.menu_filter = QtWidgets.QComboBox()
        self.menu_filter.addItem('fawfaf')
        self.menu_filter.addItem('Menu')
        self.menu_filter.setEditable(True)
        self.menu_filter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.add_menu_btn = QtWidgets.QPushButton()
        self.add_menu_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(':/QR_add.png')
        icon.addPixmap(pixmap)
        self.add_menu_btn.setIcon(icon)

        self.delete_menu_btn = QtWidgets.QPushButton()
        self.delete_menu_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/QR_delete.png'))
        self.delete_menu_btn.setIcon(icon)

        self.menu_tree = QtWidgets.QTreeWidget()
        self.menu_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.menu_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.menu_tree.setHeaderHidden(True)

        self.add_item_btn = QtWidgets.QPushButton('Item')
        self.add_submenu_btn = QtWidgets.QPushButton('Submenu')

        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/UVTBRemove.png'))
        self.delete_btn.setIcon(icon)

        self.label = QtWidgets.QLineEdit()

        self.divider = QtWidgets.QCheckBox('Divider')

        self.python_radio = QtWidgets.QRadioButton('Python')
        self.python_radio.setChecked(True)
        self.mel_radio = QtWidgets.QRadioButton('MEL')

        self.languages_btn = QtWidgets.QButtonGroup()
        self.languages_btn.addButton(self.python_radio)
        self.languages_btn.addButton(self.mel_radio)

        self.scripts_exec_python, self.scripts_edit_python = self.get_script_editor(python=True)
        self.scripts_exec_mel, self.scripts_edit_mel = self.get_script_editor()

        self.execute_btn = QtWidgets.QPushButton('Execute')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/execute.png'))
        self.execute_btn.setIcon(icon)

        self.menu_tree_base = QtWidgets.QWidget()
        self.options_base = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter(self)

        self.save_btn = QtWidgets.QPushButton('Save')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.main_ly.setContentsMargins(0, 0, 0, 0)
        self.menu_ly = QtWidgets.QVBoxLayout()

        self.menu_filter_ly = QtWidgets.QHBoxLayout()
        self.menu_filter_ly.addWidget(self.menu_filter)
        self.menu_filter_ly.addWidget(self.add_menu_btn)
        self.menu_filter_ly.addWidget(self.delete_menu_btn)

        self.options_ly = QtWidgets.QVBoxLayout()
        self.options_ly.setAlignment(QtCore.Qt.AlignTop)

        self.label_divider_ly = QtWidgets.QHBoxLayout()

        self.label_ly = QtWidgets.QFormLayout()
        self.label_ly.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.label_ly.addRow('Label:', self.label)

        self.label_divider_ly.addLayout(self.label_ly)
        self.label_divider_ly.addWidget(self.divider)

        self.languages_ly = QtWidgets.QHBoxLayout()
        self.languages_ly.setSpacing(50)
        self.languages_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.languages_ly.addWidget(self.mel_radio)
        self.languages_ly.addWidget(self.python_radio)

        self.scripts_ly = QtWidgets.QVBoxLayout()
        self.scripts_ly.addLayout(self.languages_ly)

        self.scripts_edit_mel_ly = QtWidgets.QHBoxLayout()
        self.scripts_edit_mel_ly.setContentsMargins(0, 0, 0, 0)
        self.scripts_edit_mel_ly.addWidget(self.scripts_edit_mel)

        self.mel_script = QtWidgets.QWidget()
        self.mel_script.setLayout(self.scripts_edit_mel_ly)

        self.mel_script.hide()

        self.scripts_edit_python_ly = QtWidgets.QHBoxLayout()
        self.scripts_edit_python_ly.setContentsMargins(0, 0, 0, 0)
        self.scripts_edit_python_ly.addWidget(self.scripts_edit_python)

        self.python_script = QtWidgets.QWidget()
        self.python_script.setLayout(self.scripts_edit_python_ly)

        self.scripts_ly.addWidget(self.python_script)
        self.scripts_ly.addWidget(self.mel_script)

        self.scripts_btn_ly = QtWidgets.QHBoxLayout()
        self.scripts_btn_ly.addWidget(self.execute_btn)

        self.scripts_ly.addLayout(self.scripts_btn_ly)

        self.scripts_tab = QtWidgets.QGroupBox('Command')
        self.scripts_tab.setAlignment(QtCore.Qt.AlignCenter)
        self.scripts_tab.setLayout(self.scripts_ly)

        self.options_ly.addLayout(self.label_divider_ly)
        self.options_ly.addWidget(self.scripts_tab)

        self.main_button_ly = QtWidgets.QHBoxLayout()
        self.main_button_ly.setContentsMargins(10, 0, 10, 10)
        self.main_button_ly.addWidget(self.save_btn)
        self.main_button_ly.addWidget(self.cancel_btn)

        # splitter

        self.add_btn_ly = QtWidgets.QHBoxLayout()
        self.add_btn_ly.addWidget(self.add_item_btn)
        self.add_btn_ly.addWidget(self.add_submenu_btn)
        self.add_btn_ly.addWidget(self.delete_btn)

        self.menu_ly.addLayout(self.menu_filter_ly)
        self.menu_ly.addLayout(self.add_btn_ly)
        self.menu_ly.addWidget(self.menu_tree)
        self.menu_tree_base.setLayout(self.menu_ly)
        self.options_base.setLayout(self.options_ly)

        self.splitter.addWidget(self.menu_tree_base)
        self.splitter.addWidget(self.options_base)
        self.main_ly.addWidget(self.splitter)
        self.main_ly.addLayout(self.main_button_ly)

    def make_connections(self):
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_submenu_btn.clicked.connect(self.add_submenu)
        self.menu_tree.itemSelectionChanged.connect(self.select_item)
        self.languages_btn.buttonClicked.connect(self.change_language)
        self.execute_btn.clicked.connect(self.execute)

    def get_current_languages(self):
        if self.mel_radio.isChecked():
            return 'MEL'
        elif self.python_radio.isChecked():
            return 'Python'

    def execute(self):
        lang = self.get_current_languages()
        if lang == 'MEL':
            self.scripts_exec_mel.executeAll()
        elif lang == 'Python':
            self.scripts_exec_python.executeAll()

    def change_language(self):
        lang = self.get_current_languages()
        if lang == 'MEL':
            self.python_script.hide()
            self.mel_script.show()
            self.scripts_exec_mel.getSourceType()

        elif lang == 'Python':
            self.mel_script.hide()
            self.python_script.show()
            self.scripts_exec_python.getSourceType()

    def enabled_widgets(self, state):
        widgets = [self.python_radio, self.mel_radio, self.execute_btn, self.scripts_tab]
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
