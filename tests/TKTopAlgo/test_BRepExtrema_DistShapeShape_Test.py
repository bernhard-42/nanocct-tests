# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepExtrema_DistShapeShape_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex
from nanocct.BRepExtrema import BRepExtrema_DistShapeShape
from nanocct.Geom import Geom_Circle
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pln, gp_Pnt


def test_BRepExtrema_DistShapeShapeTest_BUC60870_EdgeToVertexMinimumDistance():
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)).Edge()
    vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0.3, 1)).Vertex()
    dist = BRepExtrema_DistShapeShape(edge, vertex, 2.0)
    assert dist.IsDone()
    assert dist.NbSolution() >= 1
    assert abs(dist.Value() - 1.0) <= 1.0 * 0.01


def test_BRepExtrema_DistShapeShapeTest_EdgeEdge_Null3DCurve_NoCrash():
    edge1 = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0)).Edge()
    circle = Geom_Circle(gp_Ax2(gp_Pnt(5, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    edge2 = BRepBuilderAPI_MakeEdge(circle).Edge()
    BRep_Builder().UpdateEdge(edge2, None, 1e-7)
    BRepExtrema_DistShapeShape(edge1, edge2, 10.0)


def test_BRepExtrema_DistShapeShapeTest_EdgeFace_Null3DCurve_NoCrash():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(5, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    BRep_Builder().UpdateEdge(edge, None, 1e-7)
    face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0, 0, 5), gp_Dir(0, 0, 1)), -10, 10, -10, 10).Face()
    BRepExtrema_DistShapeShape(edge, face, 10.0)
