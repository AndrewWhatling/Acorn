# import maya.cmds as cmds

# cmds.file(
#     "C:/docs/test_01.usd",
#     reference=True,
#     namespace=":",
#     mergeNamespacesOnClash=True
# )

import os
try:
    import maya.cmds as cmds
except ModuleNotFoundError:
    pass


class AssetReferencerLogic:
    def __init__(self, asset_name, asset_type, reference_type, version_num):
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.reference_type = reference_type
        self.version_num = version_num
        self.proj = os.getenv("PROJ")


    def reference(self):
        root_path = os.path.join(self.proj, "35_depot", "assets", self.asset_type, self.asset_name, self.reference_type)
        path = ""
        for i in os.listdir(root_path):
            version = i.split(".")[0][-4:]
            if version == self.version_num:
                path = os.path.join(root_path, i)
                break
        
        cmds.file(
            path,
            reference=True,
            namespace=":",
            mergeNamespacesOnClash=True
        )
        