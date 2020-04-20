import pymel.core as pm
import maya.OpenMaya as om


class Aligner(object):
    @staticmethod
    def get_matrix(obj):
        return pm.xform(obj, ws=True, q=True, m=True)

    @staticmethod
    def matrix_to_list(in_matrix):
        matrix = []

        for i in in_matrix:
            for axis in i:
                matrix.append(axis)

        return matrix

    @staticmethod
    def scale_func(obj, flag, volume=[1, 1, 1]):
        scale_double_array = om.MScriptUtil()
        scale_double_array.createFromList([1.0, 1.0, 1.0], 3)
        scale_double_array_Ptr = scale_double_array.asDoublePtr()
        matrix = om.MTransformationMatrix(obj)

        if flag == 'get':
            matrix.getScale(scale_double_array_Ptr, om.MSpace.kWorld)
            x_scale = om.MScriptUtil().getDoubleArrayItem(scale_double_array_Ptr, 0)
            y_scale = om.MScriptUtil().getDoubleArrayItem(scale_double_array_Ptr, 1)
            z_scale = om.MScriptUtil().getDoubleArrayItem(scale_double_array_Ptr, 2)
            scale_list = om.MVector(x_scale, y_scale, z_scale)
            return scale_list

        if flag == 'set':
            scale_double_array.createFromList(volume, 3)
            scale_double_array_Ptr = scale_double_array.asDoublePtr()
            matrix.setScale(scale_double_array_Ptr, om.MSpace.kObject)
            return matrix

    def __init__(self, rotate_checkbox, scale_checkbox, x_axis_checkbox, y_axis_checkbox, z_axis_checkbox):
        self.rotate_checkbox = rotate_checkbox
        self.scale_checkbox = scale_checkbox
        self.x_axis_checkbox = x_axis_checkbox
        self.y_axis_checkbox = y_axis_checkbox
        self.z_axis_checkbox = z_axis_checkbox

        self.align()

    def align(self):

        # get selection
        selected = pm.selected()

        if not selected:
            om.MGlobal.displayError('Nothing is currently selected')
            return

        plane = selected.pop()

        # get plane matrix
        mUtil = om.MScriptUtil()
        mat0 = self.get_matrix(plane)
        m0 = om.MMatrix()
        mUtil.createMatrixFromList(mat0, m0)

        # get obj matrix and aligning
        for s in selected:

            # get objects world matrix
            mat1 = self.get_matrix(s)
            m1 = om.MMatrix()
            m2 = om.MMatrix()
            m3 = om.MMatrix()
            m4 = om.MMatrix()

            mUtil.createMatrixFromList(mat1, m1)

            # get objects local matrix
            om.MMatrix.setToProduct(m2, m1, m0.inverse())

            # set object matrix
            tm = om.MTransformationMatrix(m2)
            tv = tm.getTranslation(om.MSpace.kWorld)
            if self.x_axis_checkbox:
                tv.x = 0
            if self.y_axis_checkbox:
                tv.y = 0
            if self.z_axis_checkbox:
                tv.z = 0
            if not self.x_axis_checkbox and not self.y_axis_checkbox and not self.z_axis_checkbox:
                om.MGlobal.displayError('Select at least one axis')
                return
            tm.setTranslation(tv, om.MSpace.kWorld)

            if self.rotate_checkbox:
                rotate_double_array = om.MScriptUtil()
                rotate_double_array.createFromList([0.0, 0.0, 0.0], 3)
                rotate_double_array_Ptr = rotate_double_array.asDoublePtr()
                tm.setRotation(rotate_double_array_Ptr, om.MSpace.kObject)

            if self.scale_checkbox:
                # get plane  scale
                sv = self.scale_func(m1, 'get')

                # set objects scale
                tm = self.scale_func(tm, 'set', [sv.x, sv.y, sv.z])

            # get edited world matrix
            tm_list = self.matrix_to_list(tm)
            mUtil.createMatrixFromList(tm_list, m3)
            om.MMatrix.setToProduct(m4, m3, m0)
            if not self.scale_checkbox:
                m4 = self.scale_func(m4, 'set', [1.0, 1.0, 1.0])

            result_matrix = self.matrix_to_list(m4)

            # set object to wright place
            pm.xform(s, ws=True, m=tuple(result_matrix))
            pm.xform(s, sh=(0.0, 0.0, 0.0))
