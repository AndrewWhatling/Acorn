from pxr import Usd, UsdShade, UsdGeom, Sdf


def recursive_move_prims(stage: Usd.Stage, root_prim: Usd.Prim, path: str) -> Usd.Stage:
    """
    Recursively reparents all given primitives to a new parent in the stage.

    Args:
        stage (Usd.Stage): Input Stage .
        root_prim (Usd.Prim): Primitive to loop over.
        path (str): New path to move primitive under.

    Returns:
        Usd.Stage: Stage with reparented prims.
    """
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


def set_prim_defaults(prim: Usd.Prim):
    """
    Sets intended default values on given primitive.

    Args:
        prim (Usd.Prim): Primitive to set default values on.
    """
    if prim.IsA("Mesh"):
        mesh = UsdGeom.Mesh(prim)
        mesh.GetNormalsAttr().Clear()
        mesh.GetSubdivisionSchemeAttr().Set("catmullClark")
        mesh.GetOrientationAttr().Set(UsdGeom.Tokens.rightHanded)


def transfer_material(from_prim: Usd.Prim, to_prim: Usd.Prim):
    """
    Creates a mat primvar on second primitive based on first primitives material.

    Args:
        from_prim (Usd.Prim): Primitive with material.
        to_prim (Usd.Prim): Primitive to put mat primvar on.
    """
    binding_api = UsdShade.MaterialBindingAPI(from_prim)
    material = binding_api.GetDirectBinding().GetMaterial()
    
    if material:
        name = str(material.GetPath()).split("/")[-1]
        primvars_api = UsdGeom.PrimvarsAPI(to_prim)
        var = primvars_api.CreatePrimvar("mat", Sdf.ValueTypeNames.String)
        var.Set(name)


def flatten_stage(stage: Usd.Stage) -> Usd.Stage:
    """
    Flattens Usd stage.

    Args:
        stage (Usd.Stage): Stage to flatten.

    Returns:
        Usd.Stage: Flattened Stage.
    """
    layer = stage.Flatten()
    return Usd.Stage.Open(layer)


def get_stage_root_prims(stage: Usd.Stage) -> list[Usd.Prim]:
    """
    Gets all primitives under root of the stage.

    Args:
        stage (Usd.Stage): Stage to get root primitives of.

    Returns:
        list[Usd.Prim]: List of primitives under root of stage.
    """
    root = stage.GetPrimAtPath("/")
    root_prims = []
    for child in root.GetChildren():
        root_prims.append(child)

    return root_prims


def define_asset_hierarchy(stage: Usd.Stage, path: str) -> Usd.Stage:
    """
    Creates primitives based on given path.

    Args:
        stage (Usd.Stage): Stage to define new primitives on.
        path (str): Path of new primitives to make.

    Returns:
        Usd.Stage: Stage with newly defined primitives.
    """
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
    """
    Removes all mesh primitives in Stage.

    Args:
        stage (Usd.Stage): Stage to remove meshes in.

    Returns:
        Usd.Stage: Stage with meshes removed.
    """
    to_remove = []

    for prim in stage.Traverse():
        if prim.IsA("Mesh"):
            to_remove.append(prim)

    for prim in to_remove:
        stage.RemovePrim(prim.GetPath())
    
    return stage


def remove_mats(stage: Usd.Stage) -> Usd.Stage:
    """
    Removes materials in Stage. 

    Args:
        stage (Usd.Stage): _description_

    Returns:
        Usd.Stage: _description_
    """

    "Currently designed to remove materials from USD files coming from Maya."
    to_remove = []

    for prim in stage.Traverse():
        if prim.GetName() == "mtl":
            to_remove.append(prim)

    for prim in to_remove:
        stage.RemovePrim(prim.GetPath())

    return stage


def create_new_camera(stage: Usd.Stage, path: str) -> Usd.Stage:
    """
    Creates camera primitive.

    Args:
        stage (Usd.Stage): Stage to create camera on.
        path (str): Path for the camera primitive to be made.

    Returns:
        Usd.Stage: Stage with camera primitive.
    """
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
        for src_attr in cam.GetAttributes():
            
            if not src_attr.HasAuthoredValue() or src_attr.GetName().startswith("xformOp"):
                continue
            
            dst_attr = new_prim.CreateAttribute(src_attr.GetName(), src_attr.GetTypeName())
            handle_attribute_transfer(src_attr, dst_attr)
        
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


def transfer_xform_ops(src_prim: Usd.Prim, dst_prim: Usd.Prim):
    """
    Transfers xforms from one primitive to another.

    Args:
        src_prim (Usd.Prim): Primitive to transfer xforms from.
        dst_prim (Usd.Prim): Primitive to transfer xforms to.
    """
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


def transfer_primvars(src_prim: Usd.Prim, dst_prim: Usd.Prim):
    """
    Transfers primvars from one primitive to another.

    Args:
        src_prim (Usd.Prim): Primitive to transfer primvars from.
        dst_prim (Usd.Prim): Primitive to transfer primvars to.
    """
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


def transfer_all(src_prim: Usd.Prim, dst_prim: Usd.Prim):
    """
    Transfers xforms, primvars and attributes from one primitive to another.

    Args:
        src_prim (Usd.Prim): Primitive to transfer values from.
        dst_prim (Usd.Prim): Primitive to transfer values to.
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
        
        handle_attribute_transfer(dst_attr, attr)


def handle_attribute_transfer(new: Usd.Attribute, old: Usd.Attribute):
    """
    Transfers one attribute from one primitive to another.

    Args:
        new (Usd.Attribute): Primitive to transfer values from.
        old (Usd.Attribute): Primitive to transfer values to.
    """

    if old.ValueMightBeTimeVarying() or old.GetNumTimeSamples() > 0:
        new.Clear()
        for t in old.GetTimeSamples():
            if float(t).is_integer():
                new.Set(old.Get(t), t)
            
    else:
        new.Set(old.Get())

