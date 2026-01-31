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
    
    def __init__(self, asset_name: str, asset_type: str, export_type: str, shot_num="Empty"):
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
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")

    # Give option to choose export suffix, by default it should be .usd
    def initial_export(self) -> str:
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
        logic = rex.ReExporter(path, self.asset_name, self.asset_type, self.shot_num)

        if self.export_type == "Cam":
            logic.export_cam()

        if self.export_type == "Geo":
            logic.export_mesh()
        
        if self.export_type == "Anim":
            logic.export_anim()

    
    def cleanup(self, path: str):
        os.remove(path)


    def mesh_selected(self):
        if len(cmds.ls(sl=True)) == 0:
            ui_utils.popup_warning("Please select a mesh to export.")
            return False
        return True
