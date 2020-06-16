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