# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import (
    Domain1D,
    ExtremaPC_Circle,
    ExtremaPC_Curve,
    ExtremaPC_Line,
    ExtremumResult,
    Result,
    SearchMode,
    Status,
)
from nanocct.Geom import (
    Geom_BezierCurve,
    Geom_BSplineCurve,
    Geom_Circle,
    Geom_Ellipse,
    Geom_Hyperbola,
    Geom_Line,
    Geom_OffsetCurve,
    Geom_Parabola,
    Geom_TrimmedCurve,
)
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_TransformedCurve
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Circ, gp_Dir, gp_Lin, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1

THE_TOL = 1.0e-6


def _near(value, expected, tol):
    assert abs(value - expected) <= tol, f"{value} != {expected} +- {tol}"


def _poles(points):
    poles = NCollection_Array1[gp_Pnt](1, len(points))
    for i, p in enumerate(points, 1):
        poles.SetValue(i, p)
    return poles


def _make_test_bspline():
    poles = _poles([gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 2, 0), gp_Pnt(3, 0, 0)])
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 4)
    mults.SetValue(2, 4)
    return Geom_BSplineCurve(poles, knots, mults, 3)


def _make_test_bezier():
    return Geom_BezierCurve(_poles([gp_Pnt(0, 0, 0), gp_Pnt(1, 3, 0), gp_Pnt(3, 3, 0), gp_Pnt(4, 0, 0)]))


def _xy_circle(radius):
    return Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), radius)


# Line tests


def test_ExtremaPC_CurveTest_Line_PointOnLine():
    line = gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    point = gp_Pnt(5.0, 0.0, 0.0)
    ev = ExtremaPC_Line(line, Domain1D(0.0, 100.0))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 3
    i = result.MinIndex()
    _near(result[i].Parameter, 5.0, THE_TOL)
    _near(result[i].SquareDistance, 0.0, THE_TOL)
    assert result[i].IsMinimum


def test_ExtremaPC_CurveTest_Line_PointOffLine():
    line = gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    point = gp_Pnt(5.0, 3.0, 4.0)
    ev = ExtremaPC_Line(line, Domain1D(0.0, 100.0))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 3
    i = result.MinIndex()
    _near(result[i].Parameter, 5.0, THE_TOL)
    _near(result[i].SquareDistance, 25.0, THE_TOL)
    assert result[i].IsMinimum


def test_ExtremaPC_CurveTest_Line_ProjectionOutsideBounds():
    line = gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    point = gp_Pnt(-50.0, 3.0, 4.0)
    ev = ExtremaPC_Line(line, Domain1D(0.0, 100.0))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    i = result.MinIndex()
    _near(result[i].Parameter, 0.0, THE_TOL)


# Circle tests


def test_ExtremaPC_CurveTest_Circle_PointOutside():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    point = gp_Pnt(20.0, 0.0, 0.0)
    ev = ExtremaPC_Circle(circle, Domain1D(0.0, 2.0 * math.pi))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    i_min = 0 if result[0].SquareDistance < result[1].SquareDistance else 1
    i_max = 1 - i_min
    _near(math.sqrt(result[i_min].SquareDistance), 10.0, THE_TOL)
    assert result[i_min].IsMinimum
    _near(math.sqrt(result[i_max].SquareDistance), 30.0, THE_TOL)
    assert not result[i_max].IsMinimum


def test_ExtremaPC_CurveTest_Circle_PointInside():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    point = gp_Pnt(3.0, 0.0, 0.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_dist = min(math.sqrt(result[0].SquareDistance), math.sqrt(result[1].SquareDistance))
    _near(min_dist, 7.0, THE_TOL)


def test_ExtremaPC_CurveTest_Circle_PointAtCenter_Degenerate():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    point = gp_Pnt(0.0, 0.0, 0.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsInfinite()
    _near(math.sqrt(result.InfiniteSquareDistance), 10.0, THE_TOL)


# Aggregator tests with GeomAdaptor_Curve


def test_ExtremaPC_CurveTest_Aggregator_Line():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -100.0, 100.0)
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    point = gp_Pnt(5.0, 3.0, 4.0)
    result = ext.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 3
    i = result.MinIndex()
    _near(result[i].Parameter, 5.0, THE_TOL)
    _near(result[i].SquareDistance, 25.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_Circle():
    adaptor = GeomAdaptor_Curve(_xy_circle(10.0))
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_BSpline():
    adaptor = GeomAdaptor_Curve(_make_test_bspline())
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 0


def test_ExtremaPC_CurveTest_Aggregator_Ellipse():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 20.0, 10.0))
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_Parabola():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2.0), -10.0, 10.0)
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(2.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 2.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_Hyperbola():
    adaptor = GeomAdaptor_Curve(Geom_Hyperbola(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0, 5.0), -2.0, 2.0)
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    point = gp_Pnt(10.0, 5.0, 0.0)
    result = ext.Perform(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        _near(result[i].SquareDistance, point.SquareDistance(result[i].Point), THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_Bezier():
    adaptor = GeomAdaptor_Curve(_make_test_bezier())
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    point = gp_Pnt(2.0, 5.0, 0.0)
    result = ext.Perform(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        _near(result[i].SquareDistance, point.SquareDistance(result[i].Point), THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_OffsetCurve():
    adaptor = GeomAdaptor_Curve(Geom_OffsetCurve(_xy_circle(10.0), 5.0, gp_Dir(0, 0, 1)))
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(25.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_TrimmedCurve():
    adaptor = GeomAdaptor_Curve(Geom_TrimmedCurve(_xy_circle(10.0), 0.0, math.pi / 2.0))
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(15.0, 15.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        assert result[i].Parameter >= -THE_TOL
        assert result[i].Parameter <= math.pi / 2.0 + THE_TOL


# Edge case tests


def test_ExtremaPC_CurveTest_Aggregator_PointOnCurve():
    adaptor = GeomAdaptor_Curve(_xy_circle(10.0))
    ext = ExtremaPC_Curve(adaptor)
    result = ext.Perform(gp_Pnt(10.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 0.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_IsInitialized():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 100.0)
    ext = ExtremaPC_Curve(adaptor)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(50.0, 5.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(result[0].Parameter, 50.0, THE_TOL)


# Result utility tests


def test_ExtremaPC_CurveTest_Result_MinSquareDistance():
    result = Result()
    result.Status = Status.OK
    for sq in (100.0, 50.0, 75.0):
        ext = ExtremumResult()
        ext.SquareDistance = sq
        result.Extrema.Append(ext)
    _near(result.MinSquareDistance(), 50.0, THE_TOL)
    assert result.MinIndex() == 1


def test_ExtremaPC_CurveTest_Result_Empty():
    result = Result()
    assert not result.IsDone()
    assert result.NbExt() == 0
    assert result.MinIndex() == -1
    assert math.isinf(result.MinSquareDistance())


# SearchMode tests


def test_ExtremaPC_CurveTest_Circle_SearchMode_MinMax():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL, SearchMode.MinMax)
    assert result.IsDone()
    assert result.NbExt() == 2


def test_ExtremaPC_CurveTest_Circle_SearchMode_Min():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL, SearchMode.Min)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_Circle_SearchMode_Max():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL, SearchMode.Max)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert not result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 30.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_SearchMode_Min():
    adaptor = GeomAdaptor_Curve(_xy_circle(10.0))
    ext = ExtremaPC_Curve(adaptor)
    result = ext.Perform(gp_Pnt(20.0, 0.0, 0.0), THE_TOL, SearchMode.Min)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_SearchMode_Max():
    adaptor = GeomAdaptor_Curve(_xy_circle(10.0))
    ext = ExtremaPC_Curve(adaptor)
    result = ext.Perform(gp_Pnt(20.0, 0.0, 0.0), THE_TOL, SearchMode.Max)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert not result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 30.0, THE_TOL)


def test_ExtremaPC_CurveTest_Aggregator_BSpline_SearchMode_Min():
    adaptor = GeomAdaptor_Curve(_make_test_bspline())
    ext = ExtremaPC_Curve(adaptor)
    result = ext.Perform(gp_Pnt(1.5, 3.0, 0.0), THE_TOL, SearchMode.Min)
    assert result.IsDone()
    for i in range(result.NbExt()):
        assert result[i].IsMinimum


def test_ExtremaPC_CurveTest_Result_MaxSquareDistance():
    result = Result()
    result.Status = Status.OK
    for sq, is_min in ((100.0, False), (50.0, True), (75.0, False)):
        ext = ExtremumResult()
        ext.SquareDistance = sq
        ext.IsMinimum = is_min
        result.Extrema.Append(ext)
    _near(result.MinSquareDistance(), 50.0, THE_TOL)
    assert result.MinIndex() == 1
    _near(result.MaxSquareDistance(), 100.0, THE_TOL)
    assert result.MaxIndex() == 0


# GeomAdaptor_TransformedCurve - Identity transform


def test_ExtremaPC_CurveTest_TransformedCurve_Identity_LineMatchesNonTransformed():
    geom_line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    adaptor = GeomAdaptor_Curve(geom_line, -100.0, 100.0)
    ext = ExtremaPC_Curve(adaptor)
    transformed = GeomAdaptor_TransformedCurve(geom_line, -100.0, 100.0, gp_Trsf())
    ext_tr = ExtremaPC_Curve(transformed)
    assert ext.IsInitialized()
    assert ext_tr.IsInitialized()
    point = gp_Pnt(5.0, 3.0, 4.0)
    result = ext.Perform(point, THE_TOL)
    result_tr = ext_tr.Perform(point, THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    assert result.NbExt() == result_tr.NbExt()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Identity_BSplineMatchesNonTransformed():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    transformed = GeomAdaptor_TransformedCurve(bspline, gp_Trsf())
    ext_tr = ExtremaPC_Curve(transformed)
    point = gp_Pnt(1.5, 3.0, 0.0)
    result = ext.Perform(point, THE_TOL)
    result_tr = ext_tr.Perform(point, THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)


# GeomAdaptor_TransformedCurve - Translation


def test_ExtremaPC_CurveTest_TransformedCurve_Translation_Line():
    geom_line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 10, 0))
    transformed = GeomAdaptor_TransformedCurve(geom_line, -100.0, 100.0, trsf)
    ext = ExtremaPC_Curve(transformed)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(5.0, 13.0, 4.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    i = result.MinIndex()
    _near(result[i].Parameter, 5.0, THE_TOL)
    _near(result[i].SquareDistance, 25.0, THE_TOL)
    _near(result[i].Point.Y(), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Translation_Circle():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(100, 0, 0))
    transformed = GeomAdaptor_TransformedCurve(_xy_circle(10.0), trsf)
    ext = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(120.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Translation_BSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(10, 20, 30))
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    result_tr = ext_tr.Perform(gp_Pnt(11.5, 23.0, 30.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    assert result.NbExt() == result_tr.NbExt()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)
    i = result.MinIndex()
    i_tr = result_tr.MinIndex()
    _near(result[i].Parameter, result_tr[i_tr].Parameter, THE_TOL)
    _near(result_tr[i_tr].Point.X(), result[i].Point.X() + 10.0, THE_TOL)
    _near(result_tr[i_tr].Point.Y(), result[i].Point.Y() + 20.0, THE_TOL)
    _near(result_tr[i_tr].Point.Z(), result[i].Point.Z() + 30.0, THE_TOL)


# GeomAdaptor_TransformedCurve - Rotation


def test_ExtremaPC_CurveTest_TransformedCurve_Rotation_Line():
    geom_line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 2.0)
    transformed = GeomAdaptor_TransformedCurve(geom_line, 0.0, 100.0, trsf)
    ext = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(3.0, 5.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    i = result.MinIndex()
    _near(math.sqrt(result[i].SquareDistance), 3.0, THE_TOL)
    _near(result[i].Point.X(), 0.0, THE_TOL)
    _near(result[i].Point.Y(), 5.0, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Rotation_BSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 2.0)
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    result_tr = ext_tr.Perform(gp_Pnt(-3.0, 1.5, 0.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)
    _near(result[result.MinIndex()].Parameter, result_tr[result_tr.MinIndex()].Parameter, THE_TOL)


# GeomAdaptor_TransformedCurve - Compound transform (rotation + translation)


def test_ExtremaPC_CurveTest_TransformedCurve_Compound_BSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 4.0)
    transl = gp_Trsf()
    transl.SetTranslation(gp_Vec(5, 5, 0))
    trsf.Multiply(transl)
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    orig_point = gp_Pnt(1.5, 3.0, 0.0)
    trans_point = orig_point.Transformed(trsf)
    result = ext.Perform(orig_point, THE_TOL)
    result_tr = ext_tr.Perform(trans_point, THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)
    i = result.MinIndex()
    i_tr = result_tr.MinIndex()
    _near(result[i].Parameter, result_tr[i_tr].Parameter, THE_TOL)
    expected = result[i].Point.Transformed(trsf)
    _near(result_tr[i_tr].Point.X(), expected.X(), THE_TOL)
    _near(result_tr[i_tr].Point.Y(), expected.Y(), THE_TOL)
    _near(result_tr[i_tr].Point.Z(), expected.Z(), THE_TOL)


# GeomAdaptor_TransformedCurve - Uniform scale


def test_ExtremaPC_CurveTest_TransformedCurve_Scale_BSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(0, 0, 0), 2.0)
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    result_tr = ext_tr.Perform(gp_Pnt(3.0, 6.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result_tr.MinSquareDistance(), result.MinSquareDistance() * 4.0, THE_TOL)
    _near(result[result.MinIndex()].Parameter, result_tr[result_tr.MinIndex()].Parameter, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Scale_Bezier():
    bezier = _make_test_bezier()
    adaptor = GeomAdaptor_Curve(bezier)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(0, 0, 0), 3.0)
    transformed = GeomAdaptor_TransformedCurve(bezier, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(2.0, 5.0, 0.0), THE_TOL)
    result_tr = ext_tr.Perform(gp_Pnt(6.0, 15.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result_tr.MinSquareDistance(), result.MinSquareDistance() * 9.0, 1.0e-4)


# GeomAdaptor_TransformedCurve - Offset curve via Adaptor3d_Curve interface


def test_ExtremaPC_CurveTest_TransformedCurve_Translation_OffsetCurve():
    offset_curve = Geom_OffsetCurve(_xy_circle(10.0), 5.0, gp_Dir(0, 0, 1))
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(50, 0, 0))
    transformed = GeomAdaptor_TransformedCurve(offset_curve, trsf)
    ext = ExtremaPC_Curve(transformed)
    assert ext.IsInitialized()
    result = ext.Perform(gp_Pnt(75.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


# GeomAdaptor_TransformedCurve - Domain-limited


def test_ExtremaPC_CurveTest_TransformedCurve_DomainLimited_Circle():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, 50))
    transformed = GeomAdaptor_TransformedCurve(_xy_circle(10.0), 0.0, math.pi / 2.0, trsf)
    ext = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(15.0, 15.0, 50.0), THE_TOL)
    assert result.IsDone()
    for i in range(result.NbExt()):
        assert result[i].Parameter >= -THE_TOL
        assert result[i].Parameter <= math.pi / 2.0 + THE_TOL
        _near(result[i].Point.Z(), 50.0, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_DomainLimited_Constructor():
    geom_line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 5, 0))
    transformed = GeomAdaptor_TransformedCurve(geom_line, trsf)
    ext = ExtremaPC_Curve(transformed, 0.0, 10.0)
    result = ext.PerformWithEndpoints(gp_Pnt(5.0, 8.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    i = result.MinIndex()
    _near(result[i].Parameter, 5.0, THE_TOL)
    _near(result[i].SquareDistance, 9.0, THE_TOL)
    _near(result[i].Point.Y(), 5.0, THE_TOL)


# GeomAdaptor_TransformedCurve - PerformWithEndpoints


def test_ExtremaPC_CurveTest_TransformedCurve_PerformWithEndpoints_BSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, 10))
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.PerformWithEndpoints(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    result_tr = ext_tr.PerformWithEndpoints(gp_Pnt(1.5, 3.0, 10.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    assert result.NbExt() == result_tr.NbExt()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_PerformWithEndpoints_ScaledBSpline():
    bspline = _make_test_bspline()
    adaptor = GeomAdaptor_Curve(bspline)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(0, 0, 0), 2.0)
    transformed = GeomAdaptor_TransformedCurve(bspline, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.PerformWithEndpoints(gp_Pnt(1.5, 3.0, 0.0), THE_TOL)
    result_tr = ext_tr.PerformWithEndpoints(gp_Pnt(3.0, 6.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result_tr.MinSquareDistance(), result.MinSquareDistance() * 4.0, THE_TOL)


# GeomAdaptor_TransformedCurve - Bezier with transform


def test_ExtremaPC_CurveTest_TransformedCurve_Translation_Bezier():
    bezier = _make_test_bezier()
    adaptor = GeomAdaptor_Curve(bezier)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(10, 20, 30))
    transformed = GeomAdaptor_TransformedCurve(bezier, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(2.0, 5.0, 0.0), THE_TOL)
    result_tr = ext_tr.Perform(gp_Pnt(12.0, 25.0, 30.0), THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)
    i = result.MinIndex()
    i_tr = result_tr.MinIndex()
    expected = result[i].Point.Transformed(trsf)
    _near(result_tr[i_tr].Point.X(), expected.X(), THE_TOL)
    _near(result_tr[i_tr].Point.Y(), expected.Y(), THE_TOL)
    _near(result_tr[i_tr].Point.Z(), expected.Z(), THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_Compound_Bezier():
    bezier = _make_test_bezier()
    adaptor = GeomAdaptor_Curve(bezier)
    ext = ExtremaPC_Curve(adaptor)
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 3.0)
    transl = gp_Trsf()
    transl.SetTranslation(gp_Vec(10, 0, 0))
    trsf.Multiply(transl)
    transformed = GeomAdaptor_TransformedCurve(bezier, trsf)
    ext_tr = ExtremaPC_Curve(transformed)
    orig_point = gp_Pnt(2.0, 5.0, 0.0)
    trans_point = orig_point.Transformed(trsf)
    result = ext.Perform(orig_point, THE_TOL)
    result_tr = ext_tr.Perform(trans_point, THE_TOL)
    assert result.IsDone()
    assert result_tr.IsDone()
    _near(result.MinSquareDistance(), result_tr.MinSquareDistance(), THE_TOL)


# GeomAdaptor_TransformedCurve - SearchMode with transform


def test_ExtremaPC_CurveTest_TransformedCurve_SearchMode_Min():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, 5))
    transformed = GeomAdaptor_TransformedCurve(_xy_circle(10.0), trsf)
    ext = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(20.0, 0.0, 5.0), THE_TOL, SearchMode.Min)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 10.0, THE_TOL)


def test_ExtremaPC_CurveTest_TransformedCurve_SearchMode_Max():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, 5))
    transformed = GeomAdaptor_TransformedCurve(_xy_circle(10.0), trsf)
    ext = ExtremaPC_Curve(transformed)
    result = ext.Perform(gp_Pnt(20.0, 0.0, 5.0), THE_TOL, SearchMode.Max)
    assert result.IsDone()
    assert result.NbExt() == 1
    assert not result[0].IsMinimum
    _near(math.sqrt(result[0].SquareDistance), 30.0, THE_TOL)
