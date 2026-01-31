from pxr import Usd, UsdShade
from usd_tools import core


class Validator:
    def validate_anim(self, stage: Usd.Stage) -> Usd.Stage:
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
        for prim in stage.Traverse():
            if prim.HasAuthoredMetadata("kind"):
                prim.ClearMetadata("kind")

            if prim.IsA("Camera"):
                for attr in prim.GetAuthoredAttributes():
                    self.validate_attribute(stage, prim, attr, "Cam")

        return stage
        

    def validate_attribute(self, stage: Usd.Stage, prim: Usd.Prim, attr: Usd.Prim.GetAttribute, type: str):
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
            


