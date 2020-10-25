import maya.cmds as cmds
import MayaTools.core.base as base


def get_influence_joint(obj):
    """ get all influences joints

    :param obj: 'str' object
    :return: 'list' of skinned joints
    """
    return base.get_history(obj, type='joint')


def get_skinCluster(obj):
    """ get all skinClusters

        :param obj: 'str' object
        :return: 'list' of skinClusters
        """
    return base.get_history(obj, type='skinCluster')

def get_bindPose(obj):
    """ get all bindPoses

        :param obj: 'str' object
        :return: 'list' of bindPoses
        """
    skinCluster = get_skinCluster(obj)
    if not skinCluster:
        return None
    return base.get_history(skinCluster, type='dagPose')

def compare_influence_joints(source, target):
    """ compare influence joints two skinned objects

    :param source: 'str' first object
    :param target: 'str' second object
    :return: 'bool' True if equal, False if not
    """
    source_joints = get_influence_joint(source)
    target_joints = get_influence_joint(target)

    if source_joints == target_joints:
        return True

    return False


def copy_skin(source, target):
    """ copy skin from first list objects, to another

    :param source: 'list' or 'str' objects
    :param target: 'list' or 'str' objects
    """
    cmds.select(source, target)
    cmds.copySkinWeights(noMirror=True,
                         surfaceAssociation='closestPoint',
                         influenceAssociation='oneToOne',
                         normalize=True)

def restore_skin(source, target):
    """ add a skin to the target, like the first

    :param source: 'str' object with skin
    :param target: 'str' object without skin
    :return: New skinCluster
    """
    joints = get_influence_joint(source)
    max_inf = cmds.skinCluster(get_skinCluster(source), q=True, mi=True)
    new_skinCluster = cmds.skinCluster(*(joints + [target]), tsb=True, mi=max_inf)
    copy_skin(source, target)
    return new_skinCluster