try:
    import maya.cmds as cmds
except ModuleNotFoundError:
    pass

from utils import ui_utils
import os
import tempfile
from usd_tools.io import re_exporter as rex
from importlib import reload
reload(rex)


class MayaUsdExporterLogic:
    """
    Logic backend for maya usd exporter.
    """
    def __init__(self, asset_name: str, asset_type: str, export_type: str, shot_num="Empty"):
        """
        Initialises data from Ui and exports usd file.

        Args:
            asset_name (str): Asset name to export.
            asset_type (str): Asset type to export.
            export_type (str): Export type.
            shot_num (str, optional): Shot number if applicable. Defaults to "Empty".
        """
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.export_type = export_type
        self.shot_num = shot_num

        if self.mesh_selected():
            self.load_plugins()
            path = self.initial_export()
            self.fix_export(path)
            self.cleanup(path)


    def load_plugins(self):
        """
        Loads mayaUsdPlugin if it's not already loaded.
        """
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")


    # Give option to choose export suffix, by default it should be .usd
    def initial_export(self) -> str:
        """
        Default maya export to a temp file.

        Returns:
            str: Temp usd file.
        """
        tmp_file = tempfile.NamedTemporaryFile(suffix=".usd", delete=False)
        tmp_file_path = tmp_file.name
        tmp_file.close() 

        if self.export_type == "Geo":
            cmds.mayaUSDExport(file=tmp_file_path, selection=True, stripNamespaces=True)

        if self.export_type == "Anim" or "Cam":
            frame_range = [cmds.playbackOptions(ast=True, q=True), cmds.playbackOptions(aet=True, q=True)]
            cmds.mayaUSDExport(file=tmp_file_path, selection=True, frameRange=frame_range, stripNamespaces=True)
            
        return tmp_file_path
    

    def fix_export(self, path: str):
        """
        Reformats and re-exports usd file to correct location.

        Args:
            path (str): Temp usd file.
        """
        logic = rex.ReExporter(path, self.asset_name, self.asset_type, self.shot_num)

        if self.export_type == "Cam":
            logic.export_cam()

        if self.export_type == "Geo":
            logic.export_mesh()
        
        if self.export_type == "Anim":
            logic.export_anim()


    # Should put this in file utils.
    def cleanup(self, path: str):
        """
        Removes file at path.

        Args:
            path (str): Path of file to remove.
        """
        os.remove(path)


    def mesh_selected(self) -> bool:
        """
        Pops up warning message if no mesh is selected.

        Returns:
            bool: Returns true if a mesh is selected.
        """
        if len(cmds.ls(sl=True)) == 0:
            ui_utils.popup_warning("Please select a mesh to export.")
            return False
        return True
