# -*- coding: UTF-8 -*-
import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import MayaTools.core.ui.utils_qt as utils_qt
import maya.OpenMayaUI as omui
import shiboken2 as shiboken

import importlib

importlib.reload(utils_qt)

"""
import importlib
import MayaTools.tools.pipeline.menu_creator.menu_ui as ui
importlib.reload(ui)

menu = ui.MenuEditor()
menu.showUI()
"""


class CustomTreeItem(QtWidgets.QTreeWidgetItem):
    CONFIG = dict(
        label='Item',
        type='item',
        divider=False,
        option_box=False,
        language_command='Mel',
        language_option_box='Mel',
        text_command_python='',
        text_option_box_python='',
        text_command_mel='',
        text_option_box_mel=''
    )

    SUBMENU_FLAGS = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    COMMON_FLAGS = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled

    SUBMENU_COLOR = QtGui.QColor(255, 0, 0)
    ITEM_COLOR = QtGui.QColor(0, 255, 0)
    DIVIDER_COLOR = QtGui.QColor(224, 224, 224)
    ITEM_SIZE = 13

    def __init__(self, parent):
        super(CustomTreeItem, self).__init__(parent)
        self.set_config(config=self.CONFIG)
        self.setExpanded(True)
        font = QtGui.QFont()
        font.setPixelSize(self.ITEM_SIZE)
        self.setFont(0, font)

    def set_config(self, config):
        self.setData(0, QtCore.Qt.UserRole, config)
        self.set_label(config['label'])
        self.set_type(config['type'])
        self.set_divider(config['divider'])
        self.set_option_box(config['option_box'])

    def set_label(self, label):
        config = self.data(0, QtCore.Qt.UserRole)
        config['label'] = label
        self.setText(0, label)
        self.setData(0, QtCore.Qt.UserRole, config)

    def set_text(self, text, option_box=False):
        config = self.data(0, QtCore.Qt.UserRole)

        if option_box:
            if config['language_command'] == 'Mel':
                config['text_option_box_mel'] = text
            else:
                config['text_option_box_mel'] = text
        else:
            config['text_command'] = text

        self.setData(0, QtCore.Qt.UserRole, config)

    def set_type(self, type='item'):
        config = self.data(0, QtCore.Qt.UserRole)
        config['type'] = type
        self.setData(0, QtCore.Qt.UserRole, config)
        if type == 'item':
            self.setTextColor(0, self.ITEM_COLOR)
            self.setFlags(self.COMMON_FLAGS)
        if type == 'submenu':
            self.setTextColor(0, self.SUBMENU_COLOR)
            self.setFlags(self.SUBMENU_FLAGS)

    def set_divider(self, state=False):
        config = self.data(0, QtCore.Qt.UserRole)
        config['divider'] = state
        self.setData(0, QtCore.Qt.UserRole, config)
        if state:
            self.setTextColor(0, self.DIVIDER_COLOR)
            self.setFlags(self.COMMON_FLAGS)
        else:
            type_item = config['type']
            self.set_type(type=type_item)

    def set_option_box(self, state=False):
        config = self.data(0, QtCore.Qt.UserRole)
        config['option_box'] = state
        self.setData(0, QtCore.Qt.UserRole, config)


class TreeWidgetItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        super(TreeWidgetItemDelegate, self).paint(painter, option, index)
        config = index.data(QtCore.Qt.UserRole)

        option.state &= ~QtWidgets.QStyle.State_HasFocus  # never draw focus rect

        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        tree_widget = index.model().parent()
        main_rect = tree_widget.rect()
        self.item = tree_widget.itemFromIndex(index)
        level = self.check_parent_levels(index)
        label = QtWidgets.QLabel(index.data(QtCore.Qt.DisplayRole))
        length = label.fontMetrics().boundingRect(label.text()).width()
        rect = QtCore.QRect(option.rect)
        pos_y = rect.y() + self.item.ITEM_SIZE / 2
        indent = 25 + (20 * level)
        if config['divider']:
            pen = QtGui.QPen(self.item.DIVIDER_COLOR)
            painter.setPen(pen)
            painter.drawLine(length + indent, pos_y, main_rect.width() - 10, pos_y)

        if config['option_box'] and not config['divider']:
            pen = QtGui.QPen(self.item.DIVIDER_COLOR)
            painter.setPen(pen)
            painter.drawRect((length + indent) + 5, self.item.ITEM_SIZE / 3 + rect.y(), 10, 10)

    def check_parent_levels(self, model_index, level=0):
        parent = model_index.parent()
        if parent.data(0):
            new_level = level + 1
            return self.check_parent_levels(parent, level=new_level)
        return level

    def initStyleOption(self, option, index):
        config = index.data(QtCore.Qt.UserRole)
        if config['divider']:
            option.rect.adjust(-10, 0, 0, 0)
        QtWidgets.QStyledItemDelegate.initStyleOption(self, option, index)

    def sizeHint(self, option, index):
        config = index.data(QtCore.Qt.UserRole)
        if config['divider']:
            return QtCore.QSize(0, self.item.ITEM_SIZE)
        return QtWidgets.QStyledItemDelegate.sizeHint(self, option, index)


class CustomTabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s


class CustomTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super(CustomTabWidget, self).__init__(parent)

        self.setStyleSheet("""
        QTabWidget::tab-bar {
             color: #45a15d;
             min-width: 999999px;
             top: 0.1em;
             
             }
        QTabBar:tab:!selected {
            padding: 5px;
        }
        QTabBaq:tab:selected { 
            padding: 5px;
        }
        """)


def get_maya_main_window():
    """

    Get the main Maya window as a QtGui.QMainWindow instance

    :return: QtGui.QMainWindow instance of the top level Maya windows

    """
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(int(ptr), QtWidgets.QWidget)


class MenuEditor(QtWidgets.QDialog):
    # MAYA = pm.ui.PyUI('MayaWindow').asQtObject()
    MAYA = get_maya_main_window()
    PATH = r'E:\Work\Pipeline\MayaTools\tools\menu_creator\menu'

    @staticmethod
    def showUI():
        try:
            ui.close()
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = MenuEditor()
        ui.show()

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

        print('__init__')
        self.enabled_widgets(False)

    def create_widgets(self):
        # menu filter
        self.menu_combo = QtWidgets.QComboBox()
        self.menu_combo.addItem('Menu Name 1')
        self.menu_combo.addItem('Menu Name 1')
        self.menu_combo.SelectedIndex = -1
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
        self.menu_tree.setColumnCount(1)
        self.menu_tree.setItemDelegate(TreeWidgetItemDelegate(self))
        self.menu_tree.setIconSize(QtCore.QSize(1, 1))
        self.menu_tree.setFocusPolicy(QtCore.Qt.NoFocus)
        self.menu_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.menu_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.menu_tree.setHeaderHidden(True)

        # menu tree buttons
        self.add_item_btn = QtWidgets.QPushButton('Item')
        self.add_submenu_btn = QtWidgets.QPushButton('Submenu')
        self.add_divider_btn = QtWidgets.QPushButton('Divider')
        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setFixedSize(23, 23)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/UVTBRemove.png'))
        self.delete_btn.setIcon(icon)

        # line edit for label item
        self.label_editor = QtWidgets.QLineEdit()

        # check box divider
        self.divider_cb = QtWidgets.QCheckBox('Divider')

        # menu and options widget
        self.menu_tree_widget = QtWidgets.QWidget()
        self.options_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter(self)

        # save and cancel button
        self.save_btn = QtWidgets.QPushButton('Save')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

        self.command_editor = ScriptEditor(python=True)
        self.option_box_editor = ScriptEditor(python=True)

        self.option_box_cb = QtWidgets.QCheckBox()
        self.scripts_group_box = CustomTabWidget(self)

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
        self.menu_buttons_ly.addWidget(self.add_divider_btn)
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
        self.label_ly.addRow('Label:', self.label_editor)
        self.label_divider_ly.addLayout(self.label_ly)
        self.label_divider_ly.addWidget(self.divider_cb)

        self.scripts_group_box.addTab(self.command_editor, 'Command')
        self.scripts_group_box.addTab(self.option_box_editor, 'Option Box')
        tab_bar = self.scripts_group_box.tabBar()
        tab_bar.setExpanding(True)
        tab_bar.setTabEnabled(1, False)
        tab_bar.setTabButton(1, QtWidgets.QTabBar.LeftSide, self.option_box_cb)

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
        self.add_divider_btn.clicked.connect(self.add_divider)
        self.menu_tree.itemSelectionChanged.connect(self.select_item)
        self.menu_tree.itemChanged.connect(self.item_change)
        self.delete_btn.clicked.connect(self.delete_item)
        self.save_btn.clicked.connect(self.save)
        self.divider_cb.stateChanged.connect(self.set_divider)
        self.option_box_cb.stateChanged.connect(self.set_option_box)
        self.label_editor.textChanged.connect(self.label_change)
        self.command_editor.changeText.connect(self.command_change)
        self.option_box_editor.changeText.connect(lambda x=None: self.command_change(self.option_box_editor.python))

    """  BUTTON CONNECTIONS """

    def command_change(self, python=True):
        item = self.get_selected_item()
        if not item:
            return

        option_box = self.option_box_cb.isChecked()
        select_tab = self.scripts_group_box.currentIndex()

        # check if active option box
        option_state = False
        if option_box and select_tab:
            option_state = True

        text = self.command_editor.get_text(python=python)
        print(text)


        item.set_text(text, option_box=option_state)

    def add_item(self):
        item = CustomTreeItem(self.menu_tree)
        item.set_label('Item')
        item.set_type('item')
        self.menu_tree.addTopLevelItem(item)

    def add_submenu(self):
        item = CustomTreeItem(self.menu_tree)
        item.set_label('Submenu')
        item.set_type('submenu')
        self.menu_tree.addTopLevelItem(item)

    def add_divider(self):
        item = CustomTreeItem(self.menu_tree)
        item.set_label('Divider')
        item.set_type('item')
        item.set_divider(True)
        self.menu_tree.addTopLevelItem(item)

    def select_item(self, *args):
        item = self.get_selected_item()
        if not item:
            self.divider_cb.setCheckState(QtCore.Qt.Unchecked)
            self.label_editor.setText('')
            self.enabled_widgets(False)
            return

        config = item.data(0, QtCore.Qt.UserRole)

        # update divider
        if config['divider']:
            self.divider_cb.setCheckState(QtCore.Qt.Checked)
        else:
            self.divider_cb.setCheckState(QtCore.Qt.Unchecked)

        # update text
        self.label_editor.setText(config['label'])

        # enable all widgets
        self.enabled_widgets(True)

        # set text in editor
        language_command = True if config['language_command'] == 'python' else False
        text_command = config['text_command']

        self.command_editor.set_text(text=text_command, python=language_command)
        if self.option_box_cb.isChecked():
            language_option_box = True if config['language_option_box'] == 'python' else False
            text_option_box = config['text_option_box']
            self.option_box_editor.set_text(text=text_option_box, python=language_option_box)

        # enable divider checkBox
        self.divider_cb.setEnabled(True)
        if item.childCount():
            self.divider_cb.setCheckState(QtCore.Qt.Unchecked)
            self.divider_cb.setEnabled(False)

        self.option_box_cb.setEnabled(True)
        if config['type'] == 'submenu':
            self.option_box_cb.setEnabled(False)

        # enable option box
        if config['option_box']:
            self.option_box_cb.setCheckState(QtCore.Qt.Checked)
        else:
            self.option_box_cb.setCheckState(QtCore.Qt.Unchecked)

    def item_change(self):
        item = self.get_selected_item()
        if not item:
            return

        self.label_editor.setText(item.text(0))

    def delete_item(self):
        selected = self.menu_tree.selectedItems()
        if not selected:
            return

        for item in selected:
            parent = item.parent() or self.menu_tree.invisibleRootItem()
            parent.takeChild(self.menu_tree.indexFromItem(item).row())

    def save(self):
        print('SAVE')
        print(self.command_editor.get_text(python=True))
        print(self.command_editor.get_text())

    def set_divider(self):
        """ Apply divider property for selected item"""
        item = self.get_selected_item()
        if not item:
            return

        state = self.divider_cb.isChecked()
        if not state:
            state = False

        item.set_divider(state)

    def set_option_box(self):
        """ Apply option box for selected item """
        item = self.get_selected_item()
        if not item:
            return

        state = self.option_box_cb.isChecked()
        if not state:
            state = False

        self.scripts_group_box.setTabEnabled(1, state)
        item.set_option_box(state=state)

    def label_change(self, text):
        item = self.get_selected_item()

        if not item:
            return

        if text == item.data(0, QtCore.Qt.UserRole)['label']:
            return

        item.set_label(label=text)

    """  FUNCTIONAL  """

    def get_selected_item(self):
        selected = self.menu_tree.selectedItems()
        if not len(selected) == 1:
            return
        return selected[0]

    def enabled_widgets(self, state):
        widgets = [self.command_editor.python_radio, self.command_editor.mel_radio,
                   self.command_editor.execute_btn, self.scripts_group_box, self.label_editor, self.divider_cb]
        for w in widgets:
            w.setEnabled(state)


class ScriptEditor(QtWidgets.QWidget):
    changeText = QtCore.Signal()

    def get_script_editor(self, python=False):
        pm.window()
        pm.columnLayout()
        executer = pm.cmdScrollFieldExecuter(fkp=self.emit_signal)
        if python:
            executer = pm.cmdScrollFieldExecuter(sourceType="python", commandCompletion=False, showTooltipHelp=False,
                                                 fkp=self.emit_signal)

        qt_obj = utils_qt.convert_pymel_to_qt(executer, type_obj='QTextEdit')

        return executer, qt_obj

    def __init__(self, parent=None, python=True):
        super(ScriptEditor, self).__init__(parent)
        self.python = python

        self.build()
        self.make_connections()

        if python:
            self.python_radio.setChecked(True)
            self.mel_widget.hide()
        else:
            self.mel_radio.setChecked(True)
            self.python_widget.hide()

    def emit_signal(self, *args):
        self.changeText.emit()

    def build(self):
        self.python_radio = QtWidgets.QRadioButton('Python')
        self.mel_radio = QtWidgets.QRadioButton('MEL')
        self.languages_btn = QtWidgets.QButtonGroup()
        self.languages_btn.addButton(self.python_radio)
        self.languages_btn.addButton(self.mel_radio)

        self.exec_python, self.edit_python = self.get_script_editor(python=True)
        self.exec_mel, self.edit_mel = self.get_script_editor(python=False)

        self.python_widget = QtWidgets.QWidget()
        self.mel_widget = QtWidgets.QWidget()

        self.languages_ly = QtWidgets.QHBoxLayout()
        self.languages_ly.setSpacing(50)
        self.languages_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.languages_ly.addWidget(self.mel_radio)
        self.languages_ly.addWidget(self.python_radio)

        self.edit_mel_ly = QtWidgets.QHBoxLayout()
        self.edit_mel_ly.setContentsMargins(0, 0, 0, 0)
        self.edit_mel_ly.addWidget(self.edit_mel)
        self.mel_widget.setLayout(self.edit_mel_ly)
        self.edit_mel = self.mel_widget.children()[1]

        self.edit_python_ly = QtWidgets.QHBoxLayout()
        self.edit_python_ly.setContentsMargins(0, 0, 0, 0)
        self.edit_python_ly.addWidget(self.edit_python)
        self.python_widget.setLayout(self.edit_python_ly)
        self.edit_python = self.python_widget.children()[1]

        self.execute_btn = QtWidgets.QPushButton('Execute')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/execute.png'))
        self.execute_btn.setIcon(icon)

        self.main_ly = QtWidgets.QVBoxLayout()
        self.main_ly.setContentsMargins(0, 0, 0, 0)
        self.main_ly.addLayout(self.languages_ly)
        self.main_ly.addWidget(self.python_widget)
        self.main_ly.addWidget(self.mel_widget)
        self.main_ly.addWidget(self.execute_btn)

        self.setLayout(self.main_ly)

    def make_connections(self):
        t = QtWidgets.QWidget()

        self.languages_btn.buttonClicked.connect(self.change_language)
        self.execute_btn.clicked.connect(self.execute)
        self.edit_python.textChanged.connect(self.emit_signal)

    def change_language(self):
        lang = self.get_current_languages()
        if lang == 'Mel':
            self.python = False
            self.python_widget.hide()
            self.mel_widget.show()
        elif lang == 'Python':
            self.python = True
            self.mel_widget.hide()
            self.python_widget.show()

    def get_current_languages(self):
        if self.mel_radio.isChecked():
            return 'Mel'
        elif self.python_radio.isChecked():
            return 'Python'

    def execute(self):
        lang = self.get_current_languages()
        if lang == 'Mel':
            self.exec_mel.executeAll()
        elif lang == 'Python':
            self.exec_python.executeAll()

    def set_text(self, text, python=False):
        if python:

            return self.exec_python.setText(text)
        else:
            return self.exec_mel.setText(text)

    def get_text(self, python=False):
        if python:
            return self.edit_python.toPlainText()
        else:
            return self.edit_mel.toPlainText()

