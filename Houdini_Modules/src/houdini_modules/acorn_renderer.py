import hou 
import os
from utils import io_utils as io
from utils import file_utils as fu
from deadline_tools import houdini_submitter
from typing import Any


proj = os.getenv("PROJ")
database = os.getenv("DATABASE")
shotnums = [i for i in io.read_json(fr"{database}\shotlist.json")]
renders_root = os.path.join(proj, "45_render")


def shot_menu_script(kwargs: dict[str, Any]) -> list[str]:
    """
    Menu script for shot parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from acorn render node.

    Returns:
        list[str]: Menu of shot numbers for user to select from.
    """
    return sorted([i for j in os.listdir(renders_root) for i in (j[2:], j[2:])])


def version_menu_script(kwargs: dict[str, Any]) -> list[str]:
    """
    Menu script for asset parameter on usd importer node.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from acorn render node.

    Returns:
        list[str]: Menu of versions for user to write render file to.
    """
    self = kwargs["node"]
    path = os.path.join(renders_root, f'sh{self.parm("shot").rawValue()}')
    if len(os.listdir(path)) > 0:
        versions = os.listdir(path)
        vals = [i for j in versions for i in (j, j)]
        return sorted(vals, reverse=True)
    else:
        return ["Empty", "Empty"]


def submit_to_deadline(kwargs: dict[str, Any]):
    """
    Custom submitter to send jobs to deadline render farm.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from acorn render node.
    """
    self = kwargs["node"]
    text = "File needs to save before render can be submitted.\nIncrement file?"
    buttons = ["Save Current", "Increment file", "Cancel"]
    confirm = hou.ui.displayMessage(text, buttons, default_choice=2, close_choice=2)

    if confirm == 0:
        hou.hipFile.save()
    if confirm == 1:
        hou.hipFile.saveAndIncrementFileName()

    if confirm != 2:
        if self.parm("version").rawValue() == "Empty":
            upversion(kwargs)

        submitter = houdini_submitter.HoudiniSubmitter(kwargs)
        submitter.submit_to_deadline()

        if self.parm("deep").eval() == 1:
            submitter.submit_deep_to_deadline()


def rop_export_path() -> str:
    """
    Export path for render files to be sent to.

    Returns:
        str: Path to render exr files to.
    """
    proj = os.getenv("PROJ")
    shotnum = hou.parm("../shot").rawValue()
    version = hou.parm("../version").rawValue()

    path = os.path.join(proj, "45_render", f"sh{shotnum}", version, "beauty", f"BushtailBandit_sh{shotnum}_{version}.$F4.exr")
    path =  path.replace("P:\\", "\\\\monster\\projects\\")
    path = path.replace("\\", "/")
    return path


def deep_export_path() -> str:
    """
    Export path for deep files to be sent to.

    Returns:
        str: Path to render deep files to.
    """
    proj = os.getenv("PROJ")
    shotnum = hou.parm("../shot").rawValue()
    version = hou.parm("../version").rawValue()

    path = os.path.join(proj, "45_render", f"sh{shotnum}", version, "deep", f"BushtailBandit_sh{shotnum}_{version}_dcm.$F4.exr")
    path =  path.replace("P:\\", "\\\\monster\\projects\\")
    path = path.replace("\\", "/")
    return path


def upversion(kwargs: dict[str, Any]):
    """
    Creates new folder version to render to.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from acorn render node.
    """
    self = kwargs["node"]
    path = os.path.join(renders_root, f'sh{self.parm("shot").rawValue()}')
    next = fu.get_next_render_folder(path)
    os.makedirs(os.path.join(path, next))
    self.parm("version").pressButton()