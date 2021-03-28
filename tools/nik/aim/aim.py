import maya.OpenMaya as om
import math


class AimObject(object):
    @staticmethod
    def get_rotate_pivot(obj):
        transform_fn = om.MFnTransform(obj)
        rotate_pivot = transform_fn.rotatePivot(om.MSpace.kWorld)
        return om.MVector(rotate_pivot.x, rotate_pivot.y, rotate_pivot.z)

    @staticmethod
    def get_dag_path(obj):
        dag_path = om.MDagPath()
        sel = om.MSelectionList()
        sel.add(str(obj))
        sel.getDagPath(0, dag_path)
        return dag_path

    def __init__(self, eye, target, up, x_aim, y_aim, z_aim, x_up, y_up, z_up):
        self.eye = eye
        self.target = target
        self.up = up
        self.x_aim = x_aim
        self.y_aim = y_aim
        self.z_aim = z_aim
        self.x_up = x_up
        self.y_up = y_up
        self.z_up = z_up
        self.aim_object()

    def aim_object(self):

        if self.x_aim:
            eye_aim = om.MVector().xAxis
        if self.y_aim:
            eye_aim = om.MVector().yAxis
        if self.z_aim:
            eye_aim = om.MVector().zAxis

        if self.x_up:
            aim_up = om.MVector().xAxis

        if self.y_up:
            aim_up = om.MVector().yAxis

        if self.z_up:
            aim_up = om.MVector().zAxis

        target_dg = self.get_dag_path(self.target)
        aim_dg = self.get_dag_path(self.eye)
        manual_up = self.get_dag_path(self.up)

        aim_pivot_pos = self.get_rotate_pivot(aim_dg)
        target_pivot_pos = self.get_rotate_pivot(target_dg)
        manual_up_vector = self.get_rotate_pivot(manual_up)

        aim_vector = (target_pivot_pos - aim_pivot_pos).normal()  # finding AIM vector

        aim_u = (aim_vector ^ manual_up_vector).normal()  # finding ortogonal up vector

        aim_v = (aim_u ^ aim_vector).normal()  # finding ortogonal up vector

        quat = om.MQuaternion(eye_aim, aim_vector)  # create wright aim quaternion

        up_rotated = aim_up.rotateBy(quat)

        angle = math.acos(up_rotated * aim_v)

        quat_v = om.MQuaternion(angle, aim_vector)

        if not aim_v.isEquivalent(up_rotated.rotateBy(quat_v), 1.0e-5):
            angle = (2 * math.pi) - angle
            quat_v = om.MQuaternion(angle, aim_vector)

        quat *= quat_v
        transform_fn = om.MFnTransform(aim_dg)
        transform_fn.setRotation(quat)
