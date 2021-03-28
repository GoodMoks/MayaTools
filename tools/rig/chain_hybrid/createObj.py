import maya.cmds as cmds
import utilities as utils


def create(target=None, typeNode='joint', underscore=False, typeControl='cube'):
    """Creates any transform objects


    :param target: 'list' list of files
    :param typeNode: 'str' type of node
           'locator'
           'group'
           'joint'

    :return: 'list' list of all created objects
    """
    createdObj = []

    if not target:
        target = cmds.ls(sl=True, fl=True)
        if not target:
        	target = ['']

    if target:
    	print target
    	for obj in target:
            if typeNode == 'locator':
                newName = utils.renamePrefix(obj, prefix='Loc', underscore=underscore)
                loc = cmds.spaceLocator(n=newName)[0]
                createdObj.append(loc)
                utils.align([loc], obj)

            elif typeNode == 'group':
                newName = utils.renamePrefix(obj, prefix='Grp', underscore=underscore)
                grp = cmds.createNode('transform', n=newName)
                createdObj.append(grp)
                utils.align([grp], obj)

            elif typeNode == 'joint':
                newName = utils.renamePrefix(obj, prefix='Jnt', underscore=underscore)
                jnt = cmds.createNode('joint', n=newName)
                createdObj.append(jnt)
                utils.align([jnt], obj)

            elif typeNode == 'control':
                newName = utils.renamePrefix(obj, prefix='CTRL', underscore=underscore)
                ctrl = utils.createCurve(name=newName, control=typeControl)
                createdObj.append(ctrl)
                utils.align([ctrl], obj, scale=True)
                cmds.makeIdentity(ctrl, a=True, scale=True)

    if createdObj:
        cmds.select(createdObj)
        return createdObj
    else:
        return []
