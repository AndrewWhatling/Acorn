from pxr import Usd
import os
from utils import file_utils
from usd_tools import core, validator


class ReExporter:
    """
    Export class for reformatting input USD file.
    """
    def __init__(self, input_file: str, asset_name: str, asset_type: str, shot_num="Empty"):
        """
        Initialise attributes from Usd export.

        Args:
            input_file (str): Usd file to reformat.
            asset_name (str): Name of asset that was exported.
            asset_type (str): Type of asset that was exported.
            shot_num (str, optional): Shot number that asset is associated with. Defaults to "Empty".

        Raises:
            FileNotFoundError: If no Usd file is found.
        """
        self.input_file = input_file
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Usd file to re-export not found: {self.input_file}")
        
        self.shot_num = shot_num
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.stage = Usd.Stage.Open(self.input_file)


    def export_mesh(self):
        """
        Re-exports Usd using defined defaults for a mesh export.
        """

        path = f'/Scene/Assets/{self.asset_type}/{self.asset_name}/Geo'
        self.stage = core.flatten_stage(self.stage)
        self.root_prims = core.get_stage_root_prims(self.stage)
        self.stage = core.define_asset_hierarchy(self.stage, path)

        self.stage.SetDefaultPrim(self.stage.GetPrimAtPath(path))

        for root_prim in self.root_prims:
            core.recursive_move_prims(self.stage, root_prim, path)
        
        self.stage = validator.Validator().validate_geo(self.stage)

        output_folder = fr"{os.getenv('PROJ')}\35_depot\assets\{self.asset_type}\{self.asset_name}\Geo"
        output_file_base = fr"{self.asset_name}"
        output_file = file_utils.get_next_usd_file(output_file_base, output_folder, "usda")

        self.stage.Export(output_file)


    def export_anim(self):
        """
        Re-exports Usd using defined defaults for an animation export.
        """
        self.stage = validator.Validator().validate_anim(self.stage)

        output_folder = fr"{os.getenv('PROJ')}\35_depot\shots\{self.shot_num}\{self.asset_type}\{self.asset_name}\Anim"
        output_file_base = fr"{self.asset_name}_{self.shot_num}"
        output_file = file_utils.get_next_usd_file(output_file_base, output_folder)

        self.stage.Export(output_file)
        
    
    def export_cam(self):
        """
        Re-exports Usd using defined defaults for a camera export.
        """
        self.stage = core.flatten_stage(self.stage)
        self.stage = core.remove_meshes(self.stage)
        self.stage = core.remove_mats(self.stage)

        path = f'/Scene/Cameras/RenderCam'
        self.stage = core.create_new_camera(self.stage, path)

        output_folder = fr"{os.getenv('PROJ')}\35_depot\shots\{self.shot_num}\Cameras"
        output_file_base = fr"Camera_{self.shot_num}"
        output_file = file_utils.get_next_usd_file(output_file_base, output_folder, "usda")

        self.stage.Export(output_file)
    

if __name__ == "__main__":
    exp = ReExporter(r"C:\users\andrew\downloads\temp_01.usda", "Birdfeeder", "Prop")
    exp.export_mesh()