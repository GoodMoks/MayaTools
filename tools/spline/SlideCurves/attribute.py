import maya.cmds as cmds

def set_attr(objects=None, attr_name=None, value=None):
    for obj in objects:
        cmds.setAttr('{}.{}'.format(obj, attr_name), value)


def unlock_attr(obj=None, attr=None):
    """ Unlocks main attributes

    :param obj: 'list' list of object
    :param attr: 'list' attr to unlock
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    if not attr:
        attr = ['.tx', '.ty', '.tz',
                    '.rx', '.ry', '.rz',
                    '.sx', '.sy', '.sz',
                    '.visibility']

    for o in obj:
        for a in attr:
            full_Attr = o + a
            try:
                cmds.setAttr(full_Attr, l=False, k=True)
            except:
                pass


def delete_attr(obj=None, attr=None, force=True):
    """ Delete exist attributes

    :param obj: 'str' object with attributes
    :param attr: 'list' list of attributes
    :param force: 'bool' delete attr if exist connect or not
    """
    if attr and obj:
        for a in attr:
            exist = cmds.attributeQuery(a, node=obj, ex=True)
            if exist:
                connect = cmds.listConnections('{}.{}'.format(obj, a), c=True)
                if connect:
                    if force:
                        cmds.deleteAttr('{}.{}'.format(obj, a))
                else:
                    cmds.deleteAttr('{}.{}'.format(obj, a))