import maya.cmds as cmds
import pymel.core as pm


"""
Задача:
Сдлать едитор для откатывания изменений в референсе
"""

""" Reference Edit: disconnectAttr "skinCluster3.outputGeometry[0]" "mesh_612Shape.inMesh """

ref = pm.PyNode('Samurai_Female_RigRN')

nodes = pm.referenceQuery(ref, onReferenceNode='disconnectAttr', en=True)
#pm.referenceEdit(ref, successfulEdits=True, removeEdits=True, editCommand='disconnectAttr')
