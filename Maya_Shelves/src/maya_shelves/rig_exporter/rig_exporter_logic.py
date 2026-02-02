import os
from utils import file_utils as fu

try:
    import maya.cmds as cmds
except ModuleNotFoundError:
    pass


class RigExporterLogic:
    """
    Logic class for rig exporter.
    """
    def __init__(self, asset_name: str, asset_type: str):
        """
        Initialises asset properties.

        Args:
            asset_name (str): Name of asset.
            asset_type (str): Type of asset.
        """
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.proj = os.getenv("PROJ")

    
    def save_file(self):
        """
        Saves maya ascii file.
        """
        cmds.file(save=True, type="mayaAscii")


    def export(self):
        """
        Exports rig file.
        """
        scene_path = cmds.file(q=True, sn=True)
        name = f"{self.asset_name}_rig"
        path = os.path.join(self.proj, "35_depot", "assets", self.asset_type, self.asset_name, "rig")
        new_file = fu.get_next_ma_file(name, path)

        self.save_file()
        self.re_write(scene_path, new_file)


    def re_write(self, input_ma: str, output_ma: str):
        """Re-writes file to correct location

        Args:
            input_ma (str): Input .ma file.
            output_ma (str): Output .ma file.
        """
        with open(input_ma, "r") as infile, open(output_ma, "w") as outfile:
            for line in infile:
                    outfile.write(line)

