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
    """
    Logic class for asset referencer.
    """
    def __init__(self, asset_name: str, asset_type: str, reference_object: str, version_num: str):
        """
        Initialise asset properties to find file with.

        Args:
            asset_name (str): Name of asset to reference.
            asset_type (str): Type of asset to reference.
            reference_object (str): Object to reference.
            version_num (str): Version of asset to reference.
        """
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.reference_object = reference_object
        self.version_num = version_num
        self.proj = os.getenv("PROJ")


    def reference(self):
        """
        References selected file into Maya.
        """
        root_path = os.path.join(self.proj, "35_depot", "assets", self.asset_type, self.asset_name, self.reference_object)
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
        