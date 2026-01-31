from husd import UsdHoudini
from pxr import Sdf, UsdGeom, Gf
import hou


class PointDeformProcedural:
    def __init__(self):
        self.node = hou.pwd()
        self.name = self.node.name()
        self.parent = self.node.parent()


    def deform(self):
        node = self.node
        name = self.name
        parent = self.parent

        input_parms = ['geo', 'rest', 'deform']
        input_prim_paths = {}
        sel = hou.LopSelectionRule()

        for iparm in input_parms:
            parm = parent.parm(iparm)
            sel.setPathPattern(parm.eval())
            input_prim_paths[iparm] = sel.expandedPaths(node.inputs()[0])

        stage = node.editableStage()

        prim = stage.GetPrimAtPath(parent.evalParm('geo'))

        if prim.IsValid():

            pv_api = UsdGeom.PrimvarsAPI(prim)
            parms = ["rad",
                     "maxpts",
                     "minpts",
                     "piece"]
            
            args = { 'graph': node.evalParm('graph'), 'non_primvar_attrs': 'type wrap basis *',
                    'inputs': [], 'overrides': {} }
            
            # INPUTS
            for i, iname in enumerate(input_parms):
                rel_name = '{}:input_{}'.format(iname, i)
                if rel_name:
                    rel = prim.CreateRelationship(rel_name)
                    for path in input_prim_paths[iname]:
                        rel.AddTarget(path)
                    args['inputs'].append(rel_name)
                
                
            # OVERRIDES
            
            for p in parms:
                parm = node.parm(p)
                
                if parm:
                    parm = node.parm(p)
                    p_name = parm.name()
                    parm = node.parm(p_name)
                    pv_name = '{}:{}'.format(name, p_name)
                    val = parm.eval()
                    if type(val) == str:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.String)
                    elif type(val) == float:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Float)
                    elif type(val) == int:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Int)
                    else:
                        continue
                    pv.Set(parm.eval())
                    args['overrides'][p_name] = pv_name
            
                else:
                    parm = node.parmTuple(p)
                    p_name = parm.name()
                    pv_name = '{}:{}'.format(name, p_name)
                    parm_t = parm.parmTemplate()
                    n = parm_t.numComponents()        
                    datatype = parm_t.dataType()
                    val = parm.eval()
                    if n == 3 and datatype == hou.parmData.Float:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Vector3f)
                    elif n == 4 and datatype == hou.parmData.Float:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Vector4f)
                    elif n == 2 and datatype == hou.parmData.Float:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Float2)
                    elif n == 2 and datatype == hou.parmData.Int:
                        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.Int2)
                        val = Gf.Vec2i(val)
                    else:
                        continue
                    pv.Set(val)
                    args['overrides'][p_name] = pv_name
            
            
            hp_api = UsdHoudini.HoudiniProceduralAPI.Apply(prim, parent.name())
            hp_api.GetHoudiniProceduralPathAttr().Set('invokegraph.py')
            hp_api.GetHoudiniProceduralArgsAttr().Set(str(args))
            hp_api.GetHoudiniAnimatedAttr().Set(1)

