import os
from utils import io_utils as io
from typing import Any
import re

try:
    import hou 
except ImportError:
    pass


database = os.getenv("DATABASE")
depot = os.path.join(os.getenv("PROJ"), "35_depot")
structure = io.read_json(fr"{database}\structure.json")
assets = structure["assets"]
shots = structure["shots"]
shotnums = [i for i in io.read_json(fr"{database}\shotlist.json")]
assetlist = io.read_json(fr"{database}\assetlist.json")


def root_menu_script(kwargs: dict[str, Any], mode="LOP") -> list[str]:
    """
    Menu script for root parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from usd importer node.
        mode (str, optional): Context of usd importer node. Defaults to "LOP".

    Returns:
        list[str]: Menu of assets for user to select from.
    """

    if mode == "LOP":
        unique = sorted(set(assets) | set(shots))
        return sorted([i.capitalize() for j in unique for i in (j, j)])
    elif mode == "SOP":
        unique = sorted(set(assets))
        return sorted([i.capitalize() for j in unique for i in (j, j)])



def type_menu_script(kwargs: dict[str, Any], mode="LOP") -> list[str]:
    """
    Menu script for type parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from usd importer node.
        mode (str, optional): Context of usd importer node. Defaults to "LOP".

    Returns:
        list[str]: Menu of asset types for user to select from.
    """
    self = kwargs["node"]
    current = self.parm("root").rawValue()
    unique = set(assets.get(current, [])) | set(shots.get(current, []))
    unique.discard("rig")

    if mode == "SOP":
        unique.discard("mat")

    if len(unique) > 0:
        return sorted([i.capitalize() for j in unique for i in (j, j)])
    else:
        return ["N/A", "N/A"]


def shot_menu_script(kwargs: dict[str, Any]) -> list[str]:
    """
    Menu script for shot parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from usd importer node.

    Returns:
        list[str]: Menu of shot numbers for user to select from.
    """
    return sorted([i for j in shotnums for i in (j, j)])


def asset_menu_script(kwargs: dict[str, Any]) -> list[str]:
    """
    Menu script for asset parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from usd importer node.

    Returns:
        list[str]: Menu of asset names for user to select from.
    """
    self = kwargs["node"]
    current = self.parm("root").rawValue()
    asset_vals = [i for i in assetlist if i.startswith(current.capitalize())]
    names = [assetlist[i]["name"] for i in asset_vals]

    if len(asset_vals) > 0:
        return sorted([i for j in names for i in (j, j)])
    else:
        return ["N/A", "N/A"]


def version_menu_script(kwargs: dict[str, Any]) -> list[str]:
    """
    Menu script for asset parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from usd importer node.

    Returns:
        list[str]: Menu of asset versions for user to select from.
    """
    self = kwargs["node"]
    root = self.parm("root").rawValue()
    asset = self.parm("asset").rawValue()
    curr_type = self.parm("type").rawValue().lower()
    
    if self.parm("mat_type"):
        mat_type =self.parm("mat_type").rawValue()
    else:
        mat_type = None

    pattern = '\d{4}'
    if re.search(pattern, self.parm("shot").rawValue()):
        shotnum = self.parm("shot").rawValue()
    else:
        shotnum = hou.expandString(self.parm("shot").expression())
    
    asset_types = assets.get(root, [])
    shot_types = shots.get(root, [])

    # if asset == "N/A":
    #     return ["Empty", "Empty"]

    path = ""

    if root in ["Cameras", "Lights", "Atmospherics", "Rendersettings"]:
        path = os.path.join(depot, "shots", shotnum, root)

    elif curr_type in ["mat"]:
        path = os.path.join(depot, "assets", root, asset, curr_type, mat_type)

    elif curr_type in ["geo", "rig", "groom", "restguides"]:
        path = os.path.join(depot, "assets", root, asset, curr_type)

    elif curr_type in ["anim", "animguides", "volumetric"]:
        path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    # if curr_type in asset_types:
    #     path = os.path.join(depot, "assets", root, asset, curr_type)
    # if curr_type in shot_types:
    #     path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    if path == "" or not os.path.exists(path):
        return ["Empty", "Empty"]
    
    vals = []
    for i in os.listdir(path):
        version = i.split(".")[0][-4:]
        vals.extend([version, version])

    if len(vals) == 0:
        return ["Empty", "Empty"]
    else:
        vals = sorted(vals, reverse=True)
        vals = [vals[0], "latest"] + vals
    return vals


def import_path() -> str:
    """
    Generates path for usd importer to load Usd file from.

    Returns:
        str: Path to Usd file.
    """
    root = hou.parm("../root").rawValue()
    asset = hou.parm("../asset").rawValue()
    curr_type = hou.parm("../type").rawValue().lower()

    if hou.parm("../mat_type"):
        mat_type = hou.parm("../mat_type").rawValue()
    else:
        mat_type = None

    pattern = '\d{4}'
    if re.search(pattern, hou.parm("../shot").rawValue()):
        shotnum = hou.parm("../shot").rawValue()
    else:
        shotnum = hou.expandString(hou.parm("../shot").expression())
    version = hou.parm("../version").rawValue()

    asset_types = assets.get(root, [])
    shot_types = shots.get(root, [])

    path = ""

    if root in ["Cameras", "Lights", "Atmospherics", "Rendersettings"]:
        path = os.path.join(depot, "shots", shotnum, root)

    elif curr_type in ["mat"]:
        path = os.path.join(depot, "assets", root, asset, curr_type, mat_type, version)

    elif curr_type in ["geo", "rig", "groom", "restguides"]:
        path = os.path.join(depot, "assets", root, asset, curr_type)

    elif curr_type in ["anim", "animguides", "volumetric"]:
        path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    # elif curr_type in asset_types:
    #     path = os.path.join(depot, "assets", root, asset, curr_type)
    # elif curr_type in shot_types:
    #     path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    if path == "":
        return ""
    
    for i in os.listdir(path):
        ver = i.split(".")[0][-4:]
        if ver == version:
            return os.path.join(path, i)

    return ""


if __name__ == "__main__":
    print(root_menu_script([]))