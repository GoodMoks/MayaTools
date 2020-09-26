import os
import re
import json
import time
import maya.cmds as cmds


def timeInfo(func):
    """Decorator to track the time

    Args: func: [function for decorate]
    Returns: [func]
    """

    def timeRun(*args, **kw):
        start = time.time()
        result = func(*args, **kw)
        end = time.time()

        print 'Time: {}'.format(end - start)

        return result

    return timeRun


def flatten_list(obj=None):
    """ Decomposes the components

    Get objects list
    list(flatten_list(obj))

    :param obj: 'list'
    :return: 'generator'
    """
    if obj:
        if isinstance(obj, basestring):
            obj = [obj]

    if obj:
        for l in obj:
            list_flat = cmds.ls(l, fl=True)
            for item in list_flat:
                if isinstance(item, list):
                    for i in item:
                        yield i
                else:
                    yield item


def align(source=None, target=None, translate=True, rotate=True, scale=False):
    """ Align transform objects to target object

    :param source: 'list' objects for align
    :param target: 'string' target object
    :translate: 'bool' default True
    :rotate: 'bool' default True
    :scale: 'bool' default False
    """

    if not source or target:
        select = cmds.ls(sl=True)
        if select and len(select) >= 2:
            source = select[:-1]
            target = select[-1]

    if source and target:
        if isinstance(source, list):
            w_rotate = cmds.xform(target, q=True, ws=True, ro=True)
            w_trans = cmds.xform(target, q=True, ws=True, t=True)
            w_scale = cmds.xform(target, q=True, ws=True, s=True)
            for obj in source:
                if translate:
                    try:
                        cmds.xform(obj, ws=True, t=w_trans)
                    except:
                        pass
                if rotate:
                    try:
                        cmds.xform(obj, ws=True, ro=w_rotate)
                    except:
                        pass
                if scale:
                    try:
                        cmds.xform(obj, ws=True, s=w_scale)
                    except:
                        pass


def nullGrp(obj=None, prefix='Con', typeNode='transform', underscore=True):
    """ Adds a group on top

    :param obj: 'list' list of objects
    :param prefix: 'str' prefix to add
    :param typeNode: 'str' type of obj
    :param underscore: 'bool' add underscore or not
    :return: 'list' list of created group
    """
    createdGrp = []

    if not obj:
        select = cmds.ls(sl=True, fl=True)
        if select:
            obj = select

    if isinstance(obj, list):
        for object in obj:
            if isinstance(object, basestring):
                nameGrp = renamePrefix(object, prefix=prefix, underscore=underscore)

                nullGroup = cmds.createNode(typeNode, n=nameGrp)
                createdGrp.append(nullGroup)
                align([nullGroup], object)
                parents = cmds.listRelatives(object, p=True)
                try:
                    cmds.parent(object, nullGroup)
                    cmds.parent(nullGroup, parents)
                except:
                    pass

    cmds.select(obj)

    return createdGrp


def createCurve(name='', control='circle'):
    """ Creates NURBS curves

    :param name: 'str' name object
    :param control: 'str' shape of the curves
    :return: 'str' new object
    """
    if isinstance(name, basestring) and isinstance(control, basestring):
        baseDir = os.path.dirname(__file__)
        nameFile = 'control_manager.json'
        path = os.path.join(baseDir, nameFile)

        with open(path) as f:
            control = json.load(f)[control]

        curve = cmds.curve(degree=control['degree'],
                           knot=control['knot'],
                           point=control['point'],
                           periodic=control['periodic'])
        if not name == '':
            curve = cmds.rename(curve, name)

        return curve


def addNumber(name):
    """ Adds count number to line end

    :param name: 'str' name of object
    :return: 'str' new name with number at the end
    """
    number = 0
    exist = False
    while exist == False:
        if re.findall('\d$', name):
            nameBase, number, empty = re.split(r'(\d+)$', name)
            number = int(number)
        else:
            nameBase = name

        number += 1
        if nameBase.endswith('_'):
            newName = nameBase + '{}'.format(number)
        else:
            newName = nameBase + '_{}'.format(number)

        if not cmds.objExists(newName):
            exist = True
            return newName


def defaultPrefix(name):
    """ Deletes the prefix at the end of the line

    :param name: 'str' name of object
    :return: 'str' name without prefix and underscore
    """
    if not name:
        return []

    # Default prefix
    prefixList = ['Jnt', 'jnt', 'JNT', 'ctrl', 'Ctrl', 'CTRL', 'loc', 'Loc', 'LOC',
                  'IK', 'ik', 'Ik', 'grp', 'Grp', 'GRP']

    # Remove All ends prefix
    definePrefix = [x for x in prefixList if name.endswith(x)]

    # Delete prefix
    if definePrefix:
        name = re.sub('{}$'.format(definePrefix[0]), '', name)

    # Delete undescore at the line
    if name.endswith('_'):
        name = re.sub('_$', '', name)

    return name


def renamePrefix(name=None, prefix='', underscore=True):
    """ Add prefix and count number

    :param name: 'str' name of object
    :param prefix: 'str' prefix
    :param underscore: 'bool' add underscore or not
    :return: 'str' new name
    """
    if name:
        nameSplit = name.split('.')[0]
        name = defaultPrefix(nameSplit)

        if underscore:
            newName = name + '_{}'.format(prefix)
        else:
            newName = name + '{}'.format(prefix)

        if cmds.objExists(newName):
            newName = addNumber(newName)

        return newName
    else:
        newName = prefix
        if cmds.objExists(newName):
            newName = addNumber(newName)

        return newName