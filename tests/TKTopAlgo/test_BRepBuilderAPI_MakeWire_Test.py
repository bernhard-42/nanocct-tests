# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepBuilderAPI_MakeWire_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_List
from nanocct.TopoDS import TopoDS_Shape, TopoDS_Vertex


def _vertex(bb, pnt, tol):
    v = TopoDS_Vertex()
    bb.MakeVertex(v, pnt, tol)
    return v


def test_BRepBuilderAPI_MakeWire_Test_OCC27552_AddEdgesAndListOfEdges():
    bb = BRep_Builder()
    v1 = _vertex(bb, gp_Pnt(0, 0, 0), 0.1)
    v2 = _vertex(bb, gp_Pnt(5, 0, 0), 0.1)
    v3 = _vertex(bb, gp_Pnt(10, 0, 0), 0.1)
    e1 = BRepBuilderAPI_MakeEdge(v1, v2).Edge()
    e2 = BRepBuilderAPI_MakeEdge(v2, v3).Edge()
    mw = BRepBuilderAPI_MakeWire()
    mw.Add(e1)
    mw.Add(e2)
    v4 = _vertex(bb, gp_Pnt(10, 0.05, 0), 0.07)
    v5 = _vertex(bb, gp_Pnt(10, -0.05, 0), 0.07)
    v6 = _vertex(bb, gp_Pnt(10, 2, 0), 0.07)
    v7 = _vertex(bb, gp_Pnt(10, -2, 0), 0.07)
    e3 = BRepBuilderAPI_MakeEdge(v4, v6).Edge()
    e4 = BRepBuilderAPI_MakeEdge(v5, v7).Edge()
    edges = NCollection_List[TopoDS_Shape]()
    edges.Append(e3)
    edges.Append(e4)
    mw.Add(edges)
    assert mw.IsDone()
    assert not mw.Wire().IsNull()
