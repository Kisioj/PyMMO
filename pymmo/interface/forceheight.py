import random
import sys
import math

from PySide6.QtGui import QPalette, QColor, QFontMetrics
from PySide6.QtWidgets import QWidget, QApplication, QListWidget, QLabel


from pymmo.interface import ui_controller


class VerbWidget(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enterEvent(self, event):
        print("hovered", self.text())
        self.setStyleSheet("QLabel { color: green; }")
        ui_controller.ui.statusBar.showMessage(f'usage: {self.text()}')

    def leaveEvent(self, event):
        print("left", self.text())
        self.setStyleSheet("QLabel { color: black; }")

    def mousePressEvent(self, event):
        print("clicked", self.text())

    # def onClick(self):
    #     print('clicked')


class ChangingHeightWidget(QWidget):           # - QWidget
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.setFrameShape(self.NoFrame)           # +++
        # self.setFlow(self.LeftToRight)             # +++
        # self.setWrapping(True)                     # +++
        # self.setResizeMode(self.Adjust)            # +++

        self.element_width = 64
        self.element_height = 20
        # self._allow_height_change = False
        self._child_widgets = []
        self._create_children(8)




    def _create_children(self, count: int):
        for i in range(count):
            # Create a panel
            new_child = VerbWidget()
            text = random.choice("abcdefghij") * random.randint(5, 15)
            new_child.setText(text)
            # new_child.setFixedSize(64, 64)
            new_child.setParent(self)

            width = QFontMetrics(new_child.font()).width(text)
            if width + 20 > self.element_width:
                self.element_width = width + 20
            # new_child.font()
            print(f"{text=}, {width=}. {len(text)}")
            new_child.show()

            # Set the color
            # pal = QPalette()
            # pal.setColor(QPalette.Background, QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            # new_child.setAutoFillBackground(True)
            # new_child.setPalette(pal)

            self._child_widgets.append(new_child)

        self._move_panels()

    def _move_panels(self):
        num_per_row = max(int((self.width()) / self.element_width), 1)

        for i in range(8):
            y = int(i / num_per_row)
            x = i % num_per_row
            self._child_widgets[i].move(x * self.element_width, y * self.element_height)

#        num_rows = math.ceil(8 / float(num_per_row))
#        min_height = num_rows * 64
#        self.setFixedHeight(min_height)

    def resizeEvent(self, QResizeEvent):
        self._move_panels()


if __name__ == '__main__':
#    import callback_fix
    app = QApplication(sys.argv)
    gui = ChangingHeightWidget()
    gui.show()
    app.exec_()
