# MayaTools
 tools for pipeline

# DOCS for code writing

- Way to import module
```python
import MayaTools.utils.connections
import MayaTools.utils.dag

```

- Way to call method
```python
import sys
sys.path.append(r'E:\Work\Pipeline\Projects')
import MayaTools.fit_pose.fit_ui
reload(MayaTools.fit_pose.fit_ui)
MayaTools.fit_pose.fit_ui.FitUI()

# add namespace
import MayaTools.fit_pose.fit_ui as ui
reload(ui)
ui.fit_ui.FitUI()

```
- ### Minimum dependencies in module utils
    - ##### Import only important method or difficult
        - ##### Import only needed method
```python
# Wrong
import MayaTools.utils.connections
import MayaTools.utils.dag
import MayaTools.utils.shapes
import MayaTools.utils.base
import ...

# Right ()
import MayaTools.utils.constraint.restore_constraint

```
- ### Utility modules use only Maya standard functions
```python
# Wrong
def get_parent(obj):
    return obj.getParent()

# Right
def get_parent(obj):
    return pm.listRelatives(obj, p=True)
```
- ### Use only pymel because cmds not working with pymel object
```python
import pymel.core as pm
import maya.cmds as cmds
sel_pm = pm.selected()[0]
cmds.group(sel_pm)

# Error: TypeError: Object 'sel_pm' is invalid # 
```

- ### Give full names
```python
# Wrong
sel = pm.selected()
con = pm.listConnections()

# Right
selection = pm.selected()
connections = pm.listConnections()
```

- ### PEP8
| Type | Public | Internal |
| :--- | :--- | :--- |
| Packages | `lower_with_under` |  |
| Modules | `lower_with_under` | `_lower_with_under` |
| Classes | `CapWords` | `_CapWords` |
| Exceptions | `CapWords` |  |
| Functions | `lower_with_under()` | `_lower_with_under()` |
| Global/Class Constants | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| Global/Class Variables | `lower_with_under` | `_lower_with_under` |
| Instance Variables | `lower_with_under` | `_lower_with_under` |
| Method Names | `lower_with_under()` | `_lower_with_under()` |
| Function/Method Parameters | `lower_with_under` |  |
| Local Variables | `lower_with_under` |  |
