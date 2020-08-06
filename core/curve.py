import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.core.base as base
import MayaTools.core.utils as utils
import MayaTools.core.dag as dag


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


class CurveShape(object):
    def __init__(self):
        self.point = None
        self.degree = None
        self.periodic = None
        self.knot = None

    def __add(self, point, degree, periodic, knot):
        if not isinstance(point, list):
            raise TypeError('Point must be list: [[0, 0, 0], [0, 0, 0], [0, 0, 0], ...]')

        if not isinstance(degree, int):
            raise TypeError('Degree must be integer')

        if not isinstance(periodic, int):
            raise TypeError('Periodic must be integer')

        if not isinstance(point, list):
            raise TypeError('Knot must be list: [0, 1, 2, 3, 4, 5, ...]')

        if len(point) + 1 <= degree:
            raise ValueError('Points must be 1 more than the degree')

        self.point = point
        self.degree = degree
        self.periodic = periodic
        self.knot = knot


    def add_control(self, control):
        shape = dag.get_shapes(control)
        if not shape:
            raise ValueError('{} has no shape'.format(control))

        if not cmds.nodeType(shape[0]) == 'nurbsCurve':
            raise TypeError('{} not nurbsCurve'.format(control))

        point = cmds.getAttr("{0}.cv[*]".format(shape[0]))
        degree = cmds.getAttr("{0}.degree".format(shape[0]))
        periodic = cmds.getAttr("{0}.form".format(shape[0]))
        knot = get_curve_knots(control)

        self.__add(point, degree, periodic, knot)

    def get_data(self):
        return dict(
            knot=self.knot,
            point=self.point,
            degree=self.degree,
            periodic=self.periodic
        )

    def add_data(self, data):
        self.__add(data['point'], data['degree'],
                   data['periodic'], data['knot'])

    def add_shape(self, point, degree, periodic=0, knot=None):
        if periodic and not knot:
            knot = []

        self.__add(point, degree, periodic, knot)


class Curve(object):
    def __init__(self, shape):
        self.shape = shape

        if not isinstance(shape, CurveShape):
            raise TypeError('Argument must be of instance class "{}"'.format(shape.CurveShape.__name__))

        self.name = 'NewCurve'

        self.knot = self.shape.knot
        self.point = self.shape.point
        self.degree = self.shape.degree
        self.periodic = self.shape.periodic

        self.curve = None

    def __create_curve(self):
        point = self.point + self.point[:self.degree] if self.periodic else self.point
        self.curve = cmds.curve(degree=self.degree, knot=self.knot, point=point,
                                periodic=self.periodic, name=self.name)

    def create(self, name=None):
        self.name = name if name else self.name
        self.__create_curve()
        return self.curve


class CurveObjects(object):
    def __init__(self, objects, degree=None, name=None, connect=False):
        """ class for create nurbs curve from given objects

        :param objects: 'list' objects
        :param degree: 'int' number of degree curve
        """
        self.objects = objects
        self.degree = degree
        self.connect = connect
        self.name = name

        self.curve = None

        self.count_objects = len(self.objects)

    def create(self):
        if self.check_degree():
            if not self.degree:
                self.calculate_degree()

            self.create_curve()

            if self.connect:
                self.connect_cv()

            return self.curve

    def check_degree(self):
        if self.count_objects == 1:
            om2.MGlobal.displayError('Need more then 1 object')
            return False

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

    def create_curve(self):
        points = [(0, 0, 0) for x in range(self.count_objects)]

        curve_shape = CurveShape()
        curve_shape.add_shape(point=points, degree=self.degree)
        curve_main = Curve(curve_shape)
        self.curve = curve_main.create()

        for point, cv in zip(self.objects, range(self.count_objects)):
            point_pos = cmds.xform(point, ws=True, t=True, q=True)
            cmds.setAttr('{}.controlPoints[{}]'.format(self.curve, cv), point_pos[0], point_pos[1], point_pos[2],
                         type='double3')

    def connect_cv(self):
        connect_curve_to_objects(self.curve, self.objects)


class RebuildCurveMPath(object):
    def __init__(self, curve, degree=3, spans=1, smooth=1, parametric=False, match=False, connection=False,
                 prefix=None):
        self.curve = curve
        self.degree = degree
        self.spans = spans
        self.smooth = smooth
        self.parametric = not parametric
        self.match = match
        self.connection = connection
        self.prefix = 'rebuild' if not prefix else prefix

        self.rebuild_curve = None

        self.points_count = self.degree + self.spans
        if match:
            self.points_count = len(cmds.getAttr('{}.controlPoints[*]'.format(self.curve)))

        self.range_value = 1
        if not self.parametric:
            cmds.getAttr('{}.spans'.format(self.curve))

        self.smooth_points = self.points_count * self.smooth
        self.rebuild_points = [x for x in xrange(self.smooth_points)]
        self.values = utils.get_value_range(self.smooth_points, self.range_value)

        self.rebuild()

    def rebuild(self):
        self.rebuild_curve = CurveObjects(objects=self.rebuild_points, degree=self.degree,
                                          name='{}_{}'.format(self.curve, self.prefix)).create()

        for n, v in enumerate(self.values):
            driver = cmds.createNode('motionPath')
            cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.geometryPath'.format(driver))
            cmds.setAttr('{}.fractionMode'.format(driver), self.parametric)
            cmds.setAttr('{}.uValue'.format(driver), v)
            cmds.connectAttr('{}.allCoordinates'.format(driver), '{}.controlPoints[{}]'.format(self.rebuild_curve, n))
            if not self.connection:
                cmds.disconnectAttr('{}.allCoordinates'.format(driver),
                                    '{}.controlPoints[{}]'.format(self.rebuild_curve, n))
                cmds.delete(driver)


def get_curve_knots(curve):
    dag_curve = base.get_dagPath(curve)
    fn_curve = om2.MFnNurbsCurve()
    fn_curve.setObject(dag_curve)
    return list(fn_curve.knots())


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
