import pymel.core as pm
import swap_node



class SwapNodeUI(object):
    def __init__(self):
        self.parent_state = True
        self.show()

    def set_parent_state(self, *args):
        self.parent_state = args[0]

    def check(self, *args):
        self.parent_cb.setEnable(not args[0])
        if args[0]:
            self.parent_cb.setValue(not args[0])
        else:
            self.parent_cb.setValue(self.parent_state)

    def split_pass_obj(self, text):
        if text:
            if ',' in text:
                objs = []
                for obj in text.split(','):
                    objs.append(obj.strip())
                return objs
            else:
                return [text]

    def run(self, *args):
        # get value from check box
        parent = self.parent_cb.getValue()
        child = self.child_cb.getValue()
        hierarchy = self.hierarchy_cb.getValue()

        # pass obj for hierarchy
        pass_obj = self.pass_obj_line.getText()
        pass_obj_split = self.split_pass_obj(pass_obj)

        swap_node.SwapNodeController(parent=parent, parentChild=child,
                        hierarchy=hierarchy, pass_type=pass_obj_split)

    def show(self):
        window = 'SwapNode'

        if pm.window(window, exists=True):
            pm.deleteUI(window)

        with pm.window(window, s=True, w=200, h=100) as win:
            with pm.autoLayout():
                with pm.autoLayout():
                    pm.text('Swap Connections')
                    pm.text('Select SOURCE and select TARGET')
                with pm.horizontalLayout(bgc=[0.24, 0.24, 0.24]):
                    self.parent_cb = pm.checkBox(label='Parent', cc=lambda x: self.set_parent_state(x), value=True)
                    self.child_cb = pm.checkBox(label='Child', bgc=[0.24, 0.24, 0.24], value=True)
                    self.hierarchy_cb = pm.checkBox(label='Hierarchy', bgc=[0.24, 0.24, 0.24], cc=lambda x: self.check(x))
                self.pass_obj_line = pm.textField(pht='Skip children: joint, mesh, ...')
                pm.button(label='SWAP', c=self.run)
