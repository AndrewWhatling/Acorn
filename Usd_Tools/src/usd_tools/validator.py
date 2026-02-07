from pxr import Usd, UsdShade, UsdGeom, Gf
from usd_tools import core


class Validator:
    def validate_anim(self, stage: Usd.Stage) -> Usd.Stage:
        """
        Cleans up unneccessary animation attributes.

        Args:
            stage (Usd.Stage): Stage to clean.

        Returns:
            Usd.Stage: Cleaned Stage.
        """
        to_remove = []
        first_frame = stage.GetStartTimeCode()

        for prim in stage.Traverse():
            if prim.GetName() == "mtl" or prim.IsA("GeomSubset"):
                to_remove.append(prim.GetPath())
                continue

            if prim.HasAuthoredMetadata("kind"):
                prim.ClearMetadata("kind")

            if prim.HasAuthoredMetadata("apiSchemas"):
                prim.ClearMetadata("apiSchemas")

            if prim.HasAPI(UsdShade.MaterialBindingAPI):
                binding_api = UsdShade.MaterialBindingAPI(prim)
                binding_api.UnbindDirectBinding()

            if prim.GetRelationship('material:binding'):
                prim.RemoveProperty('material:binding')

            if prim.IsA("Mesh"):
                static = ["faceVertexCounts", "faceVertexIndices"]
                animated = ["points", "extent"]
                for attr in prim.GetAuthoredAttributes():
                    name = attr.GetName()

                    if name in static:
                        value = attr.Get(first_frame)
                        attr.Clear()
                        attr.Set(value)
                    
                    elif name in animated or name.startswith("xFormOp"):
                        timesamples = attr.GetTimeSamples()
                        if len(timesamples) > 1:
                            for sample in timesamples:
                                if not float(sample).is_integer():
                                    attr.ClearAtTime(sample)

                    else:
                        prim.RemoveProperty(name)

        for path in to_remove:
            stage.RemovePrim(path)

        return stage


    def validate_geo(self, stage: Usd.Stage) -> Usd.Stage:
        """
        Cleans up unneccessary geometry attributes.

        Args:
            stage (Usd.Stage): Stage to clean.

        Returns:
            Usd.Stage: Cleaned Stage.
        """
        to_remove = []
        first_frame = stage.GetStartTimeCode()

        for prim in stage.Traverse():
            if prim.GetName() == "mtl" or prim.IsA("GeomSubset") or prim.IsA("Material"):
                to_remove.append(prim.GetPath())
                continue
            
            core.transfer_material(prim, prim)

            if prim.HasAuthoredMetadata("kind"):
                    prim.ClearMetadata("kind")

            if prim.HasAuthoredMetadata("apiSchemas"):
                prim.ClearMetadata("apiSchemas")

            if prim.HasAPI(UsdShade.MaterialBindingAPI):
                binding_api = UsdShade.MaterialBindingAPI(prim)
                binding_api.UnbindDirectBinding()

            if prim.GetRelationship('material:binding'):
                prim.RemoveProperty('material:binding')

            for attr in prim.GetAuthoredAttributes():
                    name = attr.GetName()
                    valid = ["points", "extent", "primvars:st", "primvars:st:indices",
                            "doubleSided", "faceVertexCounts", "faceVertexIndices",
                            "normals"]
                    
                    if name in valid:
                        if attr.ValueMightBeTimeVarying():
                            value = attr.Get(time=first_frame)
                            attr.Clear()
                            attr.Set(value)

                    elif name == "primvars:mat":
                        if attr.Get(first_frame) == "initialShadingGroup":
                            prim.RemoveProperty(name)
                    else:
                        prim.RemoveProperty(name)
            
            self.clear_pivots(prim)
            core.set_prim_defaults(prim)
        
        for path in to_remove:
            stage.RemovePrim(path)

        return stage
    
    
    def validate_cam(self, stage: Usd.Stage) -> Usd.Stage:
        """
        Cleans up unneccessary camera attributes.

        Args:
            stage (Usd.Stage): Stage to clean.

        Returns:
            Usd.Stage: Cleaned Stage.
        """
        for prim in stage.Traverse():
            if prim.HasAuthoredMetadata("kind"):
                prim.ClearMetadata("kind")

            first_frame = stage.GetStartTimeCode()
            if prim.IsA("Camera"):
                static = ["clippingRange", "focalLength", "focusDistance",
                         "horizontalAperture", "verticalAperture"]
                
                for attr in prim.GetAuthoredAttributes():
                    name = attr.GetName()
                    if name in static:
                        value = attr.Get(first_frame)
                        attr.Clear()
                        attr.Set(value)

                    elif name.startswith("xFormOp"):
                        timesamples = attr.GetTimeSamples()
                        if len(timesamples) > 1:
                            for sample in timesamples:
                                if not float(sample).is_integer():
                                    attr.ClearAtTime(sample)

        return stage


    def clear_pivots(self, prim: Usd.Prim):
        """
        Clears xFormOp pivots from prim.

        Args:
            prim (Usd.Prim): Prim to clear pivots from.
        """
        xf = UsdGeom.Xformable(prim)
        if not xf:
            pass

        ops = xf.GetOrderedXformOps()
        pivot_ops = [op for op in ops if "pivot" in op.GetOpName()]
        if not pivot_ops:
            pass

        # Gather time samples
        for op in ops:
            attr = op.GetAttr()
            attr.Clear()
        
