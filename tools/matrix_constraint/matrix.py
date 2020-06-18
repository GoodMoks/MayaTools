import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2


class MatrixConstraint(object):
    def __init__(self, name, maintainOffset=False, weight=1):
        self.name = name
        self.maintainOffset = maintainOffset
        self.weight = weight


class ParentMatrix(object):
    def __init__(self, targets, destination, maintainOffset=False):
        self.targets = targets
        self.destination = destination
        self.maintainOffset = maintainOffset

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
            offset =  target_worldMatrix * dest_inverseMatrix

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

            cmds.setAttr('{}.matrixIn[1]'.format(rotate_mult), self.jointOrient_offset(self.destination), type='matrix')
            cmds.connectAttr('{}.matrixSum'.format(rotate_mult),
                             '{}.inputMatrix'.format(rotate_dec))
            cmds.connectAttr('{}.outputRotate'.format(rotate_dec),
                             '{}.rotate'.format(self.destination))


class PointMatrix(object):
    def __init__(self):
        pass


class OrientMatrix(object):
    def __init__(self):
        pass


class ScaleMatrix(object):
    def __init__(self):
        pass
