from utils import io_utils as io
from utils import codec_utils as codec
from utils import ui_utils
import os
import hashlib
from datetime import datetime

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets


class AssetLogger:
    """
    Custom asset logger for when assets are added to folder structure.
    """
    def __init__(self, parent=None):
        """
        Initialise json files to read from.

        Args:
            parent (QtWidgets.QWidget, optional): Parent widget to inherit from. Defaults to None.
        """
        self.parent_ui = parent
        self.proj = os.getenv("PROJ")
        self.database = os.getenv("DATABASE")
        self.assetlist = os.path.join(self.database, "assetlist.json")


    def asset_exists(self, asset_name: str, asset_type: str) -> bool:
        """
        Checks if asset already has been logged.

        Args:
            asset_name (str): Asset name to check.
            asset_type (str): Asset type to check.

        Returns:
            bool: Returns true if asset has already been logged.
        """
        hash = codec.hash_encode([asset_type, asset_name])
        assets = io.read_json(self.assetlist)
        
        if hash in [assets[i]["hash"] for i in assets]:
            return True
        return False


    def log_asset(self, asset_name: str, asset_type: str):
        """
        Adds asset data to log.

        Args:
            asset_name (str): Asset name to log.
            asset_type (str): Asset type to log.
        """
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

            