import hou 
import os
from utils import io_utils as io
from utils import file_utils as fu


class VolumetricExporter:
    """
    Class for Houdini volumetric exporting in SOPs.
    """
    def __init__(self):
        self.proj = os.getenv("PROJ")
        self.database = os.getenv("DATABASE")
        self.fx_path = os.path.join(self.proj, "35_depot", "shots")


    def get_shotnums(self, kwargs):
        node = kwargs["node"]
        shotnums = [i for j in io.read_json(fr"{self.database}\shotlist.json") for i in (j, j)]
        return shotnums


    def get_fx_assets(self, kwargs):
        node = kwargs["node"]
        assets = [i for i in io.read_json(fr"{self.database}\assetlist.json")]
        return [i for j in assets if j.startswith("Fx:") for i in (j[3:], j[3:])]


    def get_versions(self, kwargs):
        node = kwargs["node"]
        path = self.get_path(kwargs)
        versions =  [i for j in os.listdir(path) for i in (j, j)]

        if len(versions) > 0:
            return versions
        else:
            return ["empty", "empty"]
        

    def upversion(self, kwargs):
        node = kwargs["node"]
        path = self.get_path(kwargs)
        next = fu.get_next_render_folder(path)
        new_ver = os.path.join(path, next)
        os.makedirs(new_ver)
        num = len(os.listdir(path))
        node.parm("vol_ver").set(num-1)
        #self.cache(kwargs)
    

    def cache(self, kwargs):
        node = kwargs["node"]
        node.node("filecache1").parm("execute").pressButton()


    def get_path(self, kwargs):
        node = kwargs["node"]
        shotnum = node.parm("vol_shot").rawValue()
        asset = node.parm("vol_asset").rawValue()
        path = os.path.join(self.fx_path, shotnum, "Fx", asset, "volumetric")
        return path
    

    def export_folder_path(self, kwargs):
        node = kwargs["node"]
        path = self.get_path(kwargs)
        ver = node.parm("vol_ver").rawValue()
        if ver != "empty":
            target_path = os.path.join(path, ver)
        else:
            target_path = os.path.join(path, "v001")

        return target_path
    
    
    def export_file_name(self, kwargs):
        node = kwargs["node"]
        shotnum = node.parm("vol_shot").rawValue()
        asset = node.parm("vol_asset").rawValue()
        path = fr"sh{shotnum}_{asset}"
        return path


class GeoExporter:
    """
    Class for Houdini Geometry exporting in SOPs.
    """
    def __init__(self):
        self.proj = os.getenv("PROJ")


