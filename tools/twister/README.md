# To Do 
- Выбор второступенной оси
- Мульти атрибуты на выделенные объекты
- Загрузка и выгрузка пресетов
- Стретч окна
- Большой listWidget
- Комбайн влияния Point системы на твист

# RUN
```python
# develop UI
import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
import MayaTools.tools.twister.twister_ui as ui
reload(ui)
ui.showUI_dev()
```
```python
# user UI
import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
from MayaTools.tools.twister.twister_ui import TwisterUI
TwisterUI.showUI()
```