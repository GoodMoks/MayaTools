import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om2
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui



class ProxyAttrUI(QtWidgets.QDialog):
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self, parent=MAYA):
        super(ProxyAttrUI, self).__init__(parent)

        self.setWindowTitle('Proxy Attribute Manager')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setBaseSize(400, 250)

        self.create_layout()
        self.create_widgets()
        self.add_to_layout()
        self.make_connections()

        #self.fill_proxy_attr_list()

    def create_layout(self):
        self.main_v_ly = QtWidgets.QVBoxLayout(self)
        self.objects_v_ly = QtWidgets.QVBoxLayout()
        self.attr_v_ly = QtWidgets.QVBoxLayout()


    def create_widgets(self):
        self.list_wdg = QtWidgets.QListWidget()
        self.tab_wdg = QtWidgets.QTabWidget(self)

        self.objects_list_wdg = QtWidgets.QListWidget()
        self.attr_list_wdg = QtWidgets.QListWidget()

        self.object_btn = QtWidgets.QPushButton('Object')
        self.attr_btn = QtWidgets.QPushButton('Attr')

        self.object_tab_wdg = QtWidgets.QWidget()
        self.attr_tab_wdg = QtWidgets.QWidget()



    def add_to_layout(self):
        self.main_v_ly.addWidget(self.tab_wdg)
        self.objects_v_ly.addWidget(self.objects_list_wdg)
        self.objects_v_ly.addWidget(self.object_btn)

        self.attr_v_ly.addWidget(self.attr_list_wdg)
        self.attr_v_ly.addWidget(self.attr_btn)

        self.object_tab_wdg.setLayout(self.objects_v_ly)
        self.attr_tab_wdg.setLayout(self.attr_v_ly)
        self.tab_wdg.addTab(self.object_tab_wdg, 'Objects')
        self.tab_wdg.addTab(self.attr_tab_wdg, 'Attr')

        #self.main_v_ly.addWidget(self.add_attr_btn)

    def add_attribute(self):
        print 'add attribute'
        result = mel.eval('dynAddAttrWin( {} )')
        print result, 'result'

    def make_connections(self):
        self.attr_btn.clicked.connect(self.add_attribute)

    def fill_proxy_attr_list(self):
        proxies = get_all_proxy_attr()
        print proxies
        for obj, attr in proxies.iteritems():
            # clean_object = obj.split('|')[-1]
            item = QtWidgets.QListWidgetItem(attr)
            self.list_proxy_attrs.addItem(item)

    def fill_list_wdg(self):
        proxies = get_all_proxy_attr()
        for obj, attr in proxies.iteritems():
            clean_object = obj.split('|')[-1]
            item = QtWidgets.QListWidgetItem(clean_object)
            self.list_wdg.addItem(item)

def showUI():
    try:
        proxy.close()  # pylint: disable=E0601
        proxy.deleteLater()
    except:
        pass

    proxy = ProxyAttrUI()
    proxy.show()


def add_proxy_attr(obj, attr, proxy_attr):
    cmds.addAttr(obj, ln=attr, pxy=proxy_attr)


def get_all_proxy_attr():
    """ get objects who has given attr

    :param obj_type: 'om2.MFn.kLocator'
    :param attr: 'str' name of attr
    :return: 'list' with objects
    """
    proxies = {}
    iterDag = om2.MItDag(om2.MItDag.kDepthFirst)
    while not iterDag.isDone():
        m_object = iterDag.currentItem()
        dep_obj = om2.MFnDependencyNode(m_object)
        count = dep_obj.attributeCount()
        for index in xrange(count):
            attr = dep_obj.attribute(index)
            fn_attr = om2.MFnAttribute(attr)
            if fn_attr.isProxyAttribute:
                attrs = proxies.get(iterDag.fullPathName(), list())
                attrs.append(fn_attr.name)
                proxies[iterDag.fullPathName()] = attrs

        iterDag.next()
    return proxies
