import pymel.core as pm
import maya.OpenMaya as om


class JointBreaker(object):
    @staticmethod
    def get_orient(obj):
        rotation = pm.xform(obj, q=True, ro=True, ws=True)
        rv = om.MVector(rotation[0], rotation[1], rotation[2])

        return rv

    @staticmethod
    def vector_divide(v, dp):
        div_distance = v / dp

        return div_distance

    @staticmethod
    def get_transform(obj):
        xtr = pm.xform(obj, q=True, piv=True, ws=True)
        mv = om.MVector(xtr[0], xtr[1], xtr[2])

        return mv

    @staticmethod
    def get_selected():
        selected_jnt = pm.selected()
        if not selected_jnt:
            om.MGlobal.displayError("Nothing selected")
            return

        if len(selected_jnt) != 2:
            om.MGlobal.displayError("Select two joint to add joints between them")
            return

        return selected_jnt

    @staticmethod
    def parent_joint(par, chain, ch):
        for i in range(len(chain) - 1):
            pm.parent(chain[i], chain[i + 1])

        pm.parent(chain[-1], par)
        pm.parent(ch, chain[0])

    def __init__(self, divide_point, parent_flag):
        self.divide_point = divide_point
        self.parent_flag = parent_flag

        self.created_joints = []
        self.insert()

    def insert(self):
        selected = self.get_selected()
        if selected:
            self.parent, self.child = selected
            self.v1 = self.get_transform(self.parent)
            self.v2 = self.get_transform(self.child)

            self.distance = self.v1 - self.v2
            self.div_dist = self.vector_divide(self.distance, self.divide_point)

            self.insert_joint()

            if self.parent_flag:
                self.parent_joint(self.parent, self.created_joints, self.child)

    def insert_joint(self):
        for i in range(self.divide_point - 1):
            self.v2 += self.div_dist
            jnt = self.create_joint(self.v2, self.parent)
            self.created_joints.append(jnt)

    def create_joint(self, v, par):
        rv = self.get_orient(par)
        pm.select(cl=True)
        joint = pm.joint(p=(v.x, v.y, v.z), o=(rv.x, rv.y, rv.z))
        return joint
