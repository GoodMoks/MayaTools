import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.base as base

reload(base)


def connect_cv_to_object(cv, obj):
    """ connect given cv to object

    :param cv: 'str' name of CV
    :param obj: 'str' object name
    :return: 'str' decompose matrix node
    """
    decompose = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(obj))
    cmds.connectAttr('{}.worldMatrix'.format(obj), '{}.inputMatrix'.format(decompose))
    cmds.connectAttr('{}.outputTranslate'.format(decompose), cv)
    return decompose


def connect_curve_to_objects(curve, objects=None):
    """ connect curve cvs to locator

    :param curve: 'str' curve name
    :param objects: 'list' objects to connect
    :return: 'list' control locators
    """

    count_point = len(cmds.getAttr('{}.controlPoints[*]'.format(curve)))
    if objects:
        if not len(objects) == count_point:
            return False

    controls = []
    for cv_index in xrange(count_point):
        if objects:
            ctrl = objects[cv_index]
        else:
            ctrl = cmds.spaceLocator(n='{}_cv{}_loc'.format(curve, cv_index))[0]
            cv_pos = cmds.xform('{}.cv[{}]'.format(curve, cv_index), ws=True, t=True, q=True)
            cmds.xform(ctrl, t=cv_pos)

        connect_cv_to_object('{}.cv[{}]'.format(curve, cv_index), ctrl)
        controls.append(ctrl)

    return controls


class SlideCurve(object):
    """ Creates a slide system for a curve

        Args:
            curve (str): name of nurbs curve

        Attributes:
            curve (str): name
            control (str): working curve name
            curve_info (str): curveInfo node
            motionPath (list): list of motionPath nodes
            blend_nodes (list): list of animBlendNodeAdditiveRotation nodes
        """
    ATTR = ['StretchMax', 'StretchMin', 'Length', 'Position']

    def __init__(self, curve):
        self.curve = curve
        self.control = self.curve
        self.curve_info = None

        self.motionPath = []
        self.blend_nodes = []

    def set_control_object(self, obj):
        self.control = obj

    def set_curveInfo(self, node):
        self.curve_info = node

    def set_global_scale_ctrl(self, obj, attr):
        cmds.setAttr('{}.operation'.format(self.scale_mult), 2)
        cmds.connectAttr('{}.{}'.format(obj, attr), '{}.input2X'.format(self.scale_mult))


    def add_slide_attr(self):
        try:
            cmds.addAttr(self.control, ln=self.ATTR[0], at='double', min=1, dv=1, k=True)
            cmds.addAttr(self.control, ln=self.ATTR[1], at='double', min=0, max=1, dv=1, k=True)
            cmds.addAttr(self.control, ln=self.ATTR[2], at='double', dv=1, k=True)
            cmds.addAttr(self.control, ln=self.ATTR[3], at='double', min=0, max=1, dv=0, k=True)
        except:
            pass

    def create_curveInfo(self):
        self.curve_info = cmds.createNode('curveInfo', n='{}_infoCurve'.format(self.curve))
        cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.inputCurve'.format(self.curve_info))

    def create(self):
        if not self.curve_info:
            self.create_curveInfo()

        self.add_slide_attr()

        self.length = cmds.getAttr('{}.arcLength'.format(self.curve_info))

        self.scale_mult = cmds.createNode('multiplyDivide', n='{}_lengthScale'.format(self.curve))
        cmds.setAttr('{}.input1Y'.format(self.scale_mult), self.length)
        cmds.connectAttr('{}.arcLength'.format(self.curve_info), '{}.input1X'.format(self.scale_mult))

        self.length_div = cmds.createNode('multiplyDivide', n='{}_lengthDiv'.format(self.curve))
        cmds.setAttr('{}.operation'.format(self.length_div), 2)

        cmds.connectAttr('{}.outputX'.format(self.scale_mult), '{}.input1Y'.format(self.length_div))
        cmds.connectAttr('{}.outputX'.format(self.scale_mult), '{}.input2X'.format(self.length_div))
        cmds.connectAttr('{}.outputY'.format(self.scale_mult), '{}.input1X'.format(self.length_div))
        cmds.connectAttr('{}.outputY'.format(self.scale_mult), '{}.input2Y'.format(self.length_div))

        self.min_cond = cmds.createNode('condition', n='{}_minCond'.format(self.curve))
        self.max_cond = cmds.createNode('condition', n='{}_maxCond'.format(self.curve))
        self.main_cond = cmds.createNode('condition', n='{}_mainCond'.format(self.curve))

        cmds.connectAttr('{}.outputY'.format(self.length_div), '{}.secondTerm'.format(self.min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.control), '{}.firstTerm'.format(self.min_cond))
        cmds.connectAttr('{}.StretchMin'.format(self.control), '{}.colorIfTrueR'.format(self.min_cond))
        cmds.connectAttr('{}.outputY'.format(self.length_div), '{}.colorIfFalseR'.format(self.min_cond))
        cmds.setAttr('{}.operation'.format(self.min_cond), 3)

        cmds.connectAttr('{}.outputY'.format(self.length_div), '{}.firstTerm'.format(self.max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.control), '{}.secondTerm'.format(self.max_cond))
        cmds.connectAttr('{}.StretchMax'.format(self.control), '{}.colorIfTrueR'.format(self.max_cond))
        cmds.connectAttr('{}.outputY'.format(self.length_div), '{}.colorIfFalseR'.format(self.max_cond))
        cmds.setAttr('{}.operation'.format(self.max_cond), 3)

        cmds.connectAttr('{}.outputY'.format(self.length_div), '{}.firstTerm'.format(self.main_cond))
        cmds.connectAttr('{}.outColorR'.format(self.min_cond), '{}.colorIfFalseR'.format(self.main_cond))
        cmds.connectAttr('{}.outColorR'.format(self.max_cond), '{}.colorIfTrueR'.format(self.main_cond))
        cmds.setAttr('{}.secondTerm'.format(self.main_cond), 1)
        cmds.setAttr('{}.operation'.format(self.main_cond), 2)

        self.length_negative = cmds.createNode('addDoubleLinear', n='{}_LengthNegative'.format(self.curve))
        cmds.connectAttr('{}.Length'.format(self.control), '{}.input1'.format(self.length_negative))
        cmds.setAttr('{}.input2 '.format(self.length_negative), -1)

        self.length_sum = cmds.createNode('addDoubleLinear', n='{}_LengthSum'.format(self.curve))
        cmds.connectAttr('{}.outColorR'.format(self.main_cond), '{}.input1'.format(self.length_sum))
        cmds.connectAttr('{}.output'.format(self.length_negative), '{}.input2'.format(self.length_sum))

        self.mult_coef = cmds.createNode('multDoubleLinear', n='{}_multCoeff'.format(self.curve))
        cmds.connectAttr('{}.outputX'.format(self.length_div), '{}.input1'.format(self.mult_coef))
        cmds.connectAttr('{}.output'.format(self.length_sum), '{}.input2'.format(self.mult_coef))

        self.rev_node = cmds.createNode('reverse', n='{}_weightRev'.format(self.curve))
        cmds.connectAttr('{}.output'.format(self.mult_coef), '{}.inputX'.format(self.rev_node))

    def set_item(self, item):
        cmds.connectAttr('{}.output'.format(self.mult_coef), '{}.weightA'.format(item.blend_node))
        cmds.connectAttr('{}.outputX'.format(self.rev_node), '{}.weightB'.format(item.blend_node))
        cmds.connectAttr('{}.Position'.format(self.control), '{}.inputB'.format(item.blend_node))


class SlideItem(object):
    """ Creates a slide item

        Args:
            curve (str): name of nurbs curve
            parameter (float): value for position node on curve
            prefix (str): prefix for each slide item
            parametric (bool): curve parameterization

        Attributes:
            curve (str): name
            prefix (str): prefix for item
            parameter (float): float value for motionPath
            parametric (list): state of curve parameterization
            driven (str): object that receives the transform
        """

    def __init__(self, curve, parameter, prefix, parametric=False):
        self.curve = curve
        self.prefix = prefix
        self.parameter = parameter
        self.parametric = not parametric

        self.driven = None

        self.create_item()

    def create_item(self):
        if not self.driven:
            self.create_driven()

        self.driver = cmds.createNode('motionPath', n='{}_mPath_{}'.format(self.curve, self.prefix))
        cmds.setAttr('{}.fractionMode'.format(self.driver), self.parametric)
        cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.geometryPath'.format(self.driver))
        self.blend_node = cmds.createNode('animBlendNodeAdditive', n='{}_{}_addOffset'.format(self.curve, self.prefix))
        cmds.setAttr('{}.inputA'.format(self.blend_node), self.parameter)
        cmds.connectAttr('{}.output'.format(self.blend_node), '{}.uValue'.format(self.driver))
        cmds.connectAttr('{}.allCoordinates'.format(self.driver), '{}.t'.format(self.driven))

    def create_driven(self):
        self.driven = cmds.createNode('transform', n='{}_{}'.format(self.curve, self.prefix))



class Curve(object):
    def __init__(self, objects, degree=None, name=None):
        """ class for create nurbs curve from given objects

        :param objects: 'list' objects
        :param degree: 'int' number of degree curve
        """
        self.objects = objects
        self.degree = degree
        self.name = name or 'NewCurve'
        self.curve = None
        self.count_objects = len(self.objects)

    def create_curve(self):
        if self.check_degree():
            if not self.degree:
                self.calculate_degree()

            self.build_curve()
            return self.curve

    def check_degree(self):
        if self.count_objects == 1:
            om2.MGlobal.displayError('Need more then 1 object')
            return False

        if not self.degree:
            return True

        if self.degree > 3:
            om2.MGlobal.displayError('I can only make a 3 degree curve')
            return False

        if not self.degree <= self.count_objects - 1:
            om2.MGlobal.displayError(
                'For a {} degree curve, {} objects are needed'.format(self.degree, self.degree + 1))
            return False

        return True

    def calculate_degree(self):
        self.degree = self.count_objects - 1
        if self.count_objects >= 4:
            self.degree = 3

    def build_curve(self):
        points = [(0, 0, 0) for x in range(self.count_objects)]
        self.curve = cmds.curve(p=points, degree=self.degree, n=self.name)
        try:
            for point, cv in zip(self.objects, range(self.count_objects)):
                point_pos = cmds.xform(point, ws=True, t=True, q=True)
                cmds.setAttr('{}.controlPoints[{}]'.format(self.curve, cv), point_pos[0], point_pos[1], point_pos[2],
                             type='double3')
        except:
            pass


class NewCurve(Curve):
    def __init__(self, objects, degree=None, connect=False):
        """ Additional functionality for Curve class

        :param objects: 'list' objects
        :param degree: 'int' number of curve degree
        :param connect: 'bool' True: connect cv curve to objects
        """
        super(NewCurve, self).__init__(objects, degree)
        self.connect = connect

        if self.create_curve():
            if self.connect:
                self.connect_cv()

    def connect_cv(self):
        if not self.count_objects == len(self.objects):
            om2.MGlobal.displayError('Cv counting curve is not equal to the number of objects to connect')

        connect_curve_to_objects(self.curve, self.objects)


def connect_to_cv(curve, step=40, obj_type='joint'):  # WIP
    """

    :param curve:
    :param step:
    :param obj_type:
    :return:
    """
    curve_info = cmds.createNode('curveInfo', n='{}_info'.format(curve))
    cmds.connectAttr('{}.local'.format(curve), '{}.inputCurve'.format(curve_info))
    count_points = len(cmds.getAttr('{}.controlPoints[*]'.format(curve_info)))

    if not count_points % step:
        return False

    objs = []
    for point in range(0, count_points, step):
        connect_obj = cmds.createNode(obj_type, n='{}_crv_cv{}'.format(curve, point))
        objs.append(connect_obj)
        cmds.connectAttr('{}.controlPoints[{}]'.format(curve_info, point), '{}.translate'.format(connect_obj))

    group = cmds.createNode('transform', n='{}_crv_objs_grp'.format(curve))
    cmds.parent(objs, group)

    return objs


def get_closest_U_param(curve, point, normalize=True):
    curve_dag_path = base.get_dagPath(curve)
    curve_fn = om2.MFnNurbsCurve(curve_dag_path)
    point = om2.MPoint(point)
    param = curve_fn.closestPoint(point)[1]
    if not normalize:
        return param

    min_max_param = cmds.getAttr('{}.minMaxValue'.format(curve))[0]
    param = abs((param - min_max_param[0]) / (min_max_param[1] - min_max_param[0]))
    return param
