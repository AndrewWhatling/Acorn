from utils import ui_utils
from utils import string_utils as su
from project_manager.shot_manager import shot_manager_logic as sml
#import shot_manager_logic as sml

import sys
import os

try:
    from PySide6 import QtGui, QtCore, QtWidgets
    from PySide6.QtCore import QFile, Qt, Signal
    from PySide6.QtUiTools import *
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from PySide2.QtCore import QFile, Qt, Signal
    from PySide2.QtUiTools import *


class ShotManagerUi(QtWidgets.QMainWindow):
    """
    Ui for shot manager.

    Args:
        QtWidgets (QtWidgets.QMainWindow): Parent software's main window to inherit from.
    """
    def __init__(self, parent=None):
        """
        Initialise Ui.

        Args:
            parent (QtWidgets.QMainWindow, optional): Parent software's main window to inherit from. Defaults to None.
        """
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.initUI()
        self.connectSignals()


    def initUI(self):
        """
        Sets up Ui boxes.
        """
        # Setting defaults

        font = QtGui.QFont("Fira Code", 15)
        width = 700.0
        height = 300.0
        box_width = width/3.0

        # Setting central widget

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Shot Manager")
        self.setGeometry((1920/2) - (width/2.0), (1080/2) - (height/2), width, height)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # Setting top row widget

        one = QtWidgets.QWidget()
        one_layout = QtWidgets.QHBoxLayout(one)

        shot_num_label = QtWidgets.QLabel("Shot Num:")
        shot_num_label.setFixedWidth(box_width/2)
        shot_num_label.setFont(font)

        shot_num_lineedit = QtWidgets.QLineEdit()
        shot_num_lineedit.setFixedWidth(box_width/2)
        shot_num_lineedit.setFont(font)

        self.shot_num_lineedit = shot_num_lineedit
        one_layout.addWidget(shot_num_label, 1)
        one_layout.addWidget(self.shot_num_lineedit, 1)

        delete = QtWidgets.QPushButton("Delete")
        delete.setFont(font)
        delete.setFixedWidth(box_width)

        one_layout.addStretch(3)
        one_layout.addWidget(delete, 1)

        # Setting up row two

        two = QtWidgets.QWidget()
        two_layout = QtWidgets.QHBoxLayout(two)

        self.lens_length_lineedit = ui_utils.new_parm("Lens Length", two_layout, font, box_width, "QLineEdit")
        self.aperture_lineedit = ui_utils.new_parm("Aperture", two_layout, font, box_width, "QLineEdit")
        self.camera_height_lineedit = ui_utils.new_parm("Camera Height", two_layout, font, box_width, "QLineEdit")

        # Setting up row three

        three = QtWidgets.QWidget()
        three_layout = QtWidgets.QHBoxLayout(three)

        self.iso_lineedit = ui_utils.new_parm("ISO", three_layout, font, box_width, "QLineEdit")
        self.nd_filter_lineedit = ui_utils.new_parm("ND Filter", three_layout, font, box_width, "QLineEdit")
        self.white_balance_lineedit = ui_utils.new_parm("White Balance", three_layout, font, box_width, "QLineEdit")

        # Setting up row four

        four = QtWidgets.QWidget()
        four_layout = QtWidgets.QHBoxLayout(four)

        self.startframe_lineedit = ui_utils.new_parm("Startframe", four_layout, font, box_width, "QLineEdit")
        self.endframe_lineedit = ui_utils.new_parm("Endframe", four_layout, font, box_width, "QLineEdit")
        self.hdri_lineedit = ui_utils.new_parm("HDRI", four_layout, font, box_width, "QLineEdit")

        # Setting up row five

        five = QtWidgets.QWidget()
        five_layout = QtWidgets.QHBoxLayout(five)

        five_layout.addStretch(6)

        # Setting up bottom row

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom)

        add_new = QtWidgets.QPushButton("Add Shot")
        add_new.setFont(font)
        self.add_new = add_new

        overwrite = QtWidgets.QPushButton("Overwrite Shot")
        overwrite.setFont(font)
        self.overwrite = overwrite

        cancel = QtWidgets.QPushButton("Cancel")
        cancel.setFont(font)
        self.cancel = cancel

        bottom_layout.addWidget(add_new)
        bottom_layout.addWidget(overwrite)
        bottom_layout.addWidget(cancel)

        # Finalise adding to central widget

        layout.addWidget(one)
        layout.addWidget(two, stretch=1)
        layout.addWidget(three, stretch=1)
        layout.addWidget(four, stretch=1)
        layout.addWidget(five, stretch=1)
        layout.addWidget(bottom)
        
        # Modify any widgets previously defined

        #ui_utils.populate_combobox(self.shot_num_combobox, fr"{os.getenv('PROJ')}/30_assets/depot/")


    def connectSignals(self):
        """
        Connects Ui buttons
        """
        self.cancel.clicked.connect(self.close)
        self.add_new.clicked.connect(lambda: self.add_shot())


    def add_shot(self):
        """
        Add shot data to json file.
        """
        logic = sml.ShotManagerLogic(self)
        logic.add_shot()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShotManagerUi()
    window.show()
    sys.exit(app.exec_())
