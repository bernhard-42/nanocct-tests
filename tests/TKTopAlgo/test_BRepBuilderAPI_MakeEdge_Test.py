# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepBuilderAPI_MakeEdge_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepGProp import BRepGProp
from nanocct.Geom import Geom_Circle, Geom_Line
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopExp import TopExp
from nanocct.TopoDS import TopoDS_Vertex


def _length(edge):
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(edge, props)
    return props.Mass()


def test_BRepBuilderAPI_MakeEdgeTest_LinearEdge_TwoPoints():
    mk = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0))
    assert mk.IsDone()
    edge = mk.Edge()
    assert not edge.IsNull()
    assert abs(_length(edge) - 10.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeEdgeTest_CircularEdge_Full():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 5.0)
    mk = BRepBuilderAPI_MakeEdge(circle)
    assert mk.IsDone()
    edge = mk.Edge()
    assert not edge.IsNull()
    assert abs(_length(edge) - 2.0 * math.pi * 5.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeEdgeTest_CircularEdge_Trimmed():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 5.0)
    mk = BRepBuilderAPI_MakeEdge(circle, 0.0, math.pi)
    assert mk.IsDone()
    edge = mk.Edge()
    assert not edge.IsNull()
    assert abs(_length(edge) - math.pi * 5.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeEdgeTest_EdgeFromLine_WithBounds():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    mk = BRepBuilderAPI_MakeEdge(line, 0.0, 7.0)
    assert mk.IsDone()
    edge = mk.Edge()
    assert not edge.IsNull()
    assert abs(_length(edge) - 7.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeEdgeTest_VertexExtraction():
    p1, p2 = gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0)
    mk = BRepBuilderAPI_MakeEdge(p1, p2)
    assert mk.IsDone()
    edge = mk.Edge()
    v1, v2 = TopoDS_Vertex(), TopoDS_Vertex()
    TopExp.Vertices_s(edge, v1, v2)
    assert not v1.IsNull()
    assert not v2.IsNull()
    assert BRep_Tool.Pnt_s(v1).IsEqual(p1, Precision.Confusion_s())
    assert BRep_Tool.Pnt_s(v2).IsEqual(p2, Precision.Confusion_s())


def test_BRepBuilderAPI_MakeEdgeTest_ToleranceCheck():
    mk = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0))
    assert mk.IsDone()
    tol = BRep_Tool.Tolerance_s(mk.Edge())
    assert tol > 0.0
    assert tol <= Precision.Confusion_s()
