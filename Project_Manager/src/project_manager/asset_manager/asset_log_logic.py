from utils import io_utils as io
from utils import codec_utils as codec
from utils import ui_utils
import os
import hashlib
from datetime import datetime


class AssetLogger:
    def __init__(self, parent=None):
        self.parent_ui = parent
        self.proj = os.getenv("PROJ")
        self.database = os.getenv("DATABASE")
        self.assetlist = os.path.join(self.database, "assetlist.json")


    def asset_exists(self, asset_name, asset_type):
        hash = codec.hash_encode([asset_type, asset_name])
        assets = io.read_json(self.assetlist)
        
        if hash in [assets[i]["hash"] for i in assets]:
            return True
        return False


    def log_asset(self, asset_name: str, asset_type: str):
        hash = codec.hash_encode([asset_type, asset_name])
        assets = io.read_json(self.assetlist)
        
        if not self.asset_exists(asset_name, asset_type):
            id = f"{asset_type}:{asset_name}"
            data = {
                "id":id,
                "name":asset_name,
                "type":asset_type,
                "hash":hash,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "created_by": os.getlogin()
                }
            assets[id] = data
            io.write_json(self.assetlist, assets)

            