import pymel.core as pm

class Instance:
    def __init__(self, obj, instance):
        self.obj = obj
        self.instance = instance
        self.add_instance()

    def add_instance(self):
        obj_instance = pm.instance(self.instance)[0]
        obj_instance.getShape().setParent(self.obj, r=True)
        pm.delete(obj_instance)
        return True

    def get_instance(self):
        return self.instance


class InstanceShape:
    MAIN_INST_NAME = 'main_instance'
    ATTR_NAME = 'Instance'

    def __init__(self, objects, shape_name, shape_vis=False):
        self.objects = objects
        self.shape_name = shape_name
        self.shape_vis = shape_vis

        if not isinstance(self.objects, list):
            self.objects = list(self.objects)

        if pm.objExists(self.shape_name):
            om.MGlobal.displayError('Shape "{}" already exist'.format(self.shape_name))
            return

        self.create_main_instance()
        self.add_instance()
        self.add_instance_attr()
        self.hide_attr()

        try:
            pm.delete(self.MAIN_INST_NAME)
        except:
            pass

    def create_main_instance(self):
        self.instance_obj = pm.spaceLocator(n=self.MAIN_INST_NAME)
        self.instance_obj.getShape().visibility.set(self.shape_vis)
        pm.rename(self.instance_obj.getShape(), self.shape_name)

    def add_instance_attr(self):
        pm.addAttr(self.shape_name, ln=self.ATTR_NAME, dt="string")

    def add_instance(self):
        for obj in self.objects:
            Instance(obj, self.instance_obj)

    def get_available_attributes(self, obj):
        return pm.listAttr(obj, cb=True)

    def hide_attr(self):
        for attr in self.get_available_attributes(self.shape_name):
            pm.setAttr('{}.{}'.format(self.shape_name, attr), keyable=False, cb=False)
