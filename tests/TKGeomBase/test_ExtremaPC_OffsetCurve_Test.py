# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import Domain1D, ExtremaPC_OffsetCurve
from nanocct.Geom import Geom_Circle, Geom_Ellipse, Geom_Line, Geom_OffsetCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt

TOL = 1.0e-6


def _xy_ax2():
    return gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _offset_circle(offset=5.0):
    return GeomAdaptor_Curve(Geom_OffsetCurve(Geom_Circle(_xy_ax2(), 10.0), offset, gp_Dir(0, 0, 1)))


def _offset_ellipse():
    return GeomAdaptor_Curve(Geom_OffsetCurve(Geom_Ellipse(_xy_ax2(), 20.0, 10.0), 5.0, gp_Dir(0, 0, 1)))


def _min_dist(adaptor, point, expected):
    ev = ExtremaPC_OffsetCurve(adaptor)
    res = ev.PerformWithEndpoints(point, TOL)
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(math.sqrt(res.MinSquareDistance()) - expected) <= TOL


def _distance_consistency(point):
    adaptor = _offset_circle()
    ev = ExtremaPC_OffsetCurve(adaptor)
    res = ev.PerformWithEndpoints(point, TOL)
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert abs(res[i].SquareDistance - point.SquareDistance(res[i].Point)) <= TOL, f"extremum {i}"


def test_ExtremaPC_OffsetCurveTest_OffsetCircle_PointOutside():
    _min_dist(_offset_circle(), gp_Pnt(30.0, 0.0, 0.0), 15.0)


def test_ExtremaPC_OffsetCurveTest_OffsetCircle_PointInside():
    _min_dist(_offset_circle(), gp_Pnt(12.0, 0.0, 0.0), 3.0)


def test_ExtremaPC_OffsetCurveTest_OffsetCircle_NegativeOffset():
    _min_dist(_offset_circle(-5.0), gp_Pnt(20.0, 0.0, 0.0), 15.0)


def test_ExtremaPC_OffsetCurveTest_OffsetCircle_PointOnOffsetCurve():
    _min_dist(_offset_circle(), gp_Pnt(15.0, 0.0, 0.0), 0.0)


def test_ExtremaPC_OffsetCurveTest_OffsetEllipse_PointOutside():
    _min_dist(_offset_ellipse(), gp_Pnt(40.0, 0.0, 0.0), 15.0)


def test_ExtremaPC_OffsetCurveTest_OffsetEllipse_PointOnMinorAxis():
    _min_dist(_offset_ellipse(), gp_Pnt(0.0, 25.0, 0.0), 10.0)


def test_ExtremaPC_OffsetCurveTest_OffsetLine_PointNear():
    line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    adaptor = GeomAdaptor_Curve(Geom_OffsetCurve(line, 5.0, gp_Dir(0, 0, 1)), 0.0, 100.0)
    offset_pt = adaptor.Value(50.0)
    _min_dist(adaptor, gp_Pnt(50.0, offset_pt.Y() + 5.0, 0.0), 5.0)


def test_ExtremaPC_OffsetCurveTest_PartialRange_FirstQuadrant():
    adaptor = _offset_circle()
    ev = ExtremaPC_OffsetCurve(adaptor, Domain1D(0.0, math.pi / 2.0))
    res = ev.PerformWithEndpoints(gp_Pnt(20.0, 20.0, 0.0), TOL)
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert res[i].Parameter >= -TOL
        assert res[i].Parameter <= math.pi / 2.0 + TOL


def test_ExtremaPC_OffsetCurveTest_OffsetCircle_PointOutOfPlane():
    _min_dist(_offset_circle(), gp_Pnt(15.0, 0.0, 10.0), 10.0)


def test_ExtremaPC_OffsetCurveTest_VerifyExtremumCondition():
    _distance_consistency(gp_Pnt(25.0, 0.0, 0.0))


def test_ExtremaPC_OffsetCurveTest_VerifyDistanceConsistency():
    _distance_consistency(gp_Pnt(18.0, 12.0, 3.0))
