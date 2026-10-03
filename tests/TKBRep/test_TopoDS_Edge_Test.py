# Translated from OCCT src/ModelingData/TKBRep/GTests/TopoDS_Edge_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.gp import gp_Pnt


def test_TopoDS_Edge_Test_BUC60828_InfiniteFlag():
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.0, 0.0, 1.0)).Edge()
    assert edge.Infinite() is False
    edge.Infinite(True)
    assert edge.Infinite() is True
