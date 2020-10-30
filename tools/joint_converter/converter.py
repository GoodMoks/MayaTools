import maya.cmds as cmds
import MayaTools.core.dag as dag
import MayaTools.core.transform as transform
import MayaTools.core.vector as vector


class JointConverter(object):
    @staticmethod
    def get_hierarchy_joints(root):
        child = dag.get_children(root, all=True, type='joint')
        child.append(root)
        return child

    NAME = 'skeleton_geo'

    def __init__(self, root, joint_radius=1, middle_radius=1):
        self.root = root
        self.joint_radius = joint_radius
        self.middle_radius = joint_radius if middle_radius == 1 else (joint_radius + (middle_radius - 1) * joint_radius)

        self.check_arguments()

        self.all_geo = []

        self.build()

    def check_arguments(self):
        if not isinstance(self.root, basestring):
            raise AttributeError('Attribute skeleton must be a string')

        if not cmds.objExists(self.root):
            raise AttributeError('{} object does not exist'.format(self.root))

        if not cmds.objectType(self.root) == 'joint':
            raise AttributeError('{} must be a joint'.format(self.root))

    def build(self):
        children = self.get_hierarchy_joints(self.root)
        children.reverse()

        for child in children:
            self.convert_joint(child)

        cmds.polyUnite(self.all_geo, n=self.NAME, ch=False)

    def convert_joint(self, joint):
        parent = dag.get_parent(joint)
        sphere = cmds.polySphere(r=self.joint_radius, sa=12, sh=6, ch=False)[0]
        transform.align_transform(joint, sphere)
        self.all_geo.append(sphere)
        if not parent:
            return

        distance = vector.get_distance(source=joint, target=parent[0])
        height = distance - self.joint_radius * 2

        cone = cmds.polyCone(r=self.middle_radius, sa=4, h=height, ch=False)[0]
        cmds.delete(cmds.pointConstraint([joint, parent[0]], cone, mo=False))
        cmds.delete(cmds.aimConstraint(joint, cone, mo=False, aim=(0, 1, 0), u=(1, 0, 0), wuo=parent[0]))

        self.all_geo.append(cone)
