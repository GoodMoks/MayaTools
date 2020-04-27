import maya.cmds as cmds


def break_Con(obj=None, attr=None):
    """ Breaks input connections

    :param obj: 'list' list of objects
    :param attr: 'list' attr to disconnect
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    if obj:
        for o in obj:
            con_Pairs = []
            try:
                con = cmds.listConnections(o, plugs=True, connections=True, destination=False)
                if con:
                    con_Pairs.extend(zip(con[1::2], con[::2]))

                for source, dest in con_Pairs:
                    if attr:
                        full_Attr = o + attr
                        if dest == full_Attr:
                            cmds.disconnectAttr(source, dest)
                    else:
                        cmds.disconnectAttr(source, dest)
            except:
                pass


def unlockAttr(obj=None, attr=None):
    """ Unlocks main attributes

    :param obj: 'list' list of object
    :param attr: 'list' attr to unlock
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    if not attr:
        attrList = ['.tx', '.ty', '.tz',
                    '.rx', '.ry', '.rz',
                    '.sx', '.sy', '.sz',
                    '.visibility']

    for o in obj:
        for a in attrList:
            full_Attr = o + a
            try:
                cmds.setAttr(full_Attr, l=False, k=True)
            except:
                pass


def enabled_Layer(obj=None):
    """ Disable display layer

    :param obj:
    :return:
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    if obj:
        for o in obj:
            try:
                layers = cmds.listConnections(o, t='displayLayer')
                if layers:
                    for layer in layers:
                        cmds.setAttr(layer + '.enabled', 0)
            except:
                pass


def shape_Attr(obj=None):
    """ Set attributes for visibility

    :param obj: 'list' list of objects
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    attr_All = {
        '.overrideEnabled': 1,
        '.overrideDisplayType': 0,
        '.overrideLevelOfDetail': 0,
        '.overrideShading': 1,
        '.overrideTexturing': 1,
        '.overridePlayback': 1,
        '.overrideVisibility': 1,
        '.visibility': 1,
        '.lodVisibility': 1,
        '.template': 0,
        '.hiddenInOutliner': 0,
        '.hideOnPlayback': 0
    }
    if obj:
        for o in obj:
            try:
                shape_Node = cmds.listRelatives(o, s=True)
                if shape_Node:
                    for shape in shape_Node:
                        obj.append(shape)

                if cmds.objectType(o) == 'joint':
                    try:
                        cmds.setAttr(o + '.drawStyle', 0)
                    except:
                        pass

                for attr, value in attr_All.iteritems():
                    try:
                        cmds.setAttr(o + attr, value)
                    except:
                        pass
            except:
                pass


def build(obj=None):
    """ Run process

    :param obj: 'list' processing list
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)
        if not obj:
            obj = cmds.ls()

    if isinstance(obj, basestring):
        obj = [obj]

    if obj:
        child = cmds.listRelatives(obj, ad=True)

        unlockAttr(child)
        break_Con(child, attr='.visibility')
        enabled_Layer(child)
        shape_Attr(child)

    cmds.confirmDialog(title='Notification', message='DONE',
                       button=['OK'])