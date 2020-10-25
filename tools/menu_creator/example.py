# -*- coding: utf-8 -*-
"""
Author: Administrator
Date: 2020/5/10 14:05
"""
from PySide2 import QtCore, QtGui, QtWidgets
from functools import partial
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class SimpleOutliner(QtWidgets.QDialog):
    WINDOW_TITLE = "Simple Outliner"

    dlg_instance = None

    def __init__(self, parent=maya_main_window()):
        super(SimpleOutliner, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.scriptJob_num = -1

        self.create_action()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context)

    def create_action(self):
        self.about_action = QtWidgets.QAction("About", self)
        self.display_action = QtWidgets.QAction("Shapes", self)
        self.display_action.setCheckable(True)
        self.display_action.setChecked(True)
        self.display_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+H"))

    def create_widgets(self):
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.menu = QtWidgets.QMenuBar()
        display_menu = self.menu.addMenu("Display")
        help_menu = self.menu.addMenu("Help")

        display_menu.addAction(self.display_action)
        help_menu.addAction(self.about_action)

        self.refresh_bttn = QtWidgets.QPushButton("Refresh")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_bttn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.tree_widget)
        main_layout.setMenuBar(self.menu)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.tree_widget.itemCollapsed.connect(self.update_icon)
        self.tree_widget.itemExpanded.connect(self.update_icon)
        self.tree_widget.itemSelectionChanged.connect(self.select_items)

        self.about_action.triggered.connect(self.about)
        self.display_action.toggled.connect(self.set_shape_visible)
        self.refresh_bttn.clicked.connect(self.refresh_tree_widget)

    def showEvent(self, event):
        super(SimpleOutliner, self).showEvent(event)
        self.refresh_tree_widget()
        self.update_selection()
        self.set_scriptJob_enabled(True)

    def closeEvent(self, event):
        if isinstance(self, SimpleOutliner):
            super(SimpleOutliner, self).closeEvent(event)
            self.set_scriptJob_enabled(False)

    def refresh_tree_widget(self):
        self.shape_nodes = cmds.ls(shapes=True)

        self.tree_widget.clear()

        nodes = cmds.ls(assemblies=True)
        for node in nodes:
            item = self.create_item(node)
            self.tree_widget.addTopLevelItem(item)

    def create_item(self, text):
        item = QtWidgets.QTreeWidgetItem([text])
        self.add_children(item)
        self.update_icon(item)

        is_shape = text in self.shape_nodes
        item.setData(0, QtCore.Qt.UserRole, is_shape)

        return item

    def add_children(self, item):
        children = cmds.listRelatives(item.text(0), children=True)
        if children:
            for i in children:
                child = self.create_item(i)
                item.addChild(child)

    def update_icon(self, item):
        object_type = ""
        if item.isExpanded():
            object_type = "transform"
        else:
            child_count = item.childCount()
            if child_count == 0:
                object_type = cmds.objectType(item.text(0))
            elif child_count == 1:
                child_item = item.child(0)
                object_type = cmds.objectType(child_item.text(0))
            else:
                object_type = "transform"

        if object_type == "transform":
            icon = QtGui.QIcon(":transform.svg")
        elif object_type == "camera":
            icon = QtGui.QIcon(":camera.svg")
        elif object_type == "mesh":
            icon = QtGui.QIcon(":mesh.svg")
        else:
            icon = QtGui.QIcon(":transform.svg")

        item.setIcon(0, icon)

    def select_items(self):
        items = self.tree_widget.selectedItems()
        name = []
        for item in items:
            name.append(item.text(0))

        cmds.select(name, replace=True)

    def about(self):
        QtWidgets.QMessageBox.about(self, "About Simple Outliner", "Add About Text Here")

    def set_shape_visible(self, visible):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()

            is_shape = item.data(0, QtCore.Qt.UserRole)
            if is_shape:
                item.setHidden(not visible)
            iterator += 1

    def show_context(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.display_action)
        context_menu.addSeparator()
        context_menu.addAction(self.about_action)

        context_menu.exec_(self.mapToGlobal(point))

    def update_selection(self):
        selection = cmds.ls(selection=True)
        iteration = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        while iteration.value():
            item = iteration.value()
            is_selected = item.text(0) in selection
            item.setSelected(is_selected)

            iteration += 1

    def set_scriptJob_enabled(self, boolean):
        if boolean and self.scriptJob_num < 0:
            self.scriptJob_num = cmds.scriptJob(event=["SelectionChanged", partial(self.update_selection)],
                                                protected=True)
        elif not boolean and self.scriptJob_num >= 0:
            cmds.scriptJob(kill=self.scriptJob_num, force=True)
            self.scriptJob_num = -1


def showWindow():
    try:
        dialog.set_scriptJob_enabled(False)
        dialog.close()
        dialog.deleteLater()
    except:
        pass
    dialog = SimpleOutliner()
    dialog.show()


if __name__ == "__main__":
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = SimpleOutliner()
    dialog.show()