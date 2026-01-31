from utils import string_utils as su
from utils import io_utils as io
import os
from project_manager.asset_manager import asset_log_logic as asset_logger


def add_asset(asset_name: str, asset_type: str):
    asset_name = su.to_camel_case(asset_name)
    database = os.getenv("DATABASE")
    structure = io.read_json(fr"{database}\structure.json")
    depot = fr"{os.getenv('PROJ')}\35_depot"
    assetlist = io.read_json(fr"{database}\assetlist.json")
    logger = asset_logger.AssetLogger()
    
    if not logger.asset_exists(asset_name, asset_type):

        shotnums = [i for i in io.read_json(fr"{database}\shotlist.json")]
        asset_folders = [i for i in structure["assets"][asset_type]]
        shot_folders = [i for i in structure["shots"].get(asset_type, [])]
        
        asset_paths = [os.path.join(depot, "assets", asset_type, asset_name, i) for i in asset_folders]
        [os.makedirs(path) for path in asset_paths if not os.path.exists(path)]

        shot_paths = [os.path.join(depot, "shots", shotnum, asset_type, asset_name, i) for shotnum in shotnums for i in (shot_folders or [""]) if i]
        [os.makedirs(path) for path in shot_paths if not os.path.exists(path)]

        logger.log_asset(asset_name, asset_type)


if __name__ == "__main__":
    add_asset("Box", "Prop")
    pass