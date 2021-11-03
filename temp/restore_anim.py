import pymel.core as pm
import maya.cmds as cmds


def get_all_animCurve():
    all_curve = cmds.ls(et='animCurve')
    print(all_curve)


def build():
    all_curve = cmds.ls(type='animCurveTA')
    if not all_curve:
        return
    for curve in all_curve:
        separate = curve.split('_')
        for index in range(len(separate)):
            reverse = (len(separate) - index) - 1
            objs = separate[:reverse]
            if cmds.objExists('_'.join(objs)):
                obj = '_'.join(objs)
                channel = separate[-1:]
                connect = cmds.listConnections(('{}.output'.format(curve)))
                if connect and connect[0] == obj:
                    break

                if connect and cmds.objectType(connect[0]) == 'pairBlend':
                    print(connect)


def start():
    all_curve = cmds.ls(type='animCurve')
    if not all_curve:
        return
    for curve in all_curve:
        connect = ConnectCurve(curve)
        # print(connect.curve)
        # print(connect.obj)
        # print(connect.channel)


class ConnectCurve(object):
    def __init__(self, curve, namespace='Samurai_Female_Rig'):
        self.curve = curve
        self.namespace = namespace
        self.obj = None
        self.channel = None
        self.start()

    def start(self):
        self.get_obj_from_curve()
        connection = cmds.listConnections(('{}.output'.format(self.curve)))
        print(self.curve)
        print(self.obj)
        print(connection)
        if connection:
            if cmds.objectType(connection[0]) == 'pairBlend':
                try:
                    cmds.connectAttr('{}.outRotate'.format(connection[0]), '{}.rotate'.format(self.obj, self.channel))
                    cmds.connectAttr('{}.outTranslate'.format(connection[0]), '{}.translate'.format(self.obj, self.channel))
                except Exception as e:
                    print(e)
                    pass
        else:
            try:
                cmds.connectAttr('{}.output'.format(self.curve), '{}.{}'.format(self.obj, self.channel))
            except:
                pass

    def get_obj_from_curve(self):
        separate = self.curve.split('_')
        channel = separate[-1:]
        for index in range(len(separate)):
            reverse = (len(separate) - index) - 1
            objs = separate[:reverse]
            obj = '_'.join(objs)
            if self.namespace:
                obj = '{}:{}'.format(self.namespace, obj)
            if cmds.objExists(obj):
                self.channel = ''.join([x for x in separate if x not in objs])
                self.obj = obj
                break


class RestoreAnimationRef(object):
    def __init__(self, namespace):
        self.namespace = namespace

        print('RESTORE')

        self.start()

    def get_obj_from_curve(self, curve):
        separate = curve.split('_')
        channel = separate[-1:]
        for index in range(len(separate)):
            reverse = (len(separate) - index) - 1
            objs = separate[:reverse]
            obj = '_'.join(objs)
            if cmds.objExists(obj):
                return obj, channel

    def start(self):
        all_curve = cmds.ls(type='animCurveTA')
        if not all_curve:
            return

        for curve in all_curve:
            obj, channel = self.get_obj_from_curve(curve)







