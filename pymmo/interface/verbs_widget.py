import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QScrollArea

from pymmo.interface import ui


class VerbWidget(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enterEvent(self, event):
        print("hovered", self.text())
        self.setStyleSheet("QLabel { color: green; }")
        if ui.widgets:
            ui.widgets.status_bar.showMessage(f'usage: {self.text()}')

    def leaveEvent(self, event):
        print("left", self.text())
        self.setStyleSheet("QLabel { color: black; }")
        if ui.widgets:
            ui.widgets.status_bar.showMessage(f'')

    def mousePressEvent(self, event):
        print("clicked", self.text())


class VerbsWidget(QScrollArea):
    ITEM_HEIGHT = 20
    ITEM_MARGIN_X = 20

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet('QScrollArea {background: white;}')
        self._widget = QWidget(self)
        self._widget.setStyleSheet('QWidget {background: white; padding: 2px;}')
        self.setWidget(self._widget)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._verbs = []
        self._items = []
        self._column_width = 0


    def set_verbs(self, items):
        self._verbs = items[:]
        self._verbs.sort()
        self._create_items()

    def add_verb(self, item):
        self._verbs.append(item)
        self._verbs.sort()
        self._create_items()

    def remove_verb(self, item):
        self._verbs.pop(item)
        self._create_items()

    def _create_items(self):
        self._column_width = 0
        for item in self._verbs:
            child = VerbWidget()
            child.setText(item)
            child.setParent(self._widget)

            width = QFontMetrics(child.font()).boundingRect(item).width()
            if width > self._column_width:
                self._column_width = width

            child.show()
            self._items.append(child)

        self._column_width += self.ITEM_MARGIN_X
        self._rearrange_items()

    def _rearrange_items(self):
        if not self._column_width:
            return

        container_width = self.width()
        container_height = self.height()

        items_per_row = max(int((self.width()) / self._column_width), 1)
        for i, item in enumerate(self._items):
            y = int(i / items_per_row)
            x = i % items_per_row
            item.move(x * self._column_width, y * self.ITEM_HEIGHT)

        widget_height = (y+1) * self.ITEM_HEIGHT
        self._widget.resize(container_width, widget_height)
        self._widget.updateGeometry()
        # print(f'{container_width=}, {container_height=}, {widget_height=}, {items_per_row=}')

    def resizeEvent(self, event):
        # print('VerbsWidget.resizeEvent')
        self._rearrange_items()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    verbs_widget = VerbsWidget()
    verbs_widget.set_verbs(['przeorganizować', 'zmienić', 'zmieniać', 'poprawić', 'poprawiać', 'przestawić', 'przesunąć', 'przesuwać', 'przestawiać', 'przełożyć', 'przekładać', 'przemeblować', 'przemeblowywać'])
    verbs_widget.show()
    app.exec_()
