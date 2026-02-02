import os
from utils import io_utils as io
from project_manager.depot_manager import depot_manager_logic
try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets


class ShotManagerLogic:
    """
    Logic backend for shot manager.
    """
    def __init__(self, ui: QtWidgets.QWidget):
        """
        Initialises json files to read from.

        Args:
            ui (QtWidgets.QWidget): Parent Qt Ui.
        """
        self.ui = ui
        self.proj = os.getenv("PROJ")
        self.depot = fr"{self.proj}\35_depot"
        self.database = os.getenv("DATABASE")
        self.shotlist = fr"{self.database}\shotlist.json"
        self.structure = fr"{self.database}\structure.json"


    def add_shot(self):
        """
        Adds shot information to shotlist json file.
        """
        self.data = io.read_json(self.shotlist)

        shot_num = self.ui.shot_num_lineedit.text()
        if shot_num not in self.data:
            
            new_data = {}
            parms = ["lens_length", "aperture", "camera_height", 
                     "iso", "nd_filter", "white_balance",
                     "startframe", "endframe", "hdri"]

            for i in parms:
                new_data[i] = getattr(self.ui, f"{i}_lineedit").text()

            self.data[shot_num] = new_data
            io.write_json(self.shotlist, self.data)
            logic = depot_manager_logic.DepotManagerLogic()
            logic.update_depot()



        






if __name__ == "__main__":
    import shot_manager_ui
    from PySide6 import QtWidgets
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui =  shot_manager_ui.ShotManagerUi()



