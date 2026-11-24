# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_BSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import Domain1D, ExtremaPC_BSplineCurve
from nanocct.Geom import Geom_BSplineCurve
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1

THE_TOL = 1.0e-6


def arr1(values, item_type):
    arr = NCollection_Array1[item_type](1, len(values))
    for idx, value in enumerate(values, start=1):
        arr[idx] = value
    return arr


def bspline(poles, knots, mults, degree):
    return Geom_BSplineCurve(arr1(poles, gp_Pnt), arr1(knots, float), arr1(mults, int), degree)


def create_cubic_bspline():
    return bspline([gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 2, 0), gp_Pnt(3, 0, 0)], [0.0, 1.0], [4, 4], 3)


def create_linear_bspline():
    return bspline([gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0)], [0.0, 1.0], [2, 2], 1)


def create_quadratic_bspline():
    return bspline([gp_Pnt(0, 0, 0), gp_Pnt(5, 10, 0), gp_Pnt(10, 0, 0)], [0.0, 1.0], [3, 3], 2)


def create_multi_span_bspline():
    poles = [gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 0, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0)]
    return bspline(poles, [0.0, 0.33, 0.67, 1.0], [3, 1, 1, 3], 2)


def create_3d_bspline():
    return bspline([gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 1), gp_Pnt(2, 1, 2), gp_Pnt(3, 0, 3)], [0.0, 1.0], [4, 4], 3)


def test_ExtremaPC_BSplineCurveTest_PointOnCurve_Start():
    bs = create_cubic_bspline()
    point = gp_Pnt(0.0, 0.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_PointOnCurve_End():
    bs = create_cubic_bspline()
    point = gp_Pnt(3.0, 0.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_PointOnCurve_Middle():
    bs = create_cubic_bspline()
    point = bs.Value(0.5)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_PointNearCurve_Above():
    bs = create_cubic_bspline()
    point = gp_Pnt(1.5, 3.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    min_sq = result.MinSquareDistance()
    assert min_sq > 0.0
    assert min_sq < 4.0


def test_ExtremaPC_BSplineCurveTest_PointNearCurve_Below():
    bs = create_cubic_bspline()
    point = gp_Pnt(1.5, -1.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    assert result.MinSquareDistance() >= 1.0


def test_ExtremaPC_BSplineCurveTest_PointNearCurve_OutOfPlane():
    bs = create_cubic_bspline()
    point = gp_Pnt(1.5, 2.0, 5.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert result.MinSquareDistance() >= 25.0


def test_ExtremaPC_BSplineCurveTest_LinearBSpline_PointOnLine():
    bs = create_linear_bspline()
    point = gp_Pnt(5.0, 0.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_LinearBSpline_PointOffLine():
    bs = create_linear_bspline()
    point = gp_Pnt(5.0, 3.0, 4.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(result.MinSquareDistance() - 25.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_QuadraticBSpline_PointNear():
    bs = create_quadratic_bspline()
    point = gp_Pnt(5.0, 8.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_QuadraticBSpline_PointOnApex():
    bs = create_quadratic_bspline()
    point = bs.Value(0.5)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_MultiSpanBSpline_PointNear():
    bs = create_multi_span_bspline()
    point = gp_Pnt(2.5, 3.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    assert math.sqrt(result.MinSquareDistance()) < 2.0


def test_ExtremaPC_BSplineCurveTest_MultiSpanBSpline_MultipleExtrema():
    bs = create_multi_span_bspline()
    point = gp_Pnt(2.5, 1.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        on_curve = bs.Value(result[i].Parameter)
        assert abs(result[i].Point.Distance(on_curve) - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_BSpline3D_PointOn():
    bs = create_3d_bspline()
    point = bs.Value(0.5)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert abs(result.MinSquareDistance() - 0.0) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_BSpline3D_PointNear():
    bs = create_3d_bspline()
    point = gp_Pnt(1.5, 2.0, 1.5)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_PartialRange_FirstHalf():
    bs = create_cubic_bspline()
    point = gp_Pnt(2.5, 1.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs, Domain1D(0.0, 0.5))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        assert result[i].Parameter >= 0.0 - THE_TOL
        assert result[i].Parameter <= 0.5 + THE_TOL


def test_ExtremaPC_BSplineCurveTest_PartialRange_SecondHalf():
    bs = create_cubic_bspline()
    point = gp_Pnt(0.5, 1.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs, Domain1D(0.5, 1.0))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        assert result[i].Parameter >= 0.5 - THE_TOL
        assert result[i].Parameter <= 1.0 + THE_TOL


def test_ExtremaPC_BSplineCurveTest_VerifyProjectedPoint():
    bs = create_cubic_bspline()
    point = gp_Pnt(1.5, 3.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.X() - on_curve.X()) <= THE_TOL
    assert abs(ext.Point.Y() - on_curve.Y()) <= THE_TOL
    assert abs(ext.Point.Z() - on_curve.Z()) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_VerifyDistanceConsistency():
    bs = create_cubic_bspline()
    point = gp_Pnt(2.0, 2.5, 1.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    computed_sq = point.SquareDistance(ext.Point)
    assert abs(ext.SquareDistance - computed_sq) <= THE_TOL


def test_ExtremaPC_BSplineCurveTest_RefinementConfig_DisableRefinement():
    bs = create_cubic_bspline()
    point = gp_Pnt(1.5, 2.0, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1


def test_ExtremaPC_BSplineCurveTest_HighDegreeSpline_RefinementHelps():
    poles = [
        gp_Pnt(0.0, 0.0, 0.0),
        gp_Pnt(0.5, 1.0, 0.0),
        gp_Pnt(1.0, -0.5, 0.0),
        gp_Pnt(1.5, 1.5, 0.0),
        gp_Pnt(2.0, 0.0, 0.0),
        gp_Pnt(2.5, 1.0, 0.0),
        gp_Pnt(3.0, -0.5, 0.0),
        gp_Pnt(3.5, 0.5, 0.0),
    ]
    bs = bspline(poles, [0.0, 1.0], [8, 8], 7)
    point = gp_Pnt(1.75, 0.8, 0.0)
    ev = ExtremaPC_BSplineCurve(bs)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    ext = result[result.MinIndex()]
    on_curve = bs.Value(ext.Parameter)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= THE_TOL
    assert math.sqrt(result.MinSquareDistance()) < 2.0
