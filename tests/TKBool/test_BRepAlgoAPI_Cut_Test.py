# Translated from OCCT src/ModelingAlgorithms/TKBool/GTests/BRepAlgoAPI_Cut_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.Bnd import Bnd_Box
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from nanocct.BRepBndLib import BRepBndLib
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_SOLID
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape, TopoDS_Solid


def _volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def _solids(shape):
    result = []
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        sol = TopoDS.Solid(exp.Current())
        if not sol.IsNull():
            result.append(sol)
        exp.Next()
    return result


def _run_hollow_box_mesh_test(mesh_delta):
    delt = 5.0 * Precision.Confusion_s()
    full = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 30.0, 30.0, 30.0).Solid()
    inner = BRepPrimAPI_MakeBox(gp_Pnt(10, 10, 10), 10.0, 10.0, 10.0).Solid()
    cut = BRepAlgoAPI_Cut(full, inner)
    if not cut.IsDone():
        return -1.0
    solids = _solids(cut.Shape())
    if len(solids) != 1:
        return -1.0
    cut_solid = solids[-1]
    original = _volume(cut_solid)
    if original <= 0.0:
        return -1.0
    bnd = Bnd_Box()
    BRepBndLib.Add_s(cut_solid, bnd)
    xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get__float__float__float__float__float__float()
    xmin -= delt
    ymin -= delt
    zmin -= delt
    xmax += delt
    ymax += delt
    zmax += delt
    nx = max(int((xmax - xmin) / mesh_delta), 1)
    ny = max(int((ymax - ymin) / mesh_delta), 1)
    nz = max(int((zmax - zmin) / mesh_delta), 1)
    sx, sy, sz = (xmax - xmin) / nx, (ymax - ymin) / ny, (zmax - zmin) / nz
    subvols = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                cell = BRepPrimAPI_MakeBox(gp_Pnt(xmin + i * sx, ymin + j * sy, zmin + k * sz), sx, sy, sz).Solid()
                subvols.append((cell, _volume(cell)))
    accumulated = 0.0
    for cell, cell_vol in subvols:
        copy = BRepBuilderAPI_Copy(cut_solid).Shape()
        common = BRepAlgoAPI_Common(copy, cell)
        if not common.IsDone():
            continue
        found = _solids(common.Shape())
        if len(found) == 1:
            vol = _volume(found[0])
            if 0.0 < vol <= cell_vol:
                accumulated += vol
    return accumulated / original


def test_BRepAlgoAPI_CutTest_HollowBox_VolumeAccuracy_Delta10():
    ratio = _run_hollow_box_mesh_test(10.0)
    assert ratio >= 0.0
    assert abs(ratio - 1.0) <= 0.001


def test_BRepAlgoAPI_CutTest_HollowBox_VolumeAccuracy_Delta15():
    ratio = _run_hollow_box_mesh_test(15.0)
    assert ratio >= 0.0
    assert abs(ratio - 1.0) <= 0.001


def test_BRepAlgoAPI_CutTest_HollowBox_VolumeAccuracy_Delta30():
    ratio = _run_hollow_box_mesh_test(30.0)
    assert ratio >= 0.0
    assert abs(ratio - 1.0) <= 0.001


def test_BRepAlgoAPI_CutTest_HollowBox_SurfaceAreaAndValidity():
    full = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 30.0, 30.0, 30.0).Solid()
    inner = BRepPrimAPI_MakeBox(gp_Pnt(10, 10, 10), 10.0, 10.0, 10.0).Solid()
    cut = BRepAlgoAPI_Cut(full, inner)
    assert cut.IsDone()
    cut_solid = TopoDS_Solid()
    exp = TopExp_Explorer(cut.Shape(), TopAbs_SOLID)
    while exp.More():
        cut_solid = TopoDS.Solid(exp.Current())
        exp.Next()
    assert not cut_solid.IsNull()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(cut_solid, props)
    assert abs(props.Mass() - 6000.0) <= 6.0
    assert BRepCheck_Analyzer(cut_solid).IsValid()
