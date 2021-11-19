import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QTextOption, QFontMetrics, QPixmap, QIcon, QAction
from PySide6.QtWidgets import QApplication, QSpacerItem, QMenu

from . import ui

class StatPanelWidget(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setStyleSheet('QScrollArea {background: red;}')
        self._widget = QtWidgets.QWidget(self)
        self._widget.setStyleSheet('QWidget {background: white;}')
        self.setWidget(self._widget)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setMinimumSize(50, 50)
        self._rows = []

        self.grid = QtWidgets.QGridLayout(self._widget)
        self.grid.setColumnStretch(1, 1)

    def resizeEvent(self, event):
        self.widget().setFixedWidth(self.width() - 2)
        super().resizeEvent(event)

    def stat(self, key: str, value: dict):
        self._rows.append((key, value))

    def refresh(self):
        i = 0
        for key, value in self._rows:
            self.grid.addWidget(StatKeyWidget(text=key), i, 0)
            if 'icon' in value:
                self.grid.addLayout(StatValueLayout(**value), i, 1)
            else:
                self.grid.addWidget(StatValueWidget(**value), i, 1)
            i += 1

        self.grid.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), i, 1)
        if i > 0:
            self.grid.addItem(QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum), 0, 2)


class StatValueLayout(QtWidgets.QHBoxLayout):
    def __init__(self, *args, icon, text, **kwargs):
        super().__init__(*args, **kwargs)
        text_widget = StatValueWidget(text=text)
        text_widget.document().setDocumentMargin(3)
        icon_widget = StatIconWidget(icon=icon, text_widget=text_widget)
        self.addWidget(icon_widget)
        self.addWidget(text_widget)
        self.setSpacing(0)


class TextEdit(QtWidgets.QTextEdit):
    def __init__(self, *args, text, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.document().setDocumentMargin(0)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)
        self.textChanged.connect(self.onTextChanged)
        self.setText(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedHeight(int(self.document().size().height()))

    def onTextChanged(self):
        self.setMaximumWidth(QFontMetrics(self.font()).boundingRect(self.toPlainText()).width()+2+self.document().documentMargin()*2)


class StatKeyWidget(TextEdit):
    pass


class StatValueWidget(TextEdit):
    def enterEvent(self, event):
        if ui.widgets:
            ui.widgets.status_bar.showMessage(self.toPlainText())
        self.setStyleSheet("QTextEdit { color: green; }")

    def leaveEvent(self, event):
        if ui.widgets:
            ui.widgets.status_bar.showMessage(f'')
        self.setStyleSheet("QTextEdit { color: black; }")

    def mousePressEvent(self, event):
        print('StatValueWidget.mousePressEvent')

    def contextMenuEvent(self, event):
        print('StatValueWidget.contextMenuEvent')
        menu = QMenu()
        action = QAction(self.toPlainText())
        action.setIcon(QIcon('/home/kisioj/Pictures/awaria.png'))
        menu.addAction(action)
        menu.addAction('Action 2')
        menu.addAction('Action 3')
        menu.exec(event.globalPos())


class StatIconWidget(QtWidgets.QLabel):
    def __init__(self, *args, icon, text_widget, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPixmap(QPixmap(icon).scaled(32, 32))
        self.setFixedSize(32, 32)
        self.text_widget = text_widget

    def enterEvent(self, event):
        self.text_widget.enterEvent(event)

    def leaveEvent(self, event):
        self.text_widget.leaveEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = StatPanelWidget()
    widget.stat("TextLabel", {'text': "TextLabel TextLabel TextLabel TextLabel TextLabel", 'icon': '/home/kisioj/Pictures/awaria.png'})
    widget.stat("TextLabel", {'text': 'TextLabelTextLabelTextLabelTextLabel'})
    widget.refresh()
    widget.show()
    app.exec_()
