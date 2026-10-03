# Translated from OCCT src/ModelingAlgorithms/TKBool/GTests/BRepFill_PipeShell_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepFill import BRepFill_PipeShell, BRepFill_Right
from nanocct.gp import gp_Pnt


def _square_profile(center, half):
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(gp_Pnt(center.X() - half, center.Y() - half, center.Z()))
    poly.Add(gp_Pnt(center.X() + half, center.Y() - half, center.Z()))
    poly.Add(gp_Pnt(center.X() + half, center.Y() + half, center.Z()))
    poly.Add(gp_Pnt(center.X() - half, center.Y() + half, center.Z()))
    poly.Close()
    return poly.Wire()


def test_BRepFill_PipeShellTest_MakeSolid_StraightSpineClosedProfile_ProducesClosedSolid():
    spine_edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.0, 0.0, 10.0)).Edge()
    spine = BRepBuilderAPI_MakeWire(spine_edge).Wire()
    profile = _square_profile(gp_Pnt(0.0, 0.0, 0.0), 1.0)
    pipe = BRepFill_PipeShell(spine)
    pipe.Add(profile)
    assert pipe.IsReady()
    assert pipe.Build()
    assert pipe.MakeSolid()
    result = pipe.Shape()
    assert not result.IsNull()
    assert result.Closed()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFill_PipeShellTest_MakeSolid_PolylineSpineClosedProfile_ProducesClosedSolid():
    spine_poly = BRepBuilderAPI_MakePolygon()
    spine_poly.Add(gp_Pnt(0.0, 0.0, 0.0))
    spine_poly.Add(gp_Pnt(0.0, 0.0, 5.0))
    spine_poly.Add(gp_Pnt(0.0, 5.0, 10.0))
    spine = spine_poly.Wire()
    profile = _square_profile(gp_Pnt(0.0, 0.0, 0.0), 0.5)
    pipe = BRepFill_PipeShell(spine)
    pipe.SetTransition(BRepFill_Right)
    pipe.Add(profile)
    assert pipe.IsReady()
    assert pipe.Build()
    assert pipe.MakeSolid()
    result = pipe.Shape()
    assert not result.IsNull()
    assert result.Closed()
