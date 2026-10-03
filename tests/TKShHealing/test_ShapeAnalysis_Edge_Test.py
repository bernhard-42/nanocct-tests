# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeAnalysis_Edge_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Circle
from nanocct.gp import gp, gp_Ax2, gp_Pnt
from nanocct.ShapeAnalysis import ShapeAnalysis_Edge
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _line_edge():
    maker = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0))
    assert maker.IsDone()
    return maker.Edge()


def test_ShapeAnalysis_EdgeTest_HasCurve3d():
    assert ShapeAnalysis_Edge().HasCurve3d(_line_edge())


def test_ShapeAnalysis_EdgeTest_FirstVertex_LastVertex():
    edge = _line_edge()
    analyzer = ShapeAnalysis_Edge()
    assert not analyzer.FirstVertex(edge).IsNull()
    assert not analyzer.LastVertex(edge).IsNull()


def test_ShapeAnalysis_EdgeTest_IsClosed_OpenEdge():
    assert not ShapeAnalysis_Edge().IsClosed3d(_line_edge())


def test_ShapeAnalysis_EdgeTest_IsClosed_ClosedEdge():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp.DZ_s()), 5.0)
    maker = BRepBuilderAPI_MakeEdge(circle)
    assert maker.IsDone()
    assert ShapeAnalysis_Edge().IsClosed3d(maker.Edge())


def test_ShapeAnalysis_EdgeTest_IsSeam_NonSeam():
    maker = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    box = maker.Shape()
    assert maker.IsDone()
    face_exp = TopExp_Explorer(box, TopAbs_FACE)
    assert face_exp.More()
    face = TopoDS.Face(face_exp.Current())
    edge_exp = TopExp_Explorer(face, TopAbs_EDGE)
    assert edge_exp.More()
    edge = TopoDS.Edge(edge_exp.Current())
    assert not ShapeAnalysis_Edge().IsSeam(edge, face)
