import os
import hou
from importlib import reload
from pxr import UsdGeom
import voptoolutils
from typing import Any

# Material assigner logic

class MaterialAssigner:
    """
    Material automatic assignment backend for material assigner node.
    """
    def __init__(self, node: hou.Node):
        """
        Initialise links to mat lib and assign mat nodes inside HDA.

        Args:
            node (hou.Node): The material auto assigner node.
        """
        self.node = node;
        self.matlib = self.node.node("materiallibrary1")
        self.assign = self.node.node("assignmaterial1")
        

    def create_mats(self):
        """
        Creates materials based on input primitives 'mat' primvar.
        """
        stage = self.matlib.stage()
        pattern = self.node.evalParm("primpattern")
        if pattern.replace(" ", "") == "":
            pattern = "/**"

        rule = hou.LopSelectionRule()
        rule.setPathPattern(pattern)
        prims = rule.expandedPaths(stage=stage)

        pairs = {}
        mask = voptoolutils.KARMAMTLX_TAB_MASK

        for p in prims:
            prim = stage.GetPrimAtPath(str(p))
            if prim.IsA("Mesh"):
                primvars_api = UsdGeom.PrimvarsAPI(prim)
                if primvars_api.HasPrimvar("mat"):
                    key = primvars_api.GetPrimvar("mat").Get()
                    
                    if not key in pairs.keys():
                        pairs[key] = str(prim.GetPath())
                        
                        if hou.node(f"{self.matlib.path()}/{key}") == None:
                            voptoolutils._setupMtlXBuilderSubnet(destination_node=self.matlib,
                                                                  name=key,
                                                                    mask=mask,
                                                                      folder_label='Karma Material Builder')
                        
                    else:
                        pairs[key] += " " + str(prim.GetPath())
        
        self.assign.parm("nummaterials").set(len(pairs.keys()))
        idx = 0
        
        mat_path = self.matlib.parm("matpathprefix").eval()

        for k, v in pairs.items():
            idx += 1
            self.assign.parm(f"primpattern{idx}").set(v)
            self.assign.parm(f"matspecpath{idx}").set(f"{mat_path}{k}")

        self.matlib.layoutChildren()


    def populate_mats(self):
        pass


# Parameter Menu Scripts

def type_menu_script() -> list[str]:
    """
    Menu script for type parameter on material auto assigner node.

    Returns:
        list[str]: Menu of asset types for user to select from.
    """
    root = os.getenv("PROJ")
    path = fr"{root}\30_assets\depot"

    values = []

    values.extend(["Empty", "Empty"])

    for child in os.listdir(path):
        values.extend([child, child])   
    
    return sorted(values)


def name_menu_script() -> list[str]:
    """
    Menu script for name parameter on material auto assigner node.

    Returns:
        list[str]: Menu of asset names for user to select from.
    """
    root = os.getenv("PROJ")
    type = hou.pwd().parm("type").rawValue()
    path = fr"{root}\30_assets\depot\{type}"

    if type == "Empty":
        return ["Empty", "Empty"]
    
    values = []

    for child in os.listdir(path):
        values.extend([child, child])

    return sorted(values)


# Internal Node Parameter Scripts

def material_path() -> str:
    """
    Generates parent path for material Usd hierarchy.

    Returns:
        str: Parent path for material Usds to live under in hierarchy.
    """
    type = hou.parm("../type").rawValue()
    name = hou.parm("../name").rawValue()

    if type == "Empty":
        return "/materials/"

    return f"/Scene/Assets/{type}/{name}/Mat/"


# Python Module Scripts

def update_names(kwargs: dict[str, Any]):
    """Updates name parameter.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from the material auto assigner node.
    """
    kwargs["node"].parm("name").pressButton()


def assign_materials(kwargs: dict[str, Any]):
    """Assigns materials to input primitives.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from the material auto assigner node.
    """
    assigner = MaterialAssigner(kwargs["node"])
    assigner.create_mats()
        

def populate_materials(kwargs: dict[str, Any]):
    """Populates materials based on given folder.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from the material auto assigner node.
    """
    assigner = MaterialAssigner(kwargs["node"])
    assigner.populate_mats()


def clear_assignments(kwargs: dict[str, Any]):
    """Clears all material assignments.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from the material auto assigner node.
    """
    kwargs["node"].node("assignmaterial1").parm("nummaterials").set(0)


def clear_all(kwargs: dict[str, Any]):
    """Clears all material assignments and delete all materials.

    Args:
        kwargs (dict[str, Any]): Keyword arguments from the material auto assigner node.
    """
    clear_assignments(kwargs)
    for n in kwargs["node"].node("materiallibrary1").children():
        n.destroy()

