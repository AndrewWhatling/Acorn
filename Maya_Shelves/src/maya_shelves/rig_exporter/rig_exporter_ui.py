import os
from utils import io_utils as io

from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import *
import sys
import os

from utils import ui_utils
from utils import io_utils as io
from project_manager.asset_manager import add_asset_ui as aa
from maya_shelves.rig_exporter import rig_exporter_logic as logic

from importlib import reload
reload(logic)
reload(aa)


class RigExporterUi(QtWidgets.QMainWindow):
    """
    Ui for rig exporter.

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
        
        self.proj = os.getenv('PROJ')
        self.depot = fr"{self.proj}\35_depot"
        self.database = os.getenv("DATABASE")
        self.structure = io.read_json(fr"{self.database}\structure.json")

        self.asset_type_combobox = None
        self.asset_name_combobox = None
        self.publish = None
        self.cancel = None
        self.plus = None
        self.export_type = None

        self.initUI()
        self.connectSignals()


    def initUI(self):
        """
        Sets up Ui boxes.
        """
        # Setting defaults

        font = QtGui.QFont("Fira Code", 15)
        box_width = 120

        # Setting central widget

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Rig Exporter")
        width = 600
        height = 200
        self.setGeometry((1920/2) - (width/2), 350 - (height/2), width, height)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # Setting top row widget

        top = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top)

        self.asset_type_combobox = ui_utils.new_parm("Asset Type:", top_layout, font, box_width, "QComboBox")
        self.asset_name_combobox = ui_utils.new_parm("Asset Name:", top_layout, font, box_width, "QComboBox")

        top_layout.addStretch(1)

        # Setting up middle row

        middle = QtWidgets.QWidget()
        middle_layout = QtWidgets.QHBoxLayout(middle)

        middle_layout.addStretch(5)

        # Setting up bottom row

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom)

        publish = QtWidgets.QPushButton("Publish")
        publish.setFont(font)
        self.publish = publish

        cancel = QtWidgets.QPushButton("Cancel")
        cancel.setFont(font)
        self.cancel = cancel

        bottom_layout.addWidget(publish)
        bottom_layout.addWidget(cancel)

        # Finalise adding to central widget

        layout.addWidget(top)
        layout.addWidget(middle)
        layout.addWidget(bottom)

        # Modify any widgets previously defined

        self.asset_type_combobox.addItems([i for i in self.structure["assets"]])
        self.update_asset_name_combobox()


    def connectSignals(self):
        """
        Connects Ui buttons
        """
        self.cancel.clicked.connect(self.close)
        self.asset_type_combobox.currentIndexChanged.connect(self.on_asset_type_changed)
        self.publish.clicked.connect(self.publish_rig)


    def on_asset_type_changed(self):
        """
        Update script for when asset type is changed.
        """
        self.update_asset_name_combobox()


    def update_asset_name_combobox(self):
        """
        Update script to change asset names displayed.
        """
        self.asset_name_combobox.clear()
        path = fr"{self.depot}\assets\{self.asset_type_combobox.currentText()}"
        ui_utils.populate_combobox(self.asset_name_combobox, path)


    def publish_rig(self):
        """
        Exports rig file to folder structure.
        """
        asset_name = self.asset_name_combobox.currentText()
        asset_type = self.asset_type_combobox.currentText()
        if asset_name == "Empty" or asset_type == "Empty":
            ui_utils.popup_warning("Please select a valid asset to publish to.", self)
        else:
            exporter = logic.RigExporterLogic(asset_name, asset_type)
            exporter.export()
            self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RigExporterUi()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()