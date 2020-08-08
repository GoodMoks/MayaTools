from PySide2 import QtWidgets


class MessageQuestion(QtWidgets.QMessageBox):
    def __init__(self, title, text, parent):
        super(MessageQuestion, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)


    def showUI(self):
        value = self.exec_()
        if value == QtWidgets.QMessageBox.Ok:
            return True
        if value == QtWidgets.QMessageBox.Cancel:
            return False
