from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QFormLayout, QScrollArea, QSpacerItem, QFrame, QFileDialog)
import json, sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        with open('devices.json', 'r') as json_file:
            self.devices = json.load(json_file)

        self.left_line_edit_list = []
        self.left_checkbox_list = []
        self.left_combo_list = []
        self.left_status_list = []
        self.left_line_edit_hints = []

        self.init_ui()

    def update(self):
        for i in range(len(self.left_checkbox_list)):
            if self.left_checkbox_list[i].isChecked():
                print(self.left_line_edit_hints[i])

    @staticmethod
    def upload_file():
        files = QFileDialog.getOpenFileNames()
        print(files[0])

    def init_ui(self):
        left_group_box = QGroupBox()
        left_grid_layout = QGridLayout()

        i = 0
        for device in self.devices:
            self.left_line_edit_list.append(QLineEdit(self.devices[device][0]))
            self.left_line_edit_list[i].setFixedWidth(100)

            self.left_line_edit_list[i].setToolTip(device)
            self.left_line_edit_hints.append(device)

            self.left_combo_list.append(QComboBox())
            self.left_combo_list[i].addItems(['Media/media1.mp4', 'Media/media2.mp4', 'Media/media3.mp4'])

            if self.devices[device][1] == 'online':
                self.left_status_list.append(QLabel('online'))
                self.left_status_list[i].setObjectName('status_label_%d' % i)
                self.left_status_list[i].setStyleSheet('QLabel#status_label_%d {color: green}' % i)
            else:
                self.left_status_list.append(QLabel('offline'))
                self.left_status_list[i].setObjectName('status_label_%d' % i)
                self.left_status_list[i].setStyleSheet('QLabel#status_label_%d {color: red}' % i)
            self.left_status_list[i].setFixedWidth(50)
            self.left_status_list[i].setFrameShape(QFrame.Panel)
            self.left_status_list[i].setToolTip(self.devices[device][2])
            self.left_status_list[i].setAlignment(Qt.AlignCenter)

            self.left_checkbox_list.append(QCheckBox())
            self.left_checkbox_list[i].setFixedWidth(14)

            left_grid_layout.addWidget(self.left_line_edit_list[i], i, 0)
            left_grid_layout.addWidget(self.left_combo_list[i], i, 1)
            left_grid_layout.addWidget(self.left_status_list[i], i, 2)
            left_grid_layout.addWidget(self.left_checkbox_list[i], i, 3)

            i += 1

        left_scroll = QScrollArea()
        left_scroll.setWidget(left_group_box)
        left_scroll.setWidgetResizable(True)

        left_group_box.setLayout(left_grid_layout)

        # Right Group Box
        right_group_box = QGroupBox()
        right_vbox_layout = QVBoxLayout()
        right_vbox_layout.setSpacing(10)

        update_button = QPushButton('Update')
        upload_button = QPushButton('Upload')
        update_button.clicked.connect(self.update)
        upload_button.clicked.connect(self.upload_file)
        vertical_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        sign_label = QLabel('By: Treysen Zobell')

        right_vbox_layout.addWidget(update_button, alignment=Qt.AlignTop)
        right_vbox_layout.addWidget(upload_button, alignment=Qt.AlignTop)
        right_vbox_layout.addSpacerItem(vertical_spacer)
        right_vbox_layout.addWidget(sign_label, alignment=Qt.AlignBottom)

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
