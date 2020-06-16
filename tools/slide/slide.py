import maya.cmds as cmds
import MayaTools.core.utils as utils
import MayaTools.core.curve as curve

reload(curve)
reload(utils)


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

    def set_driven_curve(self, curve):
        for index, driver in enumerate(curve.driver_nodes):
            cmds.connectAttr('{}.worldSpace'.format(self.curve), '{}.geometryPath'.format(driver))
            cmds.connectAttr('{}.output'.format(self.mult_coef), '{}.weightA'.format(curve.blend_nodes[index]))
            cmds.connectAttr('{}.outputX'.format(self.rev_node), '{}.weightB'.format(curve.blend_nodes[index]))
            cmds.connectAttr('{}.Position'.format(self.control), '{}.inputB'.format(curve.blend_nodes[index]))


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

    def __init__(self, curve, parameter, prefix, parametric=False, driven=None):
        self.curve = curve
        self.prefix = prefix
        self.parameter = parameter
        self.parametric = not parametric

        self.driven = driven

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


class DrivenSlideCurve(object):
    """ Create driven slide curve

            Args:
                curve (str): name of nurbs curve
                parametric (bool): curve parameterization

            Attributes:
                curve (str): name
                parametric (list): state of curve parameterization
                driver_nodes (list): list motionPath nodes
                blend_nodes (list): list blend nodes
            """

    def __init__(self, curve, parametric=False):
        self.curve = curve
        self.parametric = not parametric

        self.driver_nodes = []
        self.blend_nodes = []

        self.create_driven_curve()

    def create_driven_curve(self):
        cv = len(cmds.getAttr('{}.controlPoints[*]'.format(self.curve)))
        value = utils.get_value_range(cv, 1)
        for number, v in enumerate(value):
            driver = cmds.createNode('motionPath', n='{}_mPath_{}'.format(self.curve, str(number)))
            cmds.setAttr('{}.fractionMode'.format(driver), self.parametric)
            blend_node = cmds.createNode('animBlendNodeAdditive', n='{}_{}_addOffset'.format(self.curve, number))
            cmds.setAttr('{}.inputA'.format(blend_node), v)
            cmds.connectAttr('{}.output'.format(blend_node), '{}.uValue'.format(driver))
            cmds.connectAttr('{}.allCoordinates'.format(driver), '{}.controlPoints[{}]'.format(self.curve, number))
            self.driver_nodes.append(driver)
            self.blend_nodes.append(blend_node)



