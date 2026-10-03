# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dHatch_Elements_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom2d import Geom2d_Circle
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dHatch import Geom2dHatch_Element, Geom2dHatch_Elements
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d
from nanocct.TopAbs import TopAbs_FORWARD


def _circle_element():
    circle = Geom2d_Circle(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 1.0)
    return Geom2dHatch_Element(Geom2dAdaptor_Curve(circle), TopAbs_FORWARD)


def test_Geom2dHatch_Elements_CurrentEdge_ReturnsValidData():
    elements = Geom2dHatch_Elements()
    elements.Bind(1, _circle_element())
    elements.InitWires()
    assert elements.MoreWires()
    elements.InitEdges()
    assert elements.MoreEdges()
    edge = Geom2dAdaptor_Curve()
    orient = elements.CurrentEdge(edge)
    assert orient == TopAbs_FORWARD
    assert abs(edge.FirstParameter() - 0.0) <= 1e-10
    assert edge.LastParameter() > 6.0


def test_Geom2dHatch_Elements_BindAndFind():
    elements = Geom2dHatch_Elements()
    assert not elements.IsBound(1)
    elements.Bind(1, _circle_element())
    assert elements.IsBound(1)
    assert elements.Find(1).Orientation() == TopAbs_FORWARD


def test_Geom2dHatch_Elements_Clear_RemovesAll():
    elements = Geom2dHatch_Elements()
    elements.Bind(1, _circle_element())
    elements.Bind(2, _circle_element())
    assert elements.IsBound(1)
    elements.Clear()
    assert not elements.IsBound(1)
    assert not elements.IsBound(2)
