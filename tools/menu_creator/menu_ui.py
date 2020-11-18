import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import MayaTools.core.ui.utils_qt as utils_qt



class ScriptEditor():
    def __init__(self):
        pass


    def execute(self):
        pass

    def set_text(self, python=False):
        pass

    def get_text(self, python=False):
        pass

    def set_state(self, python=False):
        pass

    def get_state(self, python=False):
        pass


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
        # menu filter
        self.menu_combo = QtWidgets.QComboBox()
        self.menu_combo.addItem('Menu Name 1')
        self.menu_combo.addItem('Menu Name 1')
        self.menu_combo.setEditable(True)
        self.menu_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # add menu button
        self.add_menu_btn = QtWidgets.QPushButton()
        self.add_menu_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(':/QR_add.png')
        icon.addPixmap(pixmap)
        self.add_menu_btn.setIcon(icon)

        # delete menu button
        self.delete_menu_btn = QtWidgets.QPushButton()
        self.delete_menu_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/QR_delete.png'))
        self.delete_menu_btn.setIcon(icon)

        # menu tree widget
        self.menu_tree = QtWidgets.QTreeWidget()
        self.menu_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.menu_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.menu_tree.setHeaderHidden(True)

        # menu tree buttons
        self.add_item_btn = QtWidgets.QPushButton('Item')
        self.add_submenu_btn = QtWidgets.QPushButton('Submenu')
        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/UVTBRemove.png'))
        self.delete_btn.setIcon(icon)

        # line edit for label item
        self.label = QtWidgets.QLineEdit()

        # check box divider
        self.divider = QtWidgets.QCheckBox('Divider')

        # languages radio button
        self.python_radio = QtWidgets.QRadioButton('Python')
        self.python_radio.setChecked(True)
        self.mel_radio = QtWidgets.QRadioButton('MEL')
        self.languages_btn = QtWidgets.QButtonGroup()
        self.languages_btn.addButton(self.python_radio)
        self.languages_btn.addButton(self.mel_radio)

        # create execute and edit widget for scripts editor
        self.exec_python, self.edit_python = self.get_script_editor(python=True)
        self.exec_mel, self.edit_mel = self.get_script_editor(python=False)

        self.python_widget = QtWidgets.QWidget()
        self.mel_widget = QtWidgets.QWidget()

        # execute button
        self.execute_btn = QtWidgets.QPushButton('Execute')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/execute.png'))
        self.execute_btn.setIcon(icon)

        # menu and options widget
        self.menu_tree_widget = QtWidgets.QWidget()
        self.options_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter(self)

        # save and cancel button
        self.save_btn = QtWidgets.QPushButton('Save')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.main_ly.setContentsMargins(0, 0, 0, 0)

        # menu main layout
        self.menu_ly = QtWidgets.QVBoxLayout()

        # menu combo box
        self.menu_combo_ly = QtWidgets.QHBoxLayout()
        self.menu_combo_ly.addWidget(self.menu_combo)
        self.menu_combo_ly.addWidget(self.add_menu_btn)
        self.menu_combo_ly.addWidget(self.delete_menu_btn)

        # menu buttons layout
        self.menu_buttons_ly = QtWidgets.QHBoxLayout()
        self.menu_buttons_ly.addWidget(self.add_item_btn)
        self.menu_buttons_ly.addWidget(self.add_submenu_btn)
        self.menu_buttons_ly.addWidget(self.delete_btn)

        # add to menu layout
        self.menu_ly.addLayout(self.menu_combo_ly)
        self.menu_ly.addLayout(self.menu_buttons_ly)
        self.menu_ly.addWidget(self.menu_tree)

        # options main layout
        self.options_ly = QtWidgets.QVBoxLayout()
        self.options_ly.setAlignment(QtCore.Qt.AlignTop)

        # label and divider layout
        self.label_divider_ly = QtWidgets.QHBoxLayout()

        # form layout for label and lineEdit widget
        self.label_ly = QtWidgets.QFormLayout()
        self.label_ly.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.label_ly.addRow('Label:', self.label)
        self.label_divider_ly.addLayout(self.label_ly)
        self.label_divider_ly.addWidget(self.divider)

        # languages layout for mel and python radio buttons
        self.languages_ly = QtWidgets.QHBoxLayout()
        self.languages_ly.setSpacing(50)
        self.languages_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.languages_ly.addWidget(self.mel_radio)
        self.languages_ly.addWidget(self.python_radio)

        # layout for edit MEL widget
        self.edit_mel_ly = QtWidgets.QHBoxLayout()
        self.edit_mel_ly.setContentsMargins(0, 0, 0, 0)
        self.edit_mel_ly.addWidget(self.edit_mel)
        self.mel_widget.setLayout(self.edit_mel_ly)

        # hide MEl widget
        self.mel_widget.hide()

        # layout for edit PYTHON widget
        self.edit_python_ly = QtWidgets.QHBoxLayout()
        self.edit_python_ly.setContentsMargins(0, 0, 0, 0)
        self.edit_python_ly.addWidget(self.edit_python)
        self.python_widget.setLayout(self.edit_python_ly)

        # layout for scripts editor and languages buttons
        self.scripts_ly = QtWidgets.QVBoxLayout()
        self.scripts_ly.addLayout(self.languages_ly)
        self.scripts_ly.addWidget(self.python_widget)
        self.scripts_ly.addWidget(self.mel_widget)
        self.scripts_ly.addWidget(self.execute_btn)

        # group box for scripts editor
        self.scripts_group_box = QtWidgets.QGroupBox('Command')
        self.scripts_group_box.setAlignment(QtCore.Qt.AlignCenter)
        self.scripts_group_box.setLayout(self.scripts_ly)

        # add label and sripts editor to options layout
        self.options_ly.addLayout(self.label_divider_ly)
        self.options_ly.addWidget(self.scripts_group_box)

        # main button layout
        self.main_button_ly = QtWidgets.QHBoxLayout()
        self.main_button_ly.setContentsMargins(10, 0, 10, 10)
        self.main_button_ly.addWidget(self.save_btn)
        self.main_button_ly.addWidget(self.cancel_btn)

        self.menu_tree_widget.setLayout(self.menu_ly)
        self.options_widget.setLayout(self.options_ly)

        # splitter
        self.splitter.addWidget(self.menu_tree_widget)
        self.splitter.addWidget(self.options_widget)
        self.main_ly.addWidget(self.splitter)

        # add main button to main layout
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
            self.python_widget.hide()
            self.mel_widget.show()
            self.exec_mel.getSourceType()

        elif lang == 'Python':
            self.mel_widget.hide()
            self.python_widget.show()
            self.exec_python.getSourceType()

    def execute(self):
        lang = self.get_current_languages()
        if lang == 'Mel':
            self.exec_mel.executeAll()
        elif lang == 'Python':
            self.exec_python.executeAll()

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
        widgets = [self.python_radio, self.mel_radio, self.execute_btn, self.scripts_group_box]
        for w in widgets:
            w.setEnabled(state)
