import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2
import MayaTools.core.attribute as attribute


class MultMatrixSystem(object):
    @staticmethod
    def calculate_offset_matrix(driver, driven):
        driver_inverseMatrix = pm.getAttr('{}.worldInverseMatrix'.format(driver))
        driven_worldMatrix = pm.getAttr('{}.worldMatrix'.format(driven))
        return driven_worldMatrix * driver_inverseMatrix

    @staticmethod
    def reset_rotate_matrix(matrix):
        m_matrix = om2.MMatrix(matrix)
        transform_matrix = om2.MTransformationMatrix(m_matrix)
        transform_matrix.setRotation(om2.MEulerRotation(0.0, 0.0, 0.0))
        new_matrix = transform_matrix.asMatrix()
        return pm.dt.Matrix(list(new_matrix))

    @staticmethod
    def reset_translate_matrix(matrix):
        m_matrix = om2.MMatrix(matrix)
        transform_matrix = om2.MTransformationMatrix(m_matrix)
        transform_matrix.setTranslation(om2.MVector(0.0, 0.0, 0.0), om2.MSpace.kWorld)
        new_matrix = transform_matrix.asMatrix()
        return pm.dt.Matrix(list(new_matrix))

    MATRIX_ATTR = 'worldMatrix'

    def __init__(self, target, driven, offset=True, parent=True, skipTranslate=False, skipRotate=False):
        self.target = target
        self.driven = driven
        self.offset = offset
        self.parent = parent
        self.skipTranslate = skipTranslate
        self.skipRotate = skipRotate

        self.multMatrix = None

        self.input_index = [0, 1, 2]
        if parent:
            self.input_index = [1, 2, 0]

        self.last_index = 3

    def create_system(self):
        self.create_multMatrix()
        self.connect_nodes()
        if self.offset:
            self.set_offset()


    def create_multMatrix(self):
        self.multMatrix = cmds.createNode('multMatrix', n='{}_multOffset'.format(self.target))

    def connect_nodes(self):
        cmds.connectAttr('{}.{}'.format(self.target, self.MATRIX_ATTR),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[0]))
        cmds.connectAttr('{}.parentInverseMatrix'.format(self.driven),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[1]))


    def set_offset(self):
        offset = self.calculate_offset_matrix(self.target, self.driven)
        if self.skipRotate:
            offset = self.reset_rotate_matrix(offset)
        if self.skipTranslate:
            offset = self.reset_translate_matrix(offset)

        pm.setAttr('{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[2]), offset)

    def add_matrix(self, matrix):
        index = self.last_index
        cmds.setAttr('{}.matrixIn[{}]'.format(self.multMatrix, index), matrix, type='matrix')
        self.last_index += 1



class MatrixConstraint(object):
    @staticmethod
    def get_jointOrient_matrix(joint):
        compose = cmds.createNode('composeMatrix')
        inverse_matrix = cmds.createNode('inverseMatrix')
        cmds.connectAttr('{}.jointOrient'.format(joint),
                         '{}.inputRotate'.format(compose))
        cmds.connectAttr('{}.outputMatrix'.format(compose),
                         '{}.inputMatrix'.format(inverse_matrix))
        matrix = cmds.getAttr('{}.outputMatrix'.format(inverse_matrix))
        cmds.delete(compose, inverse_matrix)
        return matrix

    CHANNELS = ['x', 'y', 'z']

    def __init__(self, targets, driven, offset=True, parent=True, skipTranslate=(), skipRotate=(), skipScale=()):
        self.targets = targets
        self.driven = driven
        self.offset = offset
        self.parent = parent

        self.skipTranslate = skipTranslate
        self.skipRotate = skipRotate
        self.skipScale = skipScale

        self.matrix_systems = []
        self.wtAddMatrix = None
        self.decomposeMatrix = None
        self.rotate_decomposeMatrix = None
        self.main_multMatrix = None

        self.blend_state = False

    def blend_matrix(self, matrix_system):
        self.wtAddMatrix = cmds.createNode('wtAddMatrix', n='{}_blendMatrix'.format(self.driven))

        param = 1 / float(len(matrix_system))
        for index, system in enumerate(matrix_system):
            if not attribute.has_attr(self.wtAddMatrix, system.target):
                cmds.addAttr(self.wtAddMatrix, ln=system.target, k=True)

            cmds.setAttr('{}.{}'.format(self.wtAddMatrix, system.target), param)
            cmds.connectAttr('{}.{}'.format(self.wtAddMatrix, system.target),
                             '{}.wtMatrix[{}].weightIn'.format(self.wtAddMatrix, index))
            cmds.connectAttr('{}.matrixSum'.format(system.multMatrix),
                             '{}.wtMatrix[{}].matrixIn'.format(self.wtAddMatrix, index))

        self.main_multMatrix = self.wtAddMatrix

    def connect_channel(self):
        rotate_driver = self.decomposeMatrix
        if self.rotate_decomposeMatrix:
            rotate_driver = self.rotate_decomposeMatrix

        for axis in self.CHANNELS:
            if axis not in self.skipTranslate:
                cmds.connectAttr('{}.outputTranslate{}'.format(self.decomposeMatrix, axis.upper()),
                                 '{}.t{}'.format(self.driven, axis), f=True)

            if axis not in self.skipScale:
                cmds.connectAttr('{}.outputScale{}'.format(self.decomposeMatrix, axis.upper()),
                                 '{}.s{}'.format(self.driven, axis), f=True)

            if axis not in self.skipRotate:
                cmds.connectAttr('{}.outputRotate{}'.format(rotate_driver, axis.upper()),
                                 '{}.r{}'.format(self.driven, axis), f=True)

    def joint_rotate_matrix(self):
        self.rotate_multMatrix = cmds.createNode('multMatrix', n='{}_rotate_multOffset'.format(self.driven))
        self.rotate_decomposeMatrix = cmds.createNode('decomposeMatrix', n='{}_rotate_decMatrix'.format(self.driven))

        matrix = self.get_jointOrient_matrix(self.driven)
        cmds.setAttr('{}.matrixIn[1]'.format(self.rotate_multMatrix), matrix, type='matrix')
        cmds.connectAttr('{}.matrixSum'.format(self.main_multMatrix),
                         '{}.matrixIn[0]'.format(self.rotate_multMatrix))
        cmds.connectAttr('{}.matrixSum'.format(self.rotate_multMatrix),
                         '{}.inputMatrix'.format(self.rotate_decomposeMatrix))

    def connect_object(self):
        if cmds.nodeType(self.driven) == 'joint':
            if not self.skipRotate == self.CHANNELS and not self.skipTranslate == self.CHANNELS:
                self.joint_rotate_matrix()

        self.decomposeMatrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(self.driven))
        cmds.connectAttr('{}.matrixSum'.format(self.main_multMatrix),
                         '{}.inputMatrix'.format(self.decomposeMatrix))

        self.connect_channel()

    def create_matrix_systems(self):
        skipTranslate = True if self.skipTranslate == self.CHANNELS else False
        skipRotate = True if self.skipRotate == self.CHANNELS else False

        for target in self.targets:
            matrix_system = MultMatrixSystem(target, self.driven, offset=self.offset, parent=self.parent,
                                             skipTranslate=skipTranslate, skipRotate=skipRotate)
            matrix_system.create_system()
            if cmds.nodeType(self.driven) == 'joint':
                print self.skipRotate, 'skipRotate'
                print self.skipTranslate == self.CHANNELS, 'skipTranslate'
                if not self.skipRotate == self.CHANNELS and self.skipTranslate == self.CHANNELS:
                    print 'add matrix'
                    matrix_system.add_matrix(self.get_jointOrient_matrix(self.driven))


            self.matrix_systems.append(matrix_system)

        if len(self.targets) > 1:
            self.blend_matrix(self.matrix_systems)
        else:
            self.main_multMatrix = self.matrix_systems[0].multMatrix

    def build(self):
        if not isinstance(self.targets, list):
            self.targets = [self.targets]

        pm.undoInfo(openChunk=True)

        self.create_matrix_systems()
        self.connect_object()

        pm.undoInfo(closeChunk=True)


class PointMatrix(MatrixConstraint):
    def __init__(self, targets, driven, offset=True, skipTranslate=()):
        super(PointMatrix, self).__init__(targets=targets, driven=driven, offset=offset,
                                          skipTranslate=skipTranslate, skipRotate=self.CHANNELS,
                                          skipScale=self.CHANNELS, parent=False)

        self.build()


class OrientMatrix(MatrixConstraint):
    def __init__(self, targets, driven, offset=True, skipRotate=()):
        super(OrientMatrix, self).__init__(targets=targets, driven=driven, offset=offset,
                                           skipTranslate=self.CHANNELS, skipRotate=skipRotate,
                                           skipScale=self.CHANNELS, parent=True)

        self.build()


class ScaleMatrix(MatrixConstraint):
    def __init__(self, targets, driven, offset=True, skipScale=()):
        super(ScaleMatrix, self).__init__(targets=targets, driven=driven, offset=offset,
                                          skipTranslate=self.CHANNELS, skipRotate=self.CHANNELS,
                                          skipScale=skipScale, parent=False)

        self.build()


class ParentMatrix(MatrixConstraint):
    def __init__(self, targets, driven, offset=True, skipTranslate=(), skipRotate=()):
        super(ParentMatrix, self).__init__(targets=targets, driven=driven, offset=offset,
                                           skipTranslate=skipTranslate, skipRotate=skipRotate,
                                           skipScale=self.CHANNELS, parent=True)

        self.build()
