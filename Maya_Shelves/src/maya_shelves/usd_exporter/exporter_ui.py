from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import *
import sys
import os

from utils import ui_utils
from utils import io_utils as io
from project_manager.asset_manager import add_asset_ui as aa
from maya_shelves.usd_exporter import exporter_logic as logic

from importlib import reload
reload(logic)
reload(aa)


class MayaUsdExporterUi(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
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
        # Setting defaults

        font = QtGui.QFont("Fira Code", 15)
        box_width = 120

        # Setting central widget

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.setWindowTitle("USD Exporter")
        width = 600
        height = 200
        self.setGeometry((1920/2) - (width/2), 350 - (height/2), width, height)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # Setting top row widget

        top = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top)

        self.asset_type_combobox = ui_utils.new_parm("Asset Type:", top_layout, font, box_width, "QComboBox")
        self.asset_name_combobox = ui_utils.new_parm("Asset Name:", top_layout, font, box_width, "QComboBox")

        plus = QtWidgets.QPushButton("+")
        plus.setFont(font)
        plus.setFixedWidth(box_width)
        self.plus = plus

        top_layout.addWidget(plus, 1)

        # Setting up middle row

        middle = QtWidgets.QWidget()
        middle_layout = QtWidgets.QHBoxLayout(middle)

        self.export_type = ui_utils.new_parm("Export Type:", middle_layout, font, box_width, "QComboBox")

        self.shot_num = ui_utils.new_parm("Shot Num:", middle_layout, font, box_width, "QComboBox")
        data = io.read_json(fr"{self.database}\shotlist.json")
        shotnums = []

        for num in data:
            shotnums.append(num)
        self.shot_num.addItems(sorted(shotnums))

        middle_layout.addStretch(1)

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
        #ui_utils.populate_combobox(self.asset_type_combobox, self.asset_type_path)
        self.update_asset_name_combobox()
        self.update_export_type_combobox()


    def connectSignals(self):
        self.cancel.clicked.connect(self.close)
        self.asset_type_combobox.currentIndexChanged.connect(self.on_asset_type_changed)
        self.plus.clicked.connect(self.add_asset)
        self.publish.clicked.connect(self.publish_asset)


    def on_asset_type_changed(self):
        self.update_asset_name_combobox()
        self.update_export_type_combobox()


    def update_asset_name_combobox(self):
        self.asset_name_combobox.clear()
        path = fr"{self.depot}\assets\{self.asset_type_combobox.currentText()}"
        ui_utils.populate_combobox(self.asset_name_combobox, path)


    def update_export_type_combobox(self):
        self.export_type.clear()
        if "geo" in self.structure["assets"][self.asset_type_combobox.currentText()]:
            self.export_type.addItems(["Geo"])
        if "anim" in self.structure["shots"].get(self.asset_type_combobox.currentText(), []):
            self.export_type.addItems(["Anim"])
        self.export_type.addItems(["Cam"])


    def add_asset(self):
        popup = aa.AddAssetUi(self, self.asset_type_combobox.currentText())
        popup.assetAdded.connect(self.on_asset_added)
        popup.show()

    
    def on_asset_added(self, asset_name: str, asset_type: str):
        self.asset_type_combobox.setCurrentText(asset_type)
        self.update_asset_name_combobox()
        self.asset_name_combobox.setCurrentText(asset_name)


    def publish_asset(self):
        asset_name = self.asset_name_combobox.currentText()
        asset_type = self.asset_type_combobox.currentText()
        export_type = self.export_type.currentText()
        if asset_name == "Empty":
            ui_utils.popup_warning("Please select a valid asset to export to.", self)
        else:
            logic.MayaUsdExporterLogic(self.asset_name_combobox.currentText(), self.asset_type_combobox.currentText(), 
                                       self.export_type.currentText(), self.shot_num.currentText())
            self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MayaUsdExporterUi()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
