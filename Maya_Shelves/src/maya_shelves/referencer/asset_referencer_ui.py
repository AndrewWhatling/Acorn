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
from maya_shelves.referencer import asset_referencer_logic as logic

from importlib import reload
reload(logic)
reload(aa)


class AssetReferencerUi(QtWidgets.QMainWindow):
    """
    Ui for asset referencer.

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

        self.setWindowTitle("Asset Referencer")
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

        self.reference_object = ui_utils.new_parm("Reference:", middle_layout, font, box_width, "QComboBox")
        self.version = ui_utils.new_parm("Version:", middle_layout, font, box_width, "QComboBox")

        middle_layout.addStretch(1)

        # Setting up bottom row

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom)

        reference = QtWidgets.QPushButton("Reference")
        reference.setFont(font)
        self.reference = reference

        cancel = QtWidgets.QPushButton("Cancel")
        cancel.setFont(font)
        self.cancel = cancel

        bottom_layout.addWidget(reference)
        bottom_layout.addWidget(cancel)

        # Finalise adding to central widget

        layout.addWidget(top)
        layout.addWidget(middle)
        layout.addWidget(bottom)

        # Modify any widgets previously defined

        self.asset_type_combobox.addItems([i for i in self.structure["assets"]])
        self.update_asset_name_combobox()
        self.update_reference_object_combobox()
        self.update_version()


    def connectSignals(self):
        """
        Connects Ui buttons
        """
        self.cancel.clicked.connect(self.close)
        self.asset_type_combobox.currentIndexChanged.connect(self.on_asset_type_changed)
        self.reference.clicked.connect(self.reference_asset)
        self.asset_name_combobox.currentIndexChanged.connect(self.on_asset_name_changed)
        self.reference_object.currentIndexChanged.connect(self.on_reference_object_changed)


    def on_asset_type_changed(self):
        """
        Update script for when asset is changed.
        """
        self.update_asset_name_combobox()
        self.update_reference_object_combobox()
        self.update_version()

    
    def on_reference_object_changed(self):
        """
        Update script for when asset is changed.
        """
        self.update_version()


    def on_asset_name_changed(self):
        """
        Update script for when asset name is changed.
        """
        self.update_version()


    def update_asset_name_combobox(self):
        """
        Updates asset name.
        """
        self.asset_name_combobox.clear()
        path = fr"{self.depot}\assets\{self.asset_type_combobox.currentText()}"
        ui_utils.populate_combobox(self.asset_name_combobox, path)


    def update_reference_object_combobox(self):
        """
        Updates reference object.
        """
        self.reference_object.clear()
        if "geo" in self.structure["assets"][self.asset_type_combobox.currentText()]:
            self.reference_object.addItems(["Geo"])
        if "rig" in self.structure["assets"].get(self.asset_type_combobox.currentText(), []):
            self.reference_object.addItems(["Rig"])


    def reference_asset(self):
        """
        References asset into scene.
        """
        asset_name = self.asset_name_combobox.currentText()
        asset_type = self.asset_type_combobox.currentText()
        reference_object = self.reference_object.currentText()
        version_num = self.version.currentText()
        if asset_name == "Empty" or asset_type == "Empty" or reference_object == "Empty" or version_num == "Empty":
            ui_utils.popup_warning("Please select a valid asset to reference.", self)
        else:
            referencer = logic.AssetReferencerLogic(asset_name, asset_type, reference_object, version_num)
            referencer.reference()
            self.close()


    def update_version(self):
        """
        Updates version numbers.
        """
        ver = self.version
        name = self.asset_name_combobox.currentText()
        asset_type = self.asset_type_combobox.currentText()
        ref_type = self.reference_object.currentText()
        ver.clear()

        if name == "Empty" or type == "Empty" or ref_type == "Empty":
            ver.addItems(["Empty"])

        else:
            path = os.path.join(os.getenv("PROJ"), "35_depot", "assets", asset_type, name, ref_type)
            if not os.path.exists(path):
                ver.addItems(["Empty"])
            elif len(os.listdir(path)) <= 0:
                ver.addItems(["Empty"])
            else:
                for i in os.listdir(path):
                    version = i.split(".")[0][-4:]
                    ver.addItems([version])


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AssetReferencerUi()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()