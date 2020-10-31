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

    @staticmethod
    def showUI():
        try:
            ui.close()
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = MenuEditor()
        ui.show()

    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    PATH = r'E:\Work\Pipeline\MayaTools\tools\menu_creator\menu'

    ITEM_DATA = dict(
        label='Item',
        type='item',
        language='Mel',
        text='',
        divider=False
    )

    CONFIG = dict(
        submenu=dict(
            label='Submenu',
            size=14,
            color=QtGui.QColor(255, 0, 0),
            flags=QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                  QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        ),
        item=dict(
            label='Item',
            size=14,
            color=QtGui.QColor(0, 255, 0),
            flags=QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                  QtCore.Qt.ItemIsDragEnabled,
        ),
        divider=dict(
            label='----------',
            size=12,
            color=QtGui.QColor(200, 200, 200),
            flags=QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                  QtCore.Qt.ItemIsDragEnabled
        )

    )

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

        self.menu_data = {}

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
        self.delete_btn.clicked.connect(self.delete_item)
        self.save_btn.clicked.connect(self.save)
        self.divider.stateChanged.connect(self.divider_item)

    """  BUTTON CONNECTIONS """

    def add_item(self):
        config = self.CONFIG['item']
        item = QtWidgets.QTreeWidgetItem([config['label']])
        item.setFlags(config['flags'])
        font = QtGui.QFont()
        font.setPixelSize(config['size'])
        item.setFont(0, font)
        item.setTextColor(0, config['color'])

        self.ITEM_DATA['label'] = 'Item'
        self.ITEM_DATA['type'] = 'item'

        item.setData(0, QtCore.Qt.UserRole, self.ITEM_DATA)
        self.menu_tree.addTopLevelItem(item)

    def add_submenu(self):
        config = self.CONFIG['submenu']
        item = QtWidgets.QTreeWidgetItem([config['label']])
        item.setFlags(config['flags'])
        font = QtGui.QFont()
        font.setPixelSize(config['size'])
        item.setFont(0, font)
        item.setTextColor(0, config['color'])

        self.ITEM_DATA['label'] = 'Submenu'
        self.ITEM_DATA['type'] = 'submenu'

        item.setData(0, QtCore.Qt.UserRole, self.ITEM_DATA)
        self.menu_tree.addTopLevelItem(item)

    def select_item(self, *args):
        item = self.get_selected()
        if not item:
            self.divider.setCheckState(QtCore.Qt.Unchecked)
            self.label.setText('')
            self.enabled_widgets(False)
            return

        data = item.data(0, QtCore.Qt.UserRole)

        # update divider
        if data['divider']:
            self.divider.setCheckState(QtCore.Qt.Checked)
        else:
            self.divider.setCheckState(QtCore.Qt.Unchecked)

        # update text
        self.label.setText(data['label'])

        # enable all widgets
        self.enabled_widgets(True)

        # enable divider checkBox
        self.divider.setEnabled(True)
        if item.childCount():
            self.divider.setCheckState(QtCore.Qt.Unchecked)
            self.divider.setEnabled(False)

    def change_language(self):
        lang = self.get_current_languages()
        if lang == 'Mel':
            self.python_script.hide()
            self.mel_script.show()
            self.scripts_exec_mel.getSourceType()

        elif lang == 'Python':
            self.mel_script.hide()
            self.python_script.show()
            self.scripts_exec_python.getSourceType()

    def execute(self):
        lang = self.get_current_languages()
        if lang == 'Mel':
            self.scripts_exec_mel.executeAll()
        elif lang == 'Python':
            self.scripts_exec_python.executeAll()

    def delete_item(self):
        selected = self.menu_tree.selectedItems()
        if not selected:
            return

        for item in selected:
            parent = item.parent() or self.menu_tree.invisibleRootItem()
            parent.takeChild(self.menu_tree.indexFromItem(item).row())

    def save(self):
        print 'SAVE'

    def divider_item(self):
        state = self.divider.isChecked()
        item = self.get_selected()
        data = item.data(0, QtCore.Qt.UserRole)
        if state == data['divider']:
            return

        if not state:
            self.cancel_divider(item)
            return

        self.apply_divider(item)

    """  FUNCTIONAL  """

    def apply_divider(self, item):
        data = item.data(0, QtCore.Qt.UserRole)
        data['divider'] = True
        item.setData(0, QtCore.Qt.UserRole, data)
        config = self.CONFIG['divider']
        item = self.get_selected()
        label = self.label.text()
        if not label:
            label = 'Divider'
        item.setTextColor(0, config['color'])
        font = QtGui.QFont()
        font.setPixelSize(config['size'])
        item.setFont(0, font)
        item.setText(0, '{}{}'.format(label, config['label']))

    def cancel_divider(self, item):
        data = item.data(0, QtCore.Qt.UserRole)
        data['divider'] = False
        item.setData(0, QtCore.Qt.UserRole, data)
        config = self.CONFIG[data['type']]
        item.setTextColor(0, config['color'])
        font = QtGui.QFont()
        font.setPixelSize(config['size'])
        item.setFont(0, font)
        item.setText(0, config['label'])

    def get_current_languages(self):
        if self.mel_radio.isChecked():
            return 'Mel'
        elif self.python_radio.isChecked():
            return 'Python'

    def get_selected(self):
        selected = self.menu_tree.selectedItems()
        if not len(selected) == 1:
            return
        return selected[0]

    def enabled_widgets(self, state):
        widgets = [self.python_radio, self.mel_radio, self.execute_btn, self.scripts_tab]
        for w in widgets:
            w.setEnabled(state)
