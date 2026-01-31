import os
from utils import io_utils as io

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


def root_menu_script(kwargs, mode="LOP"):

    if mode == "LOP":
        unique = sorted(set(assets) | set(shots))
        return sorted([i.capitalize() for j in unique for i in (j, j)])
    elif mode == "SOP":
        unique = sorted(set(assets))
        return sorted([i.capitalize() for j in unique for i in (j, j)])



def type_menu_script(kwargs, mode="LOP"):
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


def shot_menu_script(kwargs):
    return sorted([i for j in shotnums for i in (j, j)])


def asset_menu_script(kwargs):
    self = kwargs["node"]
    current = self.parm("root").rawValue()
    asset_vals = [i for i in assetlist if i.startswith(current.capitalize())]
    names = [assetlist[i]["name"] for i in asset_vals]

    if len(asset_vals) > 0:
        return sorted([i for j in names for i in (j, j)])
    else:
        return ["N/A", "N/A"]


def version_menu_script(kwargs):
    self = kwargs["node"]
    root = self.parm("root").rawValue()
    asset = self.parm("asset").rawValue()
    curr_type = self.parm("type").rawValue().lower()
    shotnum = self.parm("shot").rawValue()
    asset_types = assets.get(root, [])
    shot_types = shots.get(root, [])

    if asset == "N/A":
        return ["Empty", "Empty"]

    path = ""
    if curr_type in asset_types:
        path = os.path.join(depot, "assets", root, asset, curr_type)
    if curr_type in shot_types:
        path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    if path == "":
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


def import_path():
    root = hou.parm("../root").rawValue()
    asset = hou.parm("../asset").rawValue()
    curr_type = hou.parm("../type").rawValue().lower()
    shotnum = hou.parm("../shot").rawValue()
    version = hou.parm("../version").rawValue()

    asset_types = assets.get(root, [])
    shot_types = shots.get(root, [])

    path = ""
    if curr_type in asset_types:
        path = os.path.join(depot, "assets", root, asset, curr_type)
    if curr_type in shot_types:
        path = os.path.join(depot, "shots", shotnum, root, asset, curr_type)

    if path == "":
        return ""
    
    for i in os.listdir(path):
        ver = i.split(".")[0][-4:]
        if ver == version:
            return os.path.join(path, i)

    return ""


if __name__ == "__main__":
    print(root_menu_script([]))