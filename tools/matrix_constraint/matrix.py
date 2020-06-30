import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2


def test():
    sel = cmds.ls(sl=True)
    if sel:
        if len(sel) > 1:
            targets = sel[:-1]
            driven = sel[-1]
            print targets, 'targets'
            print driven, 'driven'
            # PointMatrix(destination, target)
            MatrixConstraint(targets, driven)


class MatrixSystem(object):
    @staticmethod
    def calculate_offset_matrix(driver, driven):
        driver_inverseMatrix = pm.getAttr('{}.worldInverseMatrix'.format(driver))
        driven_worldMatrix = pm.getAttr('{}.worldMatrix'.format(driven))
        return driven_worldMatrix * driver_inverseMatrix

    MATRIX_ATTR = 'worldMatrix'

    def __init__(self, target, driven, offset=True, parent=True):
        self.target = target
        self.driven = driven
        self.parent = parent
        self.offset = offset

        self.multMatrix = None

        self.input_index = [0, 1, 2]
        if parent:
            self.input_index = [1, 2, 0]

    def create_system(self):
        self.create_multMatrix()
        self.connect_nodes()
        if self.offset:
            self.set_offset()

    def create_multMatrix(self):
        self.multMatrix = cmds.createNode('multMatrix', n='{}_multOffset'.format(self.driven))

    def connect_nodes(self):
        cmds.connectAttr('{}.{}'.format(self.target, self.MATRIX_ATTR),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[0]))
        cmds.connectAttr('{}.parentInverseMatrix'.format(self.driven),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[1]))

    def set_offset(self):
        offset = self.calculate_offset_matrix(self.target, self.driven)
        pm.setAttr('{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[2]), offset)



class MatrixConstraint(object):
    @staticmethod
    def get_selected():
        sel = cmds.ls(sl=True)
        if not sel:
            om2.MGlobal.displayError('Nothing selected')
            return

        if not len(sel) > 1:
            om2.MGlobal.displayError('There must be 2 selected objects')

        return sel

    def __init__(self, targets, driven, offset=True, parent=True, translate=True, rotate=True, scale=True):
        self.targets = targets
        self.driven = driven
        self.offset = offset
        self.parent = parent

        self.translate = translate
        self.rotate = rotate
        self.scale = scale

        self.matrix_systems = []
        self.wtAddMatrix = None
        self.decomposeMatrix = None
        self.orient_multMatrix = None
        self.main_multMatrix = None

        self.blend_state = False



    def blend_matrix(self, matrix_system):
        self.wtAddMatrix = cmds.createNode('wtAddMatrix', n='{}_blendMatrix'.format(self.driven))
        param = 1 / float(len(matrix_system))
        for index, system in enumerate(matrix_system):
            cmds.connectAttr('{}.matrixSum'.format(system.multMatrix),
                             '{}.wtMatrix[{}].matrixIn'.format(self.wtAddMatrix, index))
            cmds.setAttr('{}.wtMatrix[{}].weightIn'.format(self.wtAddMatrix, index), param)

        self.main_multMatrix = self.wtAddMatrix

    def connect_channel(self, skip_rotate=True):
        if self.translate:
            cmds.connectAttr('{}.outputTranslate'.format(self.decomposeMatrix),
                             '{}.translate'.format(self.driven), f=True)
        if self.rotate and not skip_rotate:
            cmds.connectAttr('{}.outputRotate'.format(self.decomposeMatrix),
                             '{}.rotate'.format(self.driven), f=True)
        if self.scale:
            cmds.connectAttr('{}.outputScale'.format(self.decomposeMatrix),
                             '{}.scale'.format(self.driven), f=True)

    def joint_rotate_matrix(self):
        self.rotate_multMatrix = cmds.createNode('multMatrix', n='rotate_multOffset'.format(self.driven))
        self.rotate_decomposeMatrix = cmds.createNode('decomposeMatrix', n='{}_rotate_decMatrix'.format(self.driven))

        compose = cmds.createNode('composeMatrix')
        cmds.connectAttr('{}.jointOrient'.format(self.driven),
                         '{}.inputRotate'.format(compose))
        matrix = cmds.getAttr('{}.outputMatrix'.format(compose))
        cmds.setAttr('{}.matrixIn[1]'.format(self.rotate_multMatrix), matrix, type='matrix')
        cmds.connectAttr('{}.matrixSum'.format(self.main_multMatrix),
                         '{}.matrixIn[0]'.format(self.rotate_multMatrix))
        cmds.connectAttr('{}.matrixSum'.format(self.rotate_multMatrix),
                         '{}.inputMatrix'.format(self.rotate_decomposeMatrix))
        cmds.connectAttr('{}.outputRotate'.format(self.rotate_decomposeMatrix), '{}.rotate'.format(self.driven))

        cmds.delete(compose)

    def connect_object(self):
        skip_rotate = False
        if cmds.nodeType(self.driven) == 'joint':
            if self.rotate:
                self.joint_rotate_matrix()
                skip_rotate = True

        self.decomposeMatrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(self.driven))
        cmds.connectAttr('{}.matrixSum'.format(self.main_multMatrix),
                         '{}.inputMatrix'.format(self.decomposeMatrix))
        self.connect_channel(skip_rotate=skip_rotate)

    def create_matrix_systems(self):
        for target in self.targets:
            matrix_system = MatrixSystem(target, self.driven, offset=self.offset, parent=self.parent)
            matrix_system.create_system()
            self.matrix_systems.append(matrix_system)

        if len(self.targets) > 1:
            self.blend_state = True
        else:
            self.main_multMatrix = self.matrix_systems[0].multMatrix

    def build(self):
        if not isinstance(self.targets, list):
            self.targets = [self.targets]

        self.create_matrix_systems()
        if self.blend_state:
            self.blend_matrix(self.matrix_systems)

        self.connect_object()


class PointMatrix(MatrixConstraint):
    def __init__(self, targets=None, driven=None, offset=True):
        self.targets = targets
        self.driven = driven
        self.offset = offset

    # def make_constraint(self):
    #     if
    #     super(PointMatrix, self).__init__(driver, dr)



class MatrixConstraintBase(object):

    def __init__(self, driver, driven, offset=False, parent=True):
        self.driver = driver
        self.driven = driven
        self.parent = parent
        self.offset = offset

        self.multMatrix = None
        self.decomposeMatrix = None

    def create_nodes(self):
        self.multMatrix = cmds.createNode('multMatrix')
        self.decomposeMatrix = cmds.createNode('decomposeMatrix')

    def connect_nodes(self):
        cmds.connectAttr('{}.worldMatrix'.format(self.driver),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[0]))
        cmds.connectAttr('{}.parentInverseMatrix'.format(self.driven),
                         '{}.matrixIn[{}]'.format(self.multMatrix, self.input_index[1]))
        cmds.connectAttr('{}.matrixSum'.format(self.multMatrix),
                         '{}.inputMatrix'.format(self.decomposeMatrix))

    def connect_object(self, translate=True, rotate=False, scale=False, shear=False):
        if translate:
            cmds.connectAttr('{}.outputTranslate'.format(self.decomposeMatrix),
                             '{}.translate'.format(self.driven), f=True)
        if rotate:
            cmds.connectAttr('{}.outputRotate'.format(self.decomposeMatrix),
                             '{}.rotate'.format(self.driven), f=True)
        if scale:
            cmds.connectAttr('{}.outputScale'.format(self.decomposeMatrix),
                             '{}.scale'.format(self.driven), f=True)
        if shear:
            cmds.connectAttr('{}.outputShear'.format(self.decomposeMatrix),
                             '{}.shear'.format(self.driven), f=True)


class ParentMatrix(object):
    def __init__(self, targets, destination, offset=True):
        self.targets = targets
        self.destination = destination
        self.maintainOffset = offset

        self.main()

    def calculate_offset_matrix(self, matrix1, matrix2):
        matrix1 = pm.dt.Matrix(matrix1)
        matrix2 = pm.dt.Matrix(matrix2)

    def jointOrient_offset(self, joint):
        compose = cmds.createNode('composeMatrix')
        try:
            cmds.connectAttr('{}.jointOrient'.format(joint),
                             '{}.inputRotate'.format(compose))
        except:
            cmds.connectAttr('{}.rotate'.format(joint),
                             '{}.inputRotate'.format(compose))
        matrix = cmds.getAttr('{}.outputMatrix'.format(compose))
        cmds.delete(compose)
        return matrix

    def main(self):
        if not isinstance(self.targets, list):
            self.targets = [self.targets]

        for target in self.targets:
            mult_node = cmds.createNode('multMatrix')
            dec_node = cmds.createNode('decomposeMatrix')

            target_worldMatrix = pm.getAttr('{}.worldMatrix'.format(self.destination))
            dest_inverseMatrix = pm.getAttr('{}.worldInverseMatrix'.format(target))
            offset = target_worldMatrix * dest_inverseMatrix

            # connect matrix nodes
            pm.setAttr('{}.matrixIn[0]'.format(mult_node), offset)
            cmds.connectAttr('{}.worldMatrix'.format(target),
                             '{}.matrixIn[1]'.format(mult_node))
            cmds.connectAttr('{}.parentInverseMatrix'.format(self.destination),
                             '{}.matrixIn[2]'.format(mult_node))
            cmds.connectAttr('{}.matrixSum'.format(mult_node),
                             '{}.inputMatrix'.format(dec_node))

            # connect decompose to object

            cmds.connectAttr('{}.outputTranslate'.format(dec_node),
                             '{}.translate'.format(self.destination))

            rotate_mult = cmds.createNode('multMatrix')
            rotate_dec = cmds.createNode('decomposeMatrix')
            cmds.connectAttr('{}.matrixSum'.format(mult_node),
                             '{}.matrixIn[0]'.format(rotate_mult))

            orient_offset = self.jointOrient_offset(self.destination)
            cmds.setAttr('{}.matrixIn[1]'.format(rotate_mult), orient_offset, type='matrix')
            cmds.connectAttr('{}.matrixSum'.format(rotate_mult),
                             '{}.inputMatrix'.format(rotate_dec))
            cmds.connectAttr('{}.outputRotate'.format(rotate_dec),
                             '{}.rotate'.format(self.destination))


class PointMatrix_old(object):
    MATRIX_ATTR = 'worldMatrix'

    # return offset

    def __init__(self, destination, target, maintainOffset=True):
        self.destination = destination
        self.target = target
        self.maintainOffset = maintainOffset

        self.build()

    def build(self):
        self.create_node()

        self.connect_nodes()
        if self.maintainOffset:
            self.set_offset_matrix()
        self.connect_object()

    def set_offset_matrix(self):
        offset = self.calculate_offset_matrix(self.target, self.destination)
        pm.setAttr('{}.matrixIn[2]'.format(self.mult_node), offset)

    def create_node(self):
        self.mult_node = cmds.createNode('multMatrix')
        self.dec_node = cmds.createNode('decomposeMatrix')

    def connect_nodes(self):
        cmds.connectAttr('{}.worldMatrix'.format(self.target),
                         '{}.matrixIn[0]'.format(self.mult_node))
        cmds.connectAttr('{}.parentInverseMatrix'.format(self.destination),
                         '{}.matrixIn[1]'.format(self.mult_node))
        cmds.connectAttr('{}.matrixSum'.format(self.mult_node),
                         '{}.inputMatrix'.format(self.dec_node))

    def connect_object(self):
        cmds.connectAttr('{}.outputTranslate'.format(self.dec_node),
                         '{}.translate'.format(self.destination))


class OrientMatrix(object):
    def __init__(self, destination, target, maintainOffset=True):
        self.destination = destination
        self.target = target
        self.maintainOffset = maintainOffset


class ScaleMatrix(object):
    def __init__(self):
        pass
