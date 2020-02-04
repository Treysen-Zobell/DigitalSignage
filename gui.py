from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QFormLayout, QScrollArea, QSpacerItem, QFrame)
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        left_group_box = QGroupBox()
        left_grid_layout = QGridLayout()
        left_line_edit_list = []
        left_combo_list = []
        left_status_list = []
        for i in range(25):
            left_line_edit_list.append(QLineEdit('default'))
            left_line_edit_list[i].setFixedWidth(100)

            left_line_edit_list[i].setToolTip('mac_address')

            left_combo_list.append(QComboBox())

            if i % 2 == 0:
                left_status_list.append(QLabel('online'))
                left_status_list[i].setObjectName('status_label_%d' % i)
                left_status_list[i].setStyleSheet('QLabel#status_label_%d {color: green}' % i)
            else:
                left_status_list.append(QLabel('offline'))
                left_status_list[i].setObjectName('status_label_%d' % i)
                left_status_list[i].setStyleSheet('QLabel#status_label_%d {color: red}' % i)
            left_status_list[i].setFixedWidth(50)
            left_status_list[i].setFrameShape(QFrame.Panel)
            left_status_list[i].setAlignment(Qt.AlignCenter)

            left_grid_layout.addWidget(left_line_edit_list[i], i, 0)
            left_grid_layout.addWidget(left_combo_list[i], i, 1)
            left_grid_layout.addWidget(left_status_list[i], i, 2)

        left_scroll = QScrollArea()
        left_scroll.setWidget(left_group_box)
        left_scroll.setWidgetResizable(True)

        left_group_box.setLayout(left_grid_layout)

        # Right Group Box
        right_group_box = QGroupBox()
        right_vbox_layout = QVBoxLayout()
        right_vbox_layout.setSpacing(10)

        update_button = QPushButton('Update')
        select_button = QPushButton('Select')
        vertical_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        right_vbox_layout.addWidget(update_button, alignment=Qt.AlignTop)
        right_vbox_layout.addWidget(select_button, alignment=Qt.AlignTop)
        right_vbox_layout.addSpacerItem(vertical_spacer)

        right_group_box.setLayout(right_vbox_layout)

        main_layout = QGridLayout()
        main_layout.setSpacing(20)
        main_layout.addWidget(left_scroll, 0, 0)
        main_layout.addWidget(right_group_box, 0, 1)

        self.setLayout(main_layout)
        self.setGeometry(300, 300, 600, 300)
        self.setWindowTitle('Advertising Manager')
        self.show()


app = QApplication(sys.argv)

window = Window()

app.exec_()