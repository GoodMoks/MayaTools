import sys

from PySide2 import QtWidgets, QtCore, QtGui

TitleRole = QtCore.Qt.UserRole + 1000
DescriptionRole = QtCore.Qt.UserRole + 1001
IconRole = QtCore.Qt.UserRole + 1002


class ListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, title="", description="", icon=QtGui.QIcon()):
        super(ListWidgetItem, self).__init__()
        self.title = title
        self.description = description
        self.icon = icon

    @property
    def title(self):
        return self.data(TitleRole)

    @title.setter
    def title(self, title):
        self.setData(TitleRole, title)

    @property
    def description(self):
        return self.data(DescriptionRole)

    @description.setter
    def description(self, description):
        self.setData(DescriptionRole, description)

    @property
    def icon(self):
        return self.data(IconRole)

    @icon.setter
    def icon(self, icon):
        self.setData(IconRole, icon)


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def sizeHint(self, option, index):
        return QtCore.QSize(50, 50)

    def paint(self, painter, option, index):
        super(StyledItemDelegate, self).paint(painter, option, index)
        title = index.data(TitleRole)
        description = index.data(DescriptionRole)
        icon = index.data(IconRole)

        mode = QtGui.QIcon.Normal
        if not (option.state & QtWidgets.QStyle.State_Enabled):
            mode = QtGui.QIcon.Disabled
        elif option.state & QtWidgets.QStyle.State_Selected:
            mode = QtGui.QIcon.Selected

        state = (
            QtGui.QIcon.On
            if option.state & QtWidgets.QStyle.State_Open
            else QtGui.QIcon.Off
        )
        iconRect = QtCore.QRect(option.rect)
        iconRect.setSize(QtCore.QSize(40, 40))
        icon.paint(
            painter, iconRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, mode, state
        )

        titleFont = QtGui.QFont(option.font)
        titleFont.setPixelSize(20)
        fm = QtGui.QFontMetrics(titleFont)
        titleRect = QtCore.QRect(option.rect)
        titleRect.setLeft(iconRect.right())
        titleRect.setHeight(fm.height())

        color = (
            option.palette.color(QtGui.QPalette.BrightText)
            if option.state & QtWidgets.QStyle.State_Selected
            else option.palette.color(QtGui.QPalette.WindowText)
        )
        painter.save()
        painter.setFont(titleFont)
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(titleRect, title)
        painter.restore()

        descriptionFont = QtGui.QFont(option.font)
        descriptionFont.setPixelSize(15)
        fm = QtGui.QFontMetrics(descriptionFont)
        descriptionRect = QtCore.QRect(option.rect)
        descriptionRect.setTopLeft(titleRect.bottomLeft())
        descriptionRect.setHeight(fm.height())
        painter.save()
        painter.setFont(descriptionFont)
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(
            descriptionRect,
            fm.elidedText(description, QtCore.Qt.ElideRight, descriptionRect.width()),
        )
        painter.restore()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Test Window")
        self.setStyleSheet("background-color: rgb(65, 65, 65);")

        mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(mainWidget)
        self.boxLayout = QtWidgets.QVBoxLayout()
        mainWidget.setLayout(self.boxLayout)

        # Add Widgets
        self.textField = QtWidgets.QLineEdit()
        self.listView = QtWidgets.QListWidget()

        self.textField.textChanged.connect(self.onTextChanged)

        self.boxLayout.addWidget(self.textField)
        self.boxLayout.addWidget(self.listView)
        self.fill_model()

        self.textField.setFocus()

        self.listView.setItemDelegate(StyledItemDelegate(self))

    def fill_model(self):
        titles = ["Monkey", "Giraffe", "Dragon", "Bull"]
        descriptions = [
            "Almost a homo sapiens sapiens",
            "I am a Giraffe!",
            "Can fly and is hot on spices",
            "Horny...",
        ]

        for title, description in zip(titles, descriptions):
            it = ListWidgetItem(title=title, description=description)
            self.listView.addItem(it)

    @QtCore.Slot(str)
    def onTextChanged(self, text):
        text = text.strip()
        if text:
            for i in range(self.listView.count()):
                it = self.listView.item(i)
                if it is not None:
                    it.setHidden(text.lower() not in it.title.lower())
        else:
            for i in range(self.listView.count()):
                it = self.listView.item(i)
                if it is not None:
                    it.setHidden(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())