# Translated from OCCT src/ModelingData/TKBRep/GTests/BRep_Tool_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_BezierCurve, Geom_Circle, Geom_Plane
from nanocct.gp import gp, gp_Ax2, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location


def _box():
    maker = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _first(kind):
    exp = TopExp_Explorer(_box(), kind)
    assert exp.More()
    return exp.Current()


def test_BRep_Tool_Test_Pnt_FromVertex():
    p = BRep_Tool.Pnt_s(TopoDS.Vertex(_first(TopAbs_VERTEX)))
    c = Precision.Confusion_s()
    assert -c <= p.X() <= 10.0 + c
    assert -c <= p.Y() <= 20.0 + c
    assert -c <= p.Z() <= 30.0 + c


def test_BRep_Tool_Test_Tolerance_Vertex():
    assert BRep_Tool.Tolerance_s(TopoDS.Vertex(_first(TopAbs_VERTEX))) >= 0.0


def test_BRep_Tool_Test_Tolerance_Edge():
    assert BRep_Tool.Tolerance_s(TopoDS.Edge(_first(TopAbs_EDGE))) >= 0.0


def test_BRep_Tool_Test_Tolerance_Face():
    assert BRep_Tool.Tolerance_s(TopoDS.Face(_first(TopAbs_FACE))) >= 0.0


def test_BRep_Tool_Test_Curve_FromEdge():
    curve, first, last = BRep_Tool.Curve_s(TopoDS.Edge(_first(TopAbs_EDGE)))
    assert curve is not None
    assert first < last


def test_BRep_Tool_Test_Surface_FromFace():
    assert BRep_Tool.Surface_s(TopoDS.Face(_first(TopAbs_FACE))) is not None


def test_BRep_Tool_Test_IsClosed_CircleEdge():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp.DZ_s()), 5.0)
    maker = BRepBuilderAPI_MakeEdge(circle)
    assert maker.IsDone()
    assert BRep_Tool.IsClosed_s(maker.Edge())


def test_BRep_Tool_Test_IsClosed_LineEdge():
    maker = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0))
    assert maker.IsDone()
    assert not BRep_Tool.IsClosed_s(maker.Edge())


def test_BRep_Tool_Test_Degenerated():
    assert not BRep_Tool.Degenerated_s(TopoDS.Edge(_first(TopAbs_EDGE)))


def test_BRep_Tool_Test_CurveOnPlane_RejectsEdgeRangeOutsideBoundedCurve():
    poles = NCollection_Array1[gp_Pnt](1, 3)
    poles.SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, gp_Pnt(0.5, 0.25, 0.0))
    poles.SetValue(3, gp_Pnt(1.0, 0.0, 0.0))
    curve = Geom_BezierCurve(poles)
    maker = BRepBuilderAPI_MakeEdge(curve)
    assert maker.IsDone()
    edge = maker.Edge()
    first_in = -0.000002673149646
    last_in = 0.999997326850354
    BRep_Builder().Range(edge, first_in, last_in, True)
    plane = Geom_Plane(gp.XOY_s())
    # the bool* theIsStored out-pointer is not exposed by the binding; the isStored check is left out
    pcurve, first, last = BRep_Tool.CurveOnSurface_s(edge, plane, TopLoc_Location())
    assert pcurve is None
    assert first == first_in
    assert last == last_in


def test_BRep_Tool_Test_CurveOnPlane_ProjectsShiftedPeriodicRange():
    circle = Geom_Circle(gp_Ax2(gp.Origin_s(), gp.DZ_s()), 1.0)
    maker = BRepBuilderAPI_MakeEdge(circle)
    assert maker.IsDone()
    edge = maker.Edge()
    r1 = circle.Period()
    r2 = 2.0 * circle.Period()
    BRep_Builder().Range(edge, r1, r2, True)
    pcurve, first, last = BRep_Tool.CurveOnPlane_s(edge, Geom_Plane(gp.XOY_s()), TopLoc_Location())
    assert pcurve is not None
    assert first == r1
    assert last == r2


def test_BRep_Tool_Test_CurveOnPlane_ProjectsPeriodicEdgeBuiltFromEqualParameters():
    circle = Geom_Circle(gp_Ax2(gp.Origin_s(), gp.DZ_s()), 1.0)
    maker = BRepBuilderAPI_MakeEdge(circle, 0.0, 0.0)
    assert maker.IsDone()
    edge = maker.Edge()
    ef, el = BRep_Tool.Range_s(edge)
    assert abs((el - ef) - circle.Period()) <= Precision.PConfusion_s()
    pcurve, first, last = BRep_Tool.CurveOnPlane_s(edge, Geom_Plane(gp.XOY_s()), TopLoc_Location())
    assert pcurve is not None
    assert first == ef
    assert last == el


def test_BRep_Tool_Test_CurveOnPlane_RejectsEqualPeriodicRange():
    circle = Geom_Circle(gp_Ax2(gp.Origin_s(), gp.DZ_s()), 1.0)
    maker = BRepBuilderAPI_MakeEdge(circle)
    assert maker.IsDone()
    edge = maker.Edge()
    BRep_Builder().Range(edge, 0.0, 0.0, True)
    pcurve, first, last = BRep_Tool.CurveOnPlane_s(edge, Geom_Plane(gp.XOY_s()), TopLoc_Location())
    assert pcurve is None
    assert first == 0.0
    assert last == 0.0
