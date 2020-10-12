import maya.cmds as cmds
import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
import maya.api.OpenMaya as om2
import MayaTools.core.ui.axes as axes_ui
import MayaTools.core.ui.separator as separator
import MayaTools.tools.matrix_constraint.matrix as matrix

reload(matrix)
reload(axes_ui)


class MatrixUI(QtWidgets.QDialog):
    CHANNELS = ('x', 'y', 'z')
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    @staticmethod
    def get_selected():
        sel = cmds.ls(sl=True)
        if not sel:
            om2.MGlobal.displayError('Nothing selected')
            return

        if not len(sel) > 1:
            om2.MGlobal.displayError('There must be 2 selected objects')
            return

        return sel

    def __init__(self, label, parent=MAYA):
        super(MatrixUI, self).__init__(parent)

        self.setWindowTitle(label)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(300, 200)

    def build(self):
        self.create_buttons()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

        self.add_offset()
        self.add_parent()
        self.add_translate_axes()
        self.add_rotate_axes()
        self.add_scale_axes()

    def apply(self):
        self.offset = self.offset_cb.isChecked()
        selected = self.get_selected()
        if not selected:
            self.targets = None
            self.driven = None
            return

        self.targets = selected[:-1]
        self.driven = selected[-1]

    def add_offset(self):
        self.offset_cb = QtWidgets.QCheckBox()
        self.form_offset_ly.addRow(('Maintain Offset'), self.offset_cb)

    def add_parent(self):
        self.parent_cb = QtWidgets.QCheckBox()
        self.form_parent_ly.addRow(('Parent'), self.parent_cb)

    def add_translate_axes(self):
        self.translate = axes_ui.AxesCheckBox()
        self.form_axes_ly.addRow(('Translate'), self.translate)

    def add_rotate_axes(self):
        self.rotate = axes_ui.AxesCheckBox()
        self.form_axes_ly.addRow(('Rotate'), self.rotate)

    def add_scale_axes(self):
        self.scale = axes_ui.AxesCheckBox()
        self.form_axes_ly.addRow(('Scale'), self.scale)

    def create_buttons(self):
        self.apply_btn = QtWidgets.QPushButton('Apply')
        self.apply_btn.setMinimumSize(100, 30)
        self.close_btn = QtWidgets.QPushButton('Close')
        self.close_btn.setMinimumSize(100, 30)

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.base_ly = QtWidgets.QVBoxLayout()
        self.base_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.form_offset_base_ly = QtWidgets.QHBoxLayout()
        self.form_offset_ly = QtWidgets.QFormLayout()
        self.form_parent_ly = QtWidgets.QFormLayout()
        self.form_axes_ly = QtWidgets.QFormLayout()
        self.form_axes_ly.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.button_ly = QtWidgets.QHBoxLayout()

    def make_connections(self):
        self.close_btn.clicked.connect(self.close)
        self.apply_btn.clicked.connect(self.apply)

    def add_to_layout(self):
        self.form_offset_base_ly.addLayout(self.form_offset_ly)
        self.form_offset_base_ly.addLayout(self.form_parent_ly)
        self.base_ly.addLayout(self.form_offset_base_ly)
        self.base_ly.addWidget(separator.QHLine())
        self.base_ly.addLayout(self.form_axes_ly)
        self.main_ly.addLayout(self.base_ly)
        self.main_ly.addStretch()
        self.main_ly.addLayout(self.button_ly)
        self.button_ly.addWidget(self.apply_btn)
        self.button_ly.addWidget(self.close_btn)


class ParentMatrixUI(MatrixUI):
    WINDOW_INSTANCE = None
    LABEL = 'Parent MatrixConstraint'

    def __init__(self):
        super(ParentMatrixUI, self).__init__(self.LABEL)

    def add_parent(self):
        pass

    def add_scale_axes(self):
        pass

    def apply(self):
        super(ParentMatrixUI, self).apply()

        if not self.targets and not self.driven:
            return

        self.skipRotate = self.rotate.get_unchecked_axis()
        self.skipTranslate = self.translate.get_unchecked_axis()
        matrix.ParentMatrix(self.targets, self.driven, self.offset, self.skipTranslate, self.skipRotate)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = ParentMatrixUI()
            cls.WINDOW_INSTANCE.build()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()


class PointMatrixUI(MatrixUI):
    WINDOW_INSTANCE = None
    LABEL = 'Point MatrixConstraint'

    def __init__(self):
        super(PointMatrixUI, self).__init__(self.LABEL)

    def add_parent(self):
        pass

    def add_rotate_axes(self):
        pass

    def add_scale_axes(self):
        pass

    def apply(self):
        super(PointMatrixUI, self).apply()

        if not self.targets and not self.driven:
            return

        self.skipTranslate = self.translate.get_unchecked_axis()
        matrix.PointMatrix(self.targets, self.driven, self.offset, self.skipTranslate)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = PointMatrixUI()
            cls.WINDOW_INSTANCE.build()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()


class OrientMatrixUI(MatrixUI):
    WINDOW_INSTANCE = None
    LABEL = 'Orient MatrixConstraint'

    def __init__(self):
        super(OrientMatrixUI, self).__init__(self.LABEL)

    def add_parent(self):
        pass

    def add_translate_axes(self):
        pass

    def add_scale_axes(self):
        pass

    def apply(self):
        super(OrientMatrixUI, self).apply()

        if not self.targets and not self.driven:
            return

        self.skipRotate = self.rotate.get_unchecked_axis()
        matrix.OrientMatrix(self.targets, self.driven, self.offset, self.skipRotate)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = OrientMatrixUI()
            cls.WINDOW_INSTANCE.build()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()


class ScaleMatrixUI(MatrixUI):
    WINDOW_INSTANCE = None
    LABEL = 'Scale MatrixConstraint'

    def __init__(self):
        super(ScaleMatrixUI, self).__init__(self.LABEL)

    def add_parent(self):
        pass

    def add_translate_axes(self):
        pass

    def add_rotate_axes(self):
        pass

    def apply(self):
        super(ScaleMatrixUI, self).apply()

        if not self.targets and not self.driven:
            return

        self.skipScale = self.scale.get_unchecked_axis()
        matrix.ScaleMatrix(self.targets, self.driven, self.offset, self.skipScale)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = ScaleMatrixUI()
            cls.WINDOW_INSTANCE.build()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()
