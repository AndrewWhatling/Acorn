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
                for attr in prim.GetAuthoredAttributes():
                    self.validate_attribute(stage, prim, attr, "Anim")

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
        
        for prim in stage.Traverse():
            if prim.GetName() == "mtl" or prim.IsA("GeomSubset") or prim.IsA("Material"):
                to_remove.append(prim.GetPath())
                continue

            # for attr in prim.GetAuthoredAttributes():
            #         self.validate_attribute(stage, prim, attr, "Geo")
            
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

            if prim.IsA("Camera"):
                for attr in prim.GetAuthoredAttributes():
                    self.validate_attribute(stage, prim, attr, "Cam")

        return stage
        

    def validate_attribute(self, stage: Usd.Stage, prim: Usd.Prim, attr: Usd.Attribute, type: str):
        """
        Cleans up unneccessary attribute.

        Args:
            stage (Usd.Stage): Stage to clean.
            prim (Usd.Prim): Prim to clean.
            attr (Usd.Attribute): Attribute to clean.
            type (str): Type of cleaning to perform.
        """
        name = attr.GetName()
        first_frame = stage.GetStartTimeCode()

        match type:
            case "Anim":
                static = ["faceVertexCounts", "faceVertexIndices"]
                animated = ["points", "extent"]
                        
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
            
            case "Geo":
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

            case "Cam":
                static = ["clippingRange", "focalLength", "focusDistance",
                         "horizontalAperture", "verticalAperture"]
                
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
            

    def clear_pivots(self, stage: Usd.Stage) -> Usd.Stage:
        
        for prim in stage.Traverse():
            xf = UsdGeom.Xformable(prim)
            if not xf:
                return

            ops = xf.GetOrderedXformOps()
            pivot_ops = [op for op in ops if "pivot" in op.GetOpName()]
            if not pivot_ops:
                return  # nothing to do

            # Gather time samples
            times = set()
            for op in ops:
                attr = op.GetAttr()
                if attr.ValueMightBeTimeVarying():
                    times.update(attr.GetTimeSamples())

            if not times:
                times = [Usd.TimeCode.Default()]

            # Remove existing ops
            xf.ClearXformOpOrder()

            # Create clean ops
            t_op = xf.AddTranslateOp()
            r_op = xf.AddRotateXYZOp()
            s_op = xf.AddScaleOp()

            for t in times:
                m = xf.GetLocalTransformation(t)[0]

                translation = m.ExtractTranslation()
                rotation = m.ExtractRotation().GetEulerAngles()
                scale = Gf.Vec3d(
                    m[0][0], m[1][1], m[2][2]
                )

                t_op.Set(translation, t)
                r_op.Set(rotation, t)
                s_op.Set(scale, t)

        return stage

