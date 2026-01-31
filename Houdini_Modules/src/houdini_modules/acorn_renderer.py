import hou 
import os
from utils import io_utils as io
from utils import file_utils as fu
from deadline_tools import houdini_submitter


proj = os.getenv("PROJ")
database = os.getenv("DATABASE")
shotnums = [i for i in io.read_json(fr"{database}\shotlist.json")]
renders_root = os.path.join(proj, "45_render")


def shot_menu_script(kwargs):
    return sorted([i for j in os.listdir(renders_root) for i in (j[2:], j[2:])])


def version_menu_script(kwargs):
    self = kwargs["node"]
    path = os.path.join(renders_root, f'sh{self.parm("shot").rawValue()}')
    if len(os.listdir(path)) > 0:
        versions = os.listdir(path)
        vals = [i for j in versions for i in (j, j)]
        next = fu.get_next_render_folder(path)
        return [next, "New"] + sorted(vals, reverse=True)
    else:
        return ["v001", "New"]


def submit_to_deadline(kwargs):
    self = kwargs["node"]
    text = "File needs to save before render can be submitted.\nIncrement file?"
    buttons = ["Save Current", "Increment file", "Cancel"]
    confirm = hou.ui.displayMessage(text, buttons, default_choice=2, close_choice=2)

    if confirm == 0:
        hou.hipFile.save()
    if confirm == 1:
        hou.hipFile.saveAndIncrementFileName()

    if confirm != 2:
        submitter = houdini_submitter.HoudiniSubmitter(kwargs)
        submitter.submit_to_deadline()


def rop_export_path():
    proj = os.getenv("PROJ")
    shotnum = hou.parm("../shot").rawValue()
    version = hou.parm("../version").rawValue()

    path = os.path.join(proj, "45_render", f"sh{shotnum}", version, f"BushtailBandit_sh{shotnum}_{version}.$F4.exr")
    path =  path.replace("P:\\", "\\\\monster\\projects\\")
    path = path.replace("\\", "/")
    return path


def deep_export_path():
    proj = os.getenv("PROJ")
    shotnum = hou.parm("../shot").rawValue()
    version = hou.parm("../version").rawValue()

    path = os.path.join(proj, "45_render", f"sh{shotnum}", version, f"BushtailBandit_sh{shotnum}_{version}_dcm.$F4.exr")
    path =  path.replace("P:\\", "\\\\monster\\projects\\")
    path = path.replace("\\", "/")
    return path
