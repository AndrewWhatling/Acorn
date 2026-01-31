import os
import hou
from importlib import reload
from pxr import UsdGeom
import voptoolutils

# Material assigner logic

class MaterialAssigner:
    def __init__(self, node: hou.Node):
        self.node = node;
        self.matlib = self.node.node("materiallibrary1")
        self.assign = self.node.node("assignmaterial1")
        

    def create_mats(self):
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
    root = os.getenv("PROJ")
    path = fr"{root}\30_assets\depot"

    values = []

    values.extend(["Empty", "Empty"])

    for child in os.listdir(path):
        values.extend([child, child])   
    
    return sorted(values)


def name_menu_script() -> list[str]:
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
    type = hou.parm("../type").rawValue()
    name = hou.parm("../name").rawValue()

    if type == "Empty":
        return "/materials/"

    return f"/Scene/Assets/{type}/{name}/Mat/"


# Python Module Scripts

def update_names(kwargs):
    kwargs["node"].parm("name").pressButton()


def assign_materials(kwargs):
    assigner = MaterialAssigner(kwargs["node"])
    assigner.create_mats()
        

def populate_materials(kwargs):
    assigner = MaterialAssigner(kwargs["node"])
    assigner.populate_mats()


def clear_assignments(kwargs):
    kwargs["node"].node("assignmaterial1").parm("nummaterials").set(0)


def clear_all(kwargs):
    kwargs["node"].node("assignmaterial1").parm("nummaterials").set(0)
    for n in kwargs["node"].node("materiallibrary1").children():
        n.destroy()

