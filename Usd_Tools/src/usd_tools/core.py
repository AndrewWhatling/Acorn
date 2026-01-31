from pxr import Usd, UsdShade, UsdGeom, Sdf


def recursive_move_prims(stage: Usd.Stage, root_prim: Usd.Prim, path: str) -> Usd.Stage.Open:
    for prim in root_prim.GetChildren():
        type = prim.GetTypeName()
        name = prim.GetName()
        
        new_path = f"{path}/{name}"
        new_prim = stage.DefinePrim(new_path, type)
        
        transfer_all(prim, new_prim)
        transfer_material(prim, new_prim)

        if len(prim.GetChildren()) > 0:
            stage = recursive_move_prims(stage, prim, new_path)
    
    stage.RemovePrim(root_prim.GetPath())
    return stage


def move_prim(stage: Usd.Stage, prim: Usd.Prim, path: str, rename=None) -> Usd.Stage:
    type = prim.GetTypeName()
    name = prim.GetName()
    
    if rename != None:
        new_path = f"{path}/{rename}"
    else:
        new_path = f"{path}/{name}"
    new_prim = stage.DefinePrim(new_path, type)

    for attr in prim.GetAttributes():

        if not attr.HasAuthoredValue():
            continue

        new_attr = new_prim.GetAttribute(attr.GetName())
        if not new_attr:
            new_attr = new_prim.CreateAttribute(attr.GetName(), attr.GetTypeName())

        if attr.Get() != None:
            if attr.ValueMightBeTimeVarying():
                for t in attr.GetTimeSamples():
                    value = attr.Get(t)
                    new_attr.Set(value, t)
            else:
                new_attr.Set(attr.Get())

    transfer_material(prim, new_prim)
    stage.RemovePrim(prim.GetPath())
    return stage


def set_prim_defaults(prim):
    if prim.IsA("Mesh"):
        mesh = UsdGeom.Mesh(prim)
        mesh.GetNormalsAttr().Clear()
        mesh.GetSubdivisionSchemeAttr().Set("catmullClark")
        mesh.GetOrientationAttr().Set(UsdGeom.Tokens.rightHanded)


def transfer_material(from_prim: Usd.Prim, to_prim: Usd.Prim):
    binding_api = UsdShade.MaterialBindingAPI(from_prim)
    material = binding_api.GetDirectBinding().GetMaterial()
    
    if material:
        name = str(material.GetPath()).split("/")[-1]
        primvars_api = UsdGeom.PrimvarsAPI(to_prim)
        var = primvars_api.CreatePrimvar("mat", Sdf.ValueTypeNames.String)
        var.Set(name)


def flatten_stage(stage: Usd.Stage) -> Usd.Stage:
    layer = stage.Flatten()
    return Usd.Stage.Open(layer)


def get_stage_root_prims(stage: Usd.Stage) -> list[Usd.Prim]:
    root = stage.GetPrimAtPath("/")
    root_prims = []
    for child in root.GetChildren():
        root_prims.append(child)

    return root_prims


def define_asset_hierarchy(stage: Usd.Stage, path: str) -> Usd.Stage:
    split_path = [p for p in path.split("/") if p]
    current = ""

    for substring in split_path:
        
        current += fr"/{substring}"
        if substring == split_path[-1]:
            UsdGeom.Xform.Define(stage, current)
        else:
            UsdGeom.Scope.Define(stage, current)

    return stage


def remove_meshes(stage: Usd.Stage) -> Usd.Stage:
    to_remove = []

    for prim in stage.Traverse():
        if prim.IsA("Mesh"):
            to_remove.append(prim)

    for prim in to_remove:
        stage.RemovePrim(prim.GetPath())
    
    return stage


def remove_mats(stage: Usd.Stage) -> Usd.Stage:
    to_remove = []

    for prim in stage.Traverse():
        if prim.GetName() == "mtl":
            to_remove.append(prim)

    for prim in to_remove:
        stage.RemovePrim(prim.GetPath())

    return stage


def create_new_camera(stage: Usd.Stage, path: str) -> Usd.Stage:
    prims = []

    for prim in stage.Traverse():

        if prim.HasAuthoredMetadata("kind"):
            prim.ClearMetadata("kind")
        prims.append(prim)

    stage = define_asset_hierarchy(stage, path)

    new_path = f"{path}/RenderCam"
    new_prim = UsdGeom.Camera.Define(stage, new_path).GetPrim()

    stage.SetDefaultPrim(stage.GetPrimAtPath(new_path))

    if len(prims) == 1:
        cam = prims[0]
        for attr in cam.GetAttributes():
            
            if not attr.HasAuthoredValue() or attr.GetName().startswith("xformOp"):
                continue
            
            new_attr = new_prim.CreateAttribute(attr.GetName(), attr.GetTypeName())

            if attr.Get():
                new_attr.Set(attr.Get())

            if attr.ValueMightBeTimeVarying():
                for t in attr.GetTimeSamples():
                    if float(t).is_integer():
                        new_attr.Set(attr.Get(t), t)
        
        transfer_xform_ops(new_prim, cam)

    elif len(prims) == 2:
        cam = None
        xform = None

        for prim in prims:
            if prim.IsA("Camera"):
                cam = prim
            if prim.IsA("Xform"):
                xform = prim

        for attr in cam.GetAttributes():
            
            if not attr.HasAuthoredValue():
                continue
            
            new_attr = new_prim.CreateAttribute(attr.GetName(), attr.GetTypeName())

            if attr.Get():
                new_attr.Set(attr.Get())

        transfer_xform_ops(new_prim, xform)
    
    for prim in prims:
        stage.RemovePrim(prim.GetPath())

    return stage


def transfer_xform_ops(src_prim, dst_prim):
    dst_xf = UsdGeom.Xformable(dst_prim)
    src_xf = UsdGeom.Xformable(src_prim)

    for src_op in src_xf.GetOrderedXformOps():
        op_type = src_op.GetOpType()
        precision = src_op.GetPrecision()
        op_name = src_op.GetOpName().split(":")[-1]

        # Check if operation already exists in the destination Xformable
        existing_ops = dst_xf.GetOrderedXformOps()
        if any(op.GetOpName().split(":")[-1] == op_name and op.GetOpType() == op_type for op in existing_ops):
            # If operation already exists then continue
            continue

        # If operation doesn't exist, add it to the destination Xformable
        dst_op = dst_xf.AddXformOp(
            op_type,
            precision=precision,
            opSuffix=op_name
        )

        src_attr = src_op.GetAttr()
        dst_attr = dst_op.GetAttr()

        handle_attribute_transfer(src_attr, dst_attr)

        # if src_attr.ValueMightBeTimeVarying():
        #     for t in src_attr.GetTimeSamples():
        #         dst_attr.Set(src_attr.Get(t), t)
        # else:
        #     dst_attr.Set(src_attr.Get())


def transfer_primvars(src_prim, dst_prim):
    src_pv_api = UsdGeom.PrimvarsAPI(src_prim)
    dst_pv_api = UsdGeom.PrimvarsAPI(dst_prim)

    for src_pv in src_pv_api.GetPrimvars():
        # Check if primvar is authored
        if not src_pv or not src_pv.GetAttr().HasAuthoredValue():
            continue
        
        # Initialise new primvar
        name = src_pv.GetName()
        type_name = src_pv.GetTypeName()
        interpolation = src_pv.GetInterpolation()

        dst_pv = dst_pv_api.CreatePrimvar(name, type_name, interpolation)
        
        # Get original primvar indices
        src_pv_indices = src_pv.GetIndicesAttr()
        if src_pv_indices and src_pv_indices.HasAuthoredValue():
            # If primvar indices exist, create on dest primvar and set

            if src_pv_indices.ValueMightBeTimeVarying():
                for t in src_pv_indices.GetTimeSamples():
                    dst_pv.SetIndices(src_pv_indices.Get(t), t)
            else:
                dst_pv.SetIndices(src_pv_indices.Get())

        # Get attribs from primvar and set
        src_attr = src_pv.GetAttr()
        dst_attr = dst_pv.GetAttr()
        handle_attribute_transfer(src_attr, dst_attr)

        # if src_attr.ValueMightBeTimeVarying():
        #     for t in src_attr.GetTimeSamples():
        #         dst_attr.Set(src_attr.Get(t), t)
        # else:
        #     dst_attr.Set(src_attr.Get())


def transfer_all(src_prim: Usd.Prim, dst_prim: Usd.Prim):
    """
    Transfer everything from src_prim to dst_prim:
    - XformOps
    - Primvars
    - Generic attributes
    """
    
    # --- 1. XformOps ---
    if src_prim.IsA(UsdGeom.Xformable):
        transfer_xform_ops(src_prim, dst_prim)
    
    # --- 2. Primvars ---
    if src_prim.IsA(UsdGeom.Gprim):
        transfer_primvars(src_prim, dst_prim)
    
    # --- 3. Generic attributes (skip primvars) ---
    for attr in src_prim.GetAttributes():
        name = attr.GetName()
        if name.startswith("primvars:") or name.startswith("xformOp"):  # skip primvars; handled above
            continue
        if not attr.HasAuthoredValue():
            continue
        
        dst_attr = dst_prim.GetAttribute(name)
        if not dst_attr:
            dst_attr = dst_prim.CreateAttribute(name, attr.GetTypeName(), custom=True, variability=attr.GetVariability())
        
        if attr.ValueMightBeTimeVarying():
            for t in attr.GetTimeSamples():
                dst_attr.Set(attr.Get(t), t)
        else:
            dst_attr.Set(attr.Get())


def handle_attribute_transfer(new, old):

    if old.ValueMightBeTimeVarying():
        new.Clear()
        for t in old.GetTimeSamples():
            if float(t).is_integer():
                new.Set(old.Get(t), t)
            
    else:
        new.Set(old.Get())

