from utils import ui_utils
from utils import string_utils as su

from project_manager.asset_manager import add_asset_logic as aal
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


class AddAssetUi(QtWidgets.QMainWindow):

    assetAdded = Signal(str, str)

    def __init__(self, parent=None, input_asset_type=None):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.input_asset_type = input_asset_type
        self.asset_type_combobox = None
        self.asset_name_lineedit = None
        self.publish = None
        self.cancel = None

        self.initUI()
        self.connectSignals()


    def initUI(self):
        # Setting defaults

        font = QtGui.QFont("Fira Code", 15)
        box_width = 120

        # Setting central widget

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Add Asset")
        width = 600
        height = 200
        self.setGeometry((1920/2) - (width/2), 450 - (height/2), width, height)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # Setting top row widget

        top = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top)

        asset_type_label = QtWidgets.QLabel("Asset Type:")
        asset_name_label = QtWidgets.QLabel("Asset Name:")
        asset_name_label.setFixedWidth(box_width)
        asset_type_label.setFixedWidth(box_width)
        asset_name_label.setFont(font)
        asset_type_label.setFont(font)

        asset_type = QtWidgets.QComboBox()
        asset_type.setFont(font)
        asset_type.setFixedWidth(box_width)
        self.asset_type_combobox = asset_type

        asset_name = QtWidgets.QLineEdit()
        asset_name.setFont(font)
        asset_name.setFixedWidth(box_width*2)
        self.asset_name_lineedit = asset_name

        top_layout.addWidget(asset_type_label)
        top_layout.addWidget(asset_type)
        top_layout.addWidget(asset_name_label)
        top_layout.addWidget(asset_name)

        # Setting up bottom row

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom)

        publish = QtWidgets.QPushButton("Add Asset")
        publish.setFont(font)
        self.publish = publish

        cancel = QtWidgets.QPushButton("Cancel")
        cancel.setFont(font)
        self.cancel = cancel

        bottom_layout.addWidget(publish)
        bottom_layout.addWidget(cancel)

        # Finalise adding to central widget

        layout.addWidget(top)
        layout.addWidget(bottom)

        # Modify any widgets previously defined

        ui_utils.populate_combobox(self.asset_type_combobox, fr"{os.getenv('PROJ')}/35_depot/assets")
        
        text = self.input_asset_type
        index = self.asset_type_combobox.findText(text)

        if index != -1:
            self.asset_type_combobox.setCurrentIndex(index)


    def connectSignals(self):
        self.cancel.clicked.connect(self.close)
        self.publish.clicked.connect(self.add_asset)


    def add_asset(self):
        asset_type = self.asset_type_combobox.currentText()
        asset_name = su.to_camel_case(self.asset_name_lineedit.text())
        if asset_name == "":
           ui_utils.popup_warning("Please input an asset name.", self)
        else: 
            aal.add_asset(asset_name, asset_type)
            self.assetAdded.emit(asset_name, asset_type)
            self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AddAssetUi()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()