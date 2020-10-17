import re
import maya.cmds as cmds

"""
modules for naming
"""

def addNumber(name):
    """ Adds count number to line end

    :param name: 'str' name of object
    :return: 'str' New name with number at the end
    """
    number = 0
    exist = False
    while exist == False:
        if re.findall('\d$', name):
            nameBase, number, empty = re.split(r'(\d+)$', name)
            number = int(number)
        else:
            nameBase = name

        number += 1
        if nameBase.endswith('_'):
            newName = nameBase + '{}'.format(number)
        else:
            newName = nameBase + '_{}'.format(number)

        if not cmds.objExists(newName):
            exist = True
            return newName


def defaultPrefix(name):
    """ Deletes the prefix at the end of the line

    :param name: 'str' name of object
    :return: 'str' name without prefix and underscore
    """
    if not name:
        return []

    # Default prefix
    prefixList = ['Jnt', 'jnt', 'JNT', 'ctrl', 'Ctrl', 'CTRL', 'loc', 'Loc', 'LOC',
                  'IK', 'ik', 'Ik', 'grp', 'Grp', 'GRP']

    # Remove All ends prefix
    definePrefix = [x for x in prefixList if name.endswith(x)]

    # Delete prefix
    if definePrefix:
        name = re.sub('{}$'.format(definePrefix[0]), '', name)

    # Delete undescore at the line
    if name.endswith('_'):
        name = re.sub('_$', '', name)

    return name


def renamePrefix(name=None, prefix='', underscore=True):
    """ Add prefix and count number

    :param name: 'str' name of object
    :param prefix: 'str' prefix
    :param underscore: 'bool' add underscore or not
    :return: 'str' New name
    """
    if name:
        nameSplit = name.split('.')[0]
        name = defaultPrefix(nameSplit)

        if underscore:
            newName = name + '_{}'.format(prefix)
        else:
            newName = name + '{}'.format(prefix)

        if cmds.objExists(newName):
            newName = addNumber(newName)

        return newName


class CopyFace(object):
    def __init__(self):
        self.sourceFace = []
        self.proxyFace = []
        self.sourceMesh = []
        self.proxyMesh = []
        self.sourceVertex = []
        self.proxyVertex = []

    def flattenList(self, obj=None):
        """ Decomposes the components

        :param obj: 'list'
        :return: 'generator'
        """
        if obj:
            if isinstance(obj, basestring):
                obj = [obj]

        if obj:
            for l in obj:
                listFlat = cmds.ls(l, fl=True)
                for item in listFlat:
                    if isinstance(item, list):
                        for i in item:
                            yield i
                    else:
                        yield item

    def getVert(self, face=None):
        """ Convert face to vertices

        :param face: 'list' list of the faces
        :param var: 'string' name of the global variables
        """

        if face:
            # get all vertices from face
            vertex = cmds.polyListComponentConversion(face, tv=True)
            flVertex = list(self.flattenList(vertex))
            if flVertex:
                return flVertex

    def getFace(self, obj=None):
        """ Get all faces from mesh

        :param obj: 'string' name of poly objects
        :return: 'list' list of faces
        """
        if obj:
            if isinstance(obj, basestring):
                faces = cmds.polyListComponentConversion(obj, tf=True)
                flFaces = list(self.flattenList(faces))
                if flFaces:
                    return flFaces

    def splitName(self, obj):
        """ Split name vertex

        :param obj: 'list' list of vertices or obj
        :return: 'generator'
        """
        if obj:
            if isinstance(obj, basestring):
                obj = [obj]

        if obj:
            for l in obj:
                name = l.split('.')[1]
                yield str(name)

    def unlockAttr(self, obj=None, attrList=None):
        """ Unlock attribute

        :param obj: 'list'
        :param attrList: 'list'
        """
        if not obj:
            self.ls = cmds.ls(sl=True, fl=True)
            obj = self.ls

        if obj:
            if isinstance(obj, basestring):
                obj = [obj]
            if not attrList:
                attrList = ['.tx', '.ty', '.tz',
                            '.rx', '.ry', '.rz',
                            '.sx', '.sy', '.sz',
                            '.visibility']
            for o in obj:
                for attr in attrList:
                    fullAttr = o + attr
                    try:
                        cmds.setAttr(fullAttr, l=False, k=True)
                    except:
                        pass

    def centerFace(self, face=None):
        """ Finds the center position of the face

        :param face: 'string' face name
        :return: 'list' list of coordinates
        """
        if face:
            pos = cmds.xform(face, q=True, ws=True, bb=True)
            if pos:
                tx = round((pos[0] + pos[3]) / 2, 3)
                ty = round((pos[1] + pos[4]) / 2, 3)
                tz = round((pos[2] + pos[5]) / 2, 3)
                pos = [tx, ty, tz]
                return pos

    def posFace(self, face=None):
        """ Generator for get position of the faces

        :param face:
        :return:
        """
        if face:
            for f in face:
                pos = self.centerFace(f)
                yield pos

    def compareFaces(self, face=None, compare=True, target=None):
        """ Generator for compare faces

        :param face: 'list' list of faces
        :param compare: 'bool' return settings
        :param target: 'list' faces
        :return:
        """

        if face:
            if isinstance(face, basestring):
                face = [face]

            if target:
                # target faces
                trgList = list(self.posFace(target))

                for f in face:
                    facePos = self.centerFace(f)

                    # return face for delete
                    if compare == True:
                        if facePos not in trgList:
                            yield f
                    # return face for update vtx variables
                    if compare == False:
                        if facePos in trgList:
                            yield f

    def face_to_vtx(self, source=None, proxy=None):
        """ Converts faces to vertexes

        :param source: 'list' source faces
        :param proxy: 'list' proxy faces
        :return: None
        """
        if source and proxy:
            self.sourceVertex = cmds.polyListComponentConversion(source, tv=True)
            self.proxyVertex = cmds.polyListComponentConversion(proxy, tv=True)

    def duplicateFace(self):
        """ Duplicate faces """

        sel = cmds.ls(sl=True)

        try:
            isFace = sel[0].split('.f')[1]
            if isFace:
                self.sourceFace = list(self.flattenList(sel))
        except:
            cmds.confirmDialog(title='Error', message='Select only polygon faces',
                               button=['OK'])
            return False

        if self.sourceFace:
            # Gets name of source obj
            sourceObjName = self.sourceFace[0].split('.')[0]
            self.sourceMesh = sourceObjName

            # Create New name for duplicate object
            newName = renamePrefix(name=sourceObjName, prefix='proxy')

            # Duplicate obj and set name of duplicate mesh
            self.proxyMesh = cmds.duplicate(sourceObjName, n=newName)[0]

            # Get all faces from duplicate obj
            self.proxyFace = self.getFace(self.proxyMesh)

            # Gets faces to delete
            delFaces = list(self.compareFaces(self.proxyFace, compare=True, target=self.sourceFace))

            cmds.select(delFaces)
            listDel = cmds.ls(sl=True)

            if listDel:
                cmds.delete(listDel)

            self.unlockAttr(self.proxyMesh)
            cmds.select(self.proxyMesh)

            self.face_to_vtx(self.sourceFace, self.proxyFace)

            return True

    def updateMesh(self, source_mesh=None, dupl_mesh=None):
        """ Updates source vertexes

        :param source_mesh: 'str' name of source obj
        :param dupl_mesh: 'str' name of proxy obj
        :return: None
        """
        if not dupl_mesh:
            dupl_mesh = self.proxyMesh
        if not source_mesh:
            source_mesh = self.sourceMesh

        if dupl_mesh and source_mesh:
            self.sourceFace = self.getFace(source_mesh)
            self.proxyFace = self.getFace(dupl_mesh)

            sourceUpdFace = list(self.compareFaces(self.sourceFace,
                                                   compare=False,
                                                   target=self.proxyFace))

            if sourceUpdFace:
                self.face_to_vtx(sourceUpdFace, self.proxyFace)


class Skin(object):
    def __init__(self):
        self.joints = []

    def getSkinCluster(self, node=None):
        """ Gets skinCluster from object

        :param node:
        :return:
        """
        if node:
            if isinstance(node, basestring):
                skinCluster = self.history(node, type='skinCluster')
                if skinCluster:
                    return skinCluster

    def infJoints(self, node=None):
        if node:
            if isinstance(node, basestring):
                skinCluster = self.history(node, type='joint')
                if skinCluster:
                    return skinCluster

    def compareInf(self, src, trg):
        srcObj = src.split('.')[0]
        trgObj = trg.split('.')[0]

        if self.getSkinCluster(srcObj):
            if self.getSkinCluster(trgObj):
                if self.infJoints(srcObj) == self.infJoints(trgObj):
                    return True
                else:
                    return False
            else:
                cmds.confirmDialog(title='Error', message='{} since it is not a skinned object'.format(trgObj),
                                   button=['OK'])
        else:
            cmds.confirmDialog(title='Error', message='{} since it is not a skinned object'.format(srcObj),
                               button=['OK'])

    def copySkin(self, src=None, trg=None):
        if src and trg:
            cmds.select(src, trg)

        if self.compareInf(src[0], trg[0]):
            cmds.copySkinWeights(noMirror=True,
                                 surfaceAssociation='closestPoint',
                                 influenceAssociation='oneToOne',
                                 normalize=True)

    def history(self, node, type=None):
        if node:
            history = cmds.listHistory(node)
            if not type:
                return history

            history = [n for n in history if cmds.nodeType(n) == type]

            if history:
                return history

    def addSkin(self, src, trg):
        joints = self.infJoints(src)
        historySource = self.getSkinCluster(src)
        historyProxy = self.getSkinCluster(trg)

        if historyProxy:
            skincluster = historyProxy[0]
            for joint in joints:
                try:
                    cmds.skinCluster(skincluster, edit=True, lw=True, ai=joint)
                except:
                    pass
            return True

        elif historySource:
            skincluster = cmds.skinCluster(*(joints + [trg]), tsb=True)
            return True

        else:
            return False

    def dropoffSkin(self, node=None, rate=5, skinCluster=None):
        if not node:
            node = cmds.ls(sl=True)
        if node:
            if isinstance(node, basestring):
                node = [node]
            for obj in node:
                joints = self.infJoints(obj)

                if not skinCluster:
                    skinCluster = self.getSkinCluster(obj)

                if joints and not skinCluster:
                    for joint in joints:
                        try:
                            cmds.skinCluster(skinCluster, e=True, inf=joint, dr=rate)
                        except:
                            pass


class Window():
    def __init__(self):
        self.window()

    def window(self):
        windowName = 'proxySkin'
        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName)

        cmds.window(windowName, t="Proxy Skin UI", sizeable=False)
        mainLayout = cmds.columnLayout()
        cmds.separator(height=5, style='in')
        cmds.text(l='1. Select face for duplicate',
                  w=300, align='center')
        cmds.separator()
        cmds.text(l='2. Press DUPLICATE and change the skin',
                  w=300, align='center')
        cmds.separator()
        cmds.text(l='3. Select sourse then select destination object',
                  w=300, align='center')
        cmds.separator()
        cmds.text(l='4. Press COPY to transfer skin',
                  w=300, align='center')
        cmds.separator()
        cmds.rowLayout(numberOfColumns=2)

        self.dupl_btn = cmds.button(label='DUPLICATE',
                                    w=150, h=50, c=self.duplicate_face)
        self.copy_btn = cmds.button(label='COPY', w=150, h=50, c=self.copy_skin)

        cmds.showWindow(windowName)

    def duplicate_face(self, *args):
        face = CopyFace()
        duplicate = face.duplicateFace()
        if duplicate:
            skin = Skin()
            newSkin = skin.addSkin(face.sourceMesh, face.proxyMesh)
            if newSkin:
                skin.copySkin(face.sourceVertex, face.proxyVertex)
                cmds.select(face.proxyMesh)
                self.sourceObject = face.proxyMesh

    def checkSelect(self, select=None):
        if select:
            try:
                vtx = select[0].split('.vtx')[1]
                return vtx
            except:
                pass
            try:
                face = select[0].split('.f')[1]
                return face
            except:
                pass

    def copy_skin(self, *args):
        sel = cmds.ls(sl=True, fl=True)
        if not self.checkSelect(sel):
            if len(sel) == 2:
                face = CopyFace()
                face.updateMesh(sel[1], sel[0])
                skin = Skin()
                skin.copySkin(face.proxyVertex, face.sourceVertex)
                cmds.select(sel[1])
            else:
                cmds.confirmDialog(title='Error', message='Please select two objects, source and target',
                                   button=['OK'])
        else:
            cmds.confirmDialog(title='Error', message='Select only polygon objects',
                               button=['OK'])
