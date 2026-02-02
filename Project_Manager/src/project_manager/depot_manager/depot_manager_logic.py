from utils import io_utils as io
import os
from pprint import pprint


class DepotManagerLogic:
    """
    Logic backend for depot manager.
    """
    def __init__(self):
        self.proj = os.getenv("PROJ")
        self.database = os.getenv("DATABASE")
        self.depot = fr"{self.proj}\35_depot"
        self.structure = io.read_json(fr"{self.database}\structure.json")

    
    def update_depot(self):
        """
        Updates depot folder structure.
        """
        structure = self.structure
        assets = structure["assets"]
        shots = structure["shots"]
        shotnums = [i for i in io.read_json(fr"{self.database}\shotlist.json")]

        asset_paths = [os.path.join(self.depot, "assets", i) for i in assets]
        shot_paths = [os.path.join(self.depot, "shots", i, j) for i in shotnums for j in shots]
        paths = asset_paths + shot_paths
        [os.makedirs(path) for path in paths if not os.path.exists(path)]


if __name__ == "__main__":
    logic = DepotManagerLogic()
    logic.update_depot()
