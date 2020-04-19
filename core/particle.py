import pymel.core as pm

def create_goal(obj, base_name, prefix=None, w=0.5):
    """ create particle and apply goal

    :param obj: str(obj)
    :param base_name: str(base_name) name of main object
    :param w: weight goal
    :return: locator, particle
    """
    if prefix:
        base_name = '{}_{}'.format(base_name, prefix)
    pos = obj.getTranslation(space="world")
    if not pm.objExists('{}_particle'.format(base_name)):
        particle = pm.particle(p=[0, 0, 0], n='{}_particle'.format(base_name))[0]
        pm.xform(particle, t=pos)
        particle.particleRenderType.set(4)
        pm.goal(particle, g=obj, w=w)
        if not pm.objExists('{}_goal_transform'.format(base_name)):
            goal_transform = pm.spaceLocator(n='{}_goal_transform'.format(base_name))
            particle.worldCentroid.connect(goal_transform.t)
            return [goal_transform, particle]
        else:
            print '{}_goal_transform already_exists'.format(base_name)
    else:
        print '{}_particle already exists'.format(base_name)

