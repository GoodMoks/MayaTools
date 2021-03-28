import random
import pymel.core as pm


class RandomKey_UI(object):
    def __init__(self):
        self.win_name = 'random_key'
        self.curves = None
        self.value = 10
        self.time = 10
        self.space_value = None
        self.space_time = 2
        self.window()

    @staticmethod
    def get_curve():
        curve = pm.keyframe(pm.selected()[0], sl=True, n=True, q=True)
        if pm.keyframe(curve, keyframeCount=True, q=True) >= 2:
            return curve

    def update_var(self):
        self.time = pm.intFieldGrp(self.time_fld, q=True, v=True)[0]
        self.value = pm.intFieldGrp(self.value_fld, q=True, v=True)[0]
        self.space_time = pm.intFieldGrp(self.time_space_fld, q=True, v=True)[0]
        self.space_value = pm.intFieldGrp(self.value_space_fld, q=True, v=True)[0]

    def random(self, *args):
        curves = self.get_curve()
        self.update_var()
        if curves:
            keys = []
            for curve in curves:
                key = RandomKey(curve=curve, value=self.value,
                                time=self.time, space_value=self.space_value,
                                space_time=self.space_time)
                keys.append(key)
            self.curves = keys

    def check_max_time(self, *args):
        space = args[0]
        time = pm.intFieldGrp(self.time_fld, q=True, v=True)[0]
        if space > time:
            pm.intFieldGrp(self.time_space_fld, e=True, v1=int(time))

    def check_max_value(self, *args):
        space = args[0]
        value = pm.intFieldGrp(self.value_fld, q=True, v=True)[0]
        if space > value:
            pm.intFieldGrp(self.value_space_fld, e=True, v1=int(value))

    def window(self):
        if pm.window(self.win_name, exists=True):
            pm.deleteUI(self.win_name)

        with pm.window(self.win_name, s=True, title='Random Key'):
            with pm.verticalLayout():
                with pm.horizontalLayout():
                    with pm.verticalLayout():
                        pm.text('Time')
                        self.time_fld = pm.intFieldGrp(nf=1, l='Time', value1=10, cw=(1, 30))
                        self.time_space_fld = pm.intFieldGrp(nf=1, l='Space', value1=2, cw=(1, 30),
                                                             )
                    with pm.verticalLayout():
                        pm.text('Value')
                        self.value_fld = pm.intFieldGrp(nf=1, l='Value', value1=10, cw=(1, 30))
                        self.value_space_fld = pm.intFieldGrp(nf=1, l='Space', value1=0, cw=(1, 30),
                                                              cc=self.check_max_value)
                with pm.verticalLayout():
                    pm.button('Random', c=self.random)



class RandomKey(object):
    def __init__(self, curve=None,
                 value=10, time=10,
                 space_value=None, space_time=2):
        self.curve = curve
        self.value = value
        self.time = time
        self.space_value = space_value
        self.space_time = space_time

        self.values = None

        self.edit_curve()

    @staticmethod
    def set_key(curve, keys):
        for time, value in keys:
            pm.setKeyframe(curve, v=value, t=time)

    def get_random_time(self, low, high, space=2):
        value = random.randint(low, high)
        if abs(value - low) >= space:
            return value
        else:
            return self.get_random_time(low, high, space)

    def get_time(self):
        prev = self.start
        for v in range(int(self.start), int(self.end), self.time)[1:]:
            yield self.get_random_time(prev, v, space=self.space_time)
            prev = v

    def get_value(self, time, space):
        prev = 0
        for t in time:
            value = random.uniform(-self.value, self.value)
            if space:

                while abs(prev - value) >= space:
                    value = random.uniform(-self.value, self.value)
                else:
                    prev = value
                    yield [t, value]
            else:
                yield [t, value]

    def edit_curve(self):
        if self.curve:
            self.start = pm.keyframe(self.curve, q=True)[0]
            self.end = pm.keyframe(self.curve, q=True)[-1]
            self.values = list(self.get_value(self.get_time(), space=self.space_value))
            self.set_key(self.curve, self.values)
