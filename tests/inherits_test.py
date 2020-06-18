import pymel.core as pm
import maya.cmds as cmds

'''
import MayaTools.tests.inherits_test as test
reload(test)

#test.main()
#test.main_inherits()
'''

path = r"E:\Work\Pipeline\Projects\Speed_test\parentC.mb"
range = 500
def main():
    for i in xrange(range):
        cmds.file(path, i=True, ns='test_{}'.format(i))


def main_inherits():
    set_inherits(get_all_constraint(), 0)


def get_all_constraint():
    const_all = ['parentConstraint', 'pointConstraint',
                 'orientConstraint', 'aimConstraint',
                 'scaleConstraint', 'poleVectorConstraint', 'transform']

    constraint = []
    for c_type in const_all:
        const = pm.ls(type=c_type)
        if const:
            for c in const:
                constraint.append(c)

    return constraint


def set_inherits(objects, state=1):
    for p in objects:
        p.inheritsTransform.set(state)
    'done'

def gen_jnt():
    range = 10000
    prev = None
    for item in xrange(range):
        jnt = pm.createNode('joint')
        if prev:
            # dec = pm.createNode('decomposeMatrix')
            # prev.worldMatrix.connect(dec.inputMatrix)
            # dec.outputTranslate.connect(jnt.translate)
            # dec.outputRotate.connect(jnt.rotate)

            con = pm.parentConstraint(prev, jnt)
            con.inheritsTransform.set(1)
            prev = jnt
        prev = jnt
