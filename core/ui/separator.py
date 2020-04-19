import pymel.core as pm


class Separator(object):
    def __init__(self, label, parent, w, h):
        self.label = label
        self.parent = parent
        self.width = w
        self.height = h
        self.create_separator()

    def create_separator(self):
        with pm.horizontalLayout(p=self.parent, w=self.width, h=self.height) as layout:
            pm.separator()
            pm.text(self.label)
            pm.separator()
        return layout
