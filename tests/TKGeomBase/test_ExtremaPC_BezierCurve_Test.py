# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_BezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import Domain1D, ExtremaPC_BezierCurve
from nanocct.Geom import Geom_BezierCurve
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

THE_TOL = 1.0e-6


def arr1(values, item_type):
    arr = NCollection_Array1[item_type](1, len(values))
    for idx, value in enumerate(values, start=1):
        arr[idx] = value
    return arr


def create_bezier(*poles):
    """Linear, quadratic, cubic or quartic Bezier curve from 2-5 poles (the fixture's create*Bezier helpers)."""
    return Geom_BezierCurve(arr1(list(poles), gp_Pnt))


def create_rational_quadratic_bezier(p0, p1, p2, w1):
    return Geom_BezierCurve(arr1([p0, p1, p2], gp_Pnt), arr1([1.0, w1, 1.0], float))


def create_3d_cubic_bezier():
    return create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 1), gp_Pnt(2, 2, 2), gp_Pnt(3, 0, 3))


def standard_cubic():
    return create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0))


def flat_cubic():
    return create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(2, 1, 0), gp_Pnt(3, 0, 0))


def wavy_quartic():
    return create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, -1, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0))


def assert_min_on_curve(bezier, result):
    ext = result[result.MinIndex()]
    on_curve = bezier.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    return ext, on_curve


def assert_all_on_curve(bezier, result):
    for i in range(result.NbExt()):
        on_curve = bezier.Value(result[i].Parameter)
        assert abs(result[i].Point.Distance(on_curve) - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_PointOnCurve_AtStart():
    bezier = standard_cubic()
    point = bezier.Value(0.0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_PointOnCurve_AtEnd():
    bezier = standard_cubic()
    point = bezier.Value(1.0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_PointOnCurve_AtMiddle():
    bezier = standard_cubic()
    point = bezier.Value(0.5)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_LinearBezier_PointProjection():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))
    point = gp_Pnt(5, 3, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 9.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_LinearBezier_PointAtPole():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))
    point = gp_Pnt(0, 0, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_LinearBezier_PointBeforeStart():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))
    point = gp_Pnt(-5, 0, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 25.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_QuadraticBezier_SymmetricArc():
    bezier = create_bezier(gp_Pnt(-2, 0, 0), gp_Pnt(0, 2, 0), gp_Pnt(2, 0, 0))
    point = gp_Pnt(0, 3, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    found_middle = False
    for i in range(result.NbExt()):
        if abs(result[i].Parameter - 0.5) < 0.01:
            found_middle = True
            break
    assert found_middle


def test_ExtremaPC_BezierCurveTest_QuadraticBezier_PointBelowApex():
    bezier = create_bezier(gp_Pnt(-2, 0, 0), gp_Pnt(0, 2, 0), gp_Pnt(2, 0, 0))
    point = gp_Pnt(0, 0, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_min_on_curve(bezier, result)
    assert math.sqrt(result.MinSquareDistance()) < 2.0


def test_ExtremaPC_BezierCurveTest_QuadraticBezier_AsymmetricArc():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(2, 4, 0), gp_Pnt(6, 0, 0))
    point = gp_Pnt(3, 3, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext, on_curve = assert_min_on_curve(bezier, result)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_CubicBezier_SCurve():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(0, 4, 0), gp_Pnt(4, -4, 0), gp_Pnt(4, 0, 0))
    point = gp_Pnt(2, 0, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_min_on_curve(bezier, result)


def test_ExtremaPC_BezierCurveTest_CubicBezier_LoopedCurve():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(4, 3, 0), gp_Pnt(-2, 3, 0), gp_Pnt(2, 0, 0))
    point = gp_Pnt(1, 1.5, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_all_on_curve(bezier, result)


def test_ExtremaPC_BezierCurveTest_CubicBezier_MultipleExtrema():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 3, 0), gp_Pnt(3, 3, 0), gp_Pnt(4, 0, 0))
    point = gp_Pnt(2, -1, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_all_on_curve(bezier, result)


def test_ExtremaPC_BezierCurveTest_QuarticBezier_WavyCurve():
    bezier = wavy_quartic()
    point = gp_Pnt(2, 1, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_all_on_curve(bezier, result)


def test_ExtremaPC_BezierCurveTest_QuarticBezier_PointOnCurve():
    bezier = wavy_quartic()
    point = bezier.Value(0.25)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_RationalQuadratic_CircularArc():
    w = 1.0 / math.sqrt(2.0)
    bezier = create_rational_quadratic_bezier(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(0, 1, 0), w)
    point = gp_Pnt(0, 0, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 1.0) <= 0.01


def test_ExtremaPC_BezierCurveTest_RationalQuadratic_HighWeight():
    bezier = create_rational_quadratic_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 0, 0), 3.0)
    point = gp_Pnt(1, 1.5, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext, on_curve = assert_min_on_curve(bezier, result)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_CubicBezier_3D_HelixLike():
    bezier = create_bezier(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 1), gp_Pnt(2, 1, 2), gp_Pnt(3, 0, 3))
    point = gp_Pnt(1.5, 0.5, 1.5)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext, on_curve = assert_min_on_curve(bezier, result)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_CubicBezier_3D_PointOnCurve():
    bezier = create_3d_cubic_bezier()
    point = bezier.Value(0.3)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_BoundedRange_ExtremumInside():
    bezier = standard_cubic()
    point = bezier.Value(0.5)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_BoundedRange_ExtremumAtBound():
    bezier = standard_cubic()
    point = bezier.Value(0.5)
    ev = ExtremaPC_BezierCurve(bezier, Domain1D(0.0, 0.3))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        u = result[i].Parameter
        assert u >= -0.001
        assert u <= 0.301


def test_ExtremaPC_BezierCurveTest_DegenerateBezier_AllPolesSame():
    bezier = create_bezier(gp_Pnt(1, 1, 1), gp_Pnt(1, 1, 1), gp_Pnt(1, 1, 1), gp_Pnt(1, 1, 1))
    point = gp_Pnt(2, 1, 1)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 1.0) <= THE_TOL


def test_ExtremaPC_BezierCurveTest_PointFarFromCurve():
    bezier = flat_cubic()
    point = gp_Pnt(100, 100, 100)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert_min_on_curve(bezier, result)
    assert math.sqrt(result.MinSquareDistance()) > 170.0


def test_ExtremaPC_BezierCurveTest_PointVeryCloseButNotOn():
    bezier = flat_cubic()
    on_curve = bezier.Value(0.5)
    point = gp_Pnt(on_curve.X(), on_curve.Y() + 1e-8, on_curve.Z())
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= 1e-12


def test_ExtremaPC_BezierCurveTest_VerifyExtremumCondition():
    bezier = standard_cubic()
    point = gp_Pnt(2, 3, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    interior_count = 0
    satisfied_count = 0
    for i in range(result.NbExt()):
        u = result[i].Parameter
        if u < 0.01 or u > 0.99:
            continue
        interior_count += 1
        curve_pnt = gp_Pnt()
        tangent = gp_Vec()
        bezier.D1(u, curve_pnt, tangent)
        vec = gp_Vec(curve_pnt, point)
        if abs(vec.Dot(tangent)) < 0.1:
            satisfied_count += 1
    if interior_count > 0:
        assert satisfied_count >= 1


def test_ExtremaPC_BezierCurveTest_ConsistentDistanceCalculation():
    bezier = flat_cubic()
    point = gp_Pnt(1.5, 2, 0)
    ev = ExtremaPC_BezierCurve(bezier)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        curve_pt = bezier.Value(result[i].Parameter)
        assert abs(result[i].SquareDistance - point.SquareDistance(curve_pt)) <= THE_TOL
