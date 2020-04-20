import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.dag as dag


class SwapNode(object):
    def __init__(self, source, target, parentChild=True, parent=True, pass_type=None):
        self.source = source
        self.target = target
        self.parent_child = parentChild
        self.parent = parent
        self.pass_type = pass_type

        if self.check_match():
            self.swap_connect()

            if self.parent:
                try:
                    self.change_parent()
                except Exception as error:
                    print error

            if self.parent_child:
                self.move_child()

    def check_match(self):
        if pm.nodeType(self.source) == pm.nodeType(self.target):
            return True
        else:
            om.MGlobal.displayError('Different types of nodes')
            return False

    def filter_nodes(self, nodes):
        filtered = []
        for node in nodes:
            type = pm.nodeType(node)
            if type not in self.pass_type:
                if type == 'transform':
                    all_child = dag.get_children(node)
                    if all_child:
                        for child in all_child:
                            if not pm.nodeType(child) in self.pass_type:
                                filtered.append(node)
                else:
                    filtered.append(node)
        return filtered

    def change_parent(self):
        parent_source = self.source.getParent()
        parent_target = self.target.getParent()
        if parent_source:
            pm.parent(self.target, parent_source)
        else:
            pm.parent(self.target, w=True)
        if parent_target:
            pm.parent(self.source, parent_target)
        else:
            pm.parent(self.source, w=True)

    def move_child(self):
        child = dag.get_children(self.source)
        if child:
            filter_child = self.filter_nodes(child)
            if filter_child:
                pm.parent(self.filter_nodes(child), self.target)

    def swap_connect(self):
        out_con = self.source.outputs(c=True, p=True)
        in_con = self.source.inputs(c=True, p=True)

        if out_con:
            for con in out_con:
                try:
                    pm.disconnectAttr(con[0], con[1])
                except Exception as error:
                    print error

                try:
                    pm.connectAttr('{}.{}'.format(self.target, con[0].split('.')[1]), con[1])
                except Exception as error:
                    print error

        if in_con:
            for con in in_con:
                try:
                    pm.disconnectAttr(con[1], con[0])
                except Exception as error:
                    print error

                try:
                    pm.connectAttr(con[1], '{}.{}'.format(self.target, con[0].split('.')[1]))
                except Exception as error:
                    print error


class SwapNodeController(object):
    def __init__(self, source=None, target=None,
                 parentChild=True, parent=True,
                 hierarchy=False, pass_type=None):
        self.source = source
        self.target = target
        self.parent_child = parentChild
        self.parent = parent
        self.hierarchy = hierarchy
        self.pass_type = pass_type

        self.selection_type = None

        self.run()

    def run(self):
        if self.hierarchy:
            self.swap_hierarchy()
        else:
            self.swap_node()

    def get_selection(self):
        sel = pm.selected()
        if not sel:
            om.MGlobal.displayError('Nothing selected')
            return

        if not len(sel) == 2:
            om.MGlobal.displayError('Selected not 2 objects')
            return

        # initialize type selection node
        self.selection_type = pm.nodeType(sel[0])
        if not self.pass_type:
            self.pass_type = [self.selection_type]

        return sel

    def swap_node(self):
        selected = self.get_selection()
        if selected:
            SwapNode(selected[0], selected[1], parent=self.parent, parentChild=self.parent_child,
                     pass_type=self.pass_type)

    def get_hierarchy(self, obj):
        hierarchy = [x for x in obj.getChildren(ad=True) if pm.nodeType(x) == self.selection_type]
        hierarchy.append(obj)
        return hierarchy

    def swap_hierarchy(self):
        sel = self.get_selection()
        if sel:
            all_source = self.get_hierarchy(sel[0])
            all_target = self.get_hierarchy(sel[1])

            if len(all_source) == len(all_target):
                for src, trg in zip(all_source, all_target):
                    SwapNode(src, trg, parentChild=self.parent_child, parent=False, pass_type=self.pass_type)
            else:
                om.MGlobal.displayError('Hierarchies are not equal')
