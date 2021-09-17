import maya.cmds as cmds


class LeechesDynamic(object):
    @staticmethod
    def get_constraint(obj):
        out_con = cmds.listConnections(obj, d=True, p=False, t='parentConstraint')
        if not out_con:
            return None
        return out_con[0]

    @staticmethod
    def apply_constraint(constraint, obj):

        try:
            cmds.connectAttr('{}.constraintRotate'.format(constraint), '{}.rotate'.format(obj), f=True)
            cmds.connectAttr('{}.constraintTranslate'.format(constraint), '{}.translate'.format(obj), f=True)
        except:
            pass

    @staticmethod
    def disconnect_control(constraint, obj):
        try:
            cmds.disconnectAttr('{}.constraintRotate'.format(constraint), '{}.rotate'.format(obj))
            cmds.disconnectAttr('{}.constraintTranslate'.format(constraint), '{}.translate'.format(obj))
        except:
            pass

    def __init__(self, namespace=''):
        self.namespace = namespace + ':' if namespace else namespace
        self.l_leeches = ['{}L_Leeches_0{}_IK_CTRL'.format(self.namespace, x) for x in range(1, 10)]
        self.r_leeches = ['{}R_Leeches_0{}_IK_CTRL'.format(self.namespace, x) for x in range(1, 10)]
        self.all_controls = self.l_leeches + self.r_leeches

    def apply(self):
        for control in self.all_controls:
            constraint = self.get_constraint(control)
            self.apply_constraint(constraint=constraint, obj=control)

    def disconnect(self):
        for control in self.all_controls:
            constraint = self.get_constraint(control)
            self.disconnect_control(constraint=constraint, obj=control)

    def selected_connections(self, disconnect=False):
        sel = cmds.ls(sl=True)
        if not sel:
            return None

        cmds.undoInfo(openChunk=True)
        for s in sel:
            if s in self.all_controls:
                constraint = self.get_constraint(s)
                if disconnect:
                    self.disconnect_control(constraint=constraint, obj=s)
                else:
                    self.apply_constraint(constraint=constraint, obj=s)
        cmds.undoInfo(closeChunk=True)

    def apply_selected(self):
        self.selected_connections()

    def disconnect_selected(self):
        self.selected_connections(disconnect=True)
