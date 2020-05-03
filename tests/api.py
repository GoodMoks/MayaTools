import maya.api.OpenMaya as om2
import maya.OpenMaya as om
from MayaTools.core.utils import time_info


def get_MObject(object):
    """ get MObject for given object

    :param object: 'str' object
    :return: MObject
    """
    selectionList = om2.MGlobal.getSelectionListByName(object)
    return selectionList.getDependNode(0)


@time_info
def api_iter(objects):
    for obj in objects:
        sel_list = om.MSelectionList()
        sel_list.add(obj)
        m_obj = om.MObject()
        sel_list.getDependNode(0, m_obj)

        fn_obj = om.MFnDependencyNode()
        fn_obj.setObject(m_obj)
        vis_attr = fn_obj.findPlug('visibility')
        print vis_attr.name()
        plug = om.MPlug()
        #fn_attr = om.MFnAttribute()
        #fn_attr.setObject(vis_attr)

        #fn_attr.setKeyable(0)
        #fn_attr.setWritable(1)
        #fn_attr.setReadable(0)
    # for index in xrange(sel_list.length()):
    #     m_obj = sel_list.getDependNode(index)
    #     fn_attr = om2.MFnDependencyNode(m_obj)
    #     type = fn_attr.attributeCount()
    #     print type

        # m_sel = om2.MSelectionList()
        # m_sel.add(attr)
        #
        #
        # print m_sel.getDagPath(0)
        # m_fn.n



def api_unlock():
    pass