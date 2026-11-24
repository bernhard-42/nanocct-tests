# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Comparison_Test.cxx (LGPL-2.1 with the OCCT exception)
# Circle_RandomPoints and BSpline_RandomPoints use Python's random.Random (same seeds, same uniform ranges, same
# count) instead of std::mt19937 with std::uniform_real_distribution, so the 100 query points differ from the C++.
# The fixture's VerifyNewNotWorse helper is not called by any case and is not translated.
import math
import random

from nanocct.Extrema import Extrema_ExtPC
from nanocct.ExtremaPC import ExtremaPC_Curve
from nanocct.Geom import (
    Geom_BezierCurve,
    Geom_BSplineCurve,
    Geom_Circle,
    Geom_Ellipse,
    Geom_Hyperbola,
    Geom_Line,
    Geom_OffsetCurve,
    Geom_Parabola,
)
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import RealLast

THE_TOL = 1.0e-6
THE_TOL_REL = 1.0e-4


def arr1(values, item_type):
    arr = NCollection_Array1[item_type](1, len(values))
    for idx, value in enumerate(values, start=1):
        arr[idx] = value
    return arr


def bspline(poles, knots, mults, degree):
    return Geom_BSplineCurve(arr1(poles, gp_Pnt), arr1(knots, float), arr1(mults, int), degree)


def xy_ax2():
    return gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def cubic_bspline():
    return bspline([gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 2, 0), gp_Pnt(3, 0, 0)], [0.0, 1.0], [4, 4], 3)


def old_min_square_distance(old):
    old_min_sq = RealLast()
    for i in range(1, old.NbExt() + 1):
        old_min_sq = min(old_min_sq, old.SquareDistance(i))
    return old_min_sq


def compare_min_distance(new, old):
    assert new.IsDone()
    assert old.IsDone()

    old_min_sq = RealLast()
    old_min_idx = -1
    for i in range(1, old.NbExt() + 1):
        sq = old.SquareDistance(i)
        if sq < old_min_sq:
            old_min_sq = sq
            old_min_idx = i

    new_min_sq = new.MinSquareDistance()
    new_min_idx = new.MinIndex()

    if old_min_idx < 0 and new_min_idx < 0:
        return

    assert old_min_idx >= 1
    assert new_min_idx >= 0

    old_dist = math.sqrt(old_min_sq)
    new_dist = math.sqrt(new_min_sq)

    if old_dist > THE_TOL:
        rel_diff = abs(new_dist - old_dist) / old_dist
        assert rel_diff < THE_TOL_REL
    else:
        assert abs(new_dist - old_dist) <= THE_TOL

    old_param = old.Point(old_min_idx).Parameter()
    new_param = new[new_min_idx].Parameter
    if abs(new_dist - old_dist) < THE_TOL:
        if abs(new_param - old_param) > 0.1:
            assert abs(new_dist - old_dist) <= THE_TOL


def run_compare(adaptor, point):
    ext_pc = ExtremaPC_Curve(adaptor)
    new = ext_pc.Perform(point, THE_TOL)
    old = Extrema_ExtPC(point, adaptor)
    compare_min_distance(new, old)
    return ext_pc, new


def test_ExtremaPC_ComparisonTest_Line_PointOnLine():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -100.0, 100.0)
    run_compare(adaptor, gp_Pnt(5.0, 0.0, 0.0))


def test_ExtremaPC_ComparisonTest_Line_PointOffLine():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -100.0, 100.0)
    run_compare(adaptor, gp_Pnt(5.0, 3.0, 4.0))


def test_ExtremaPC_ComparisonTest_Circle_PointOutside():
    adaptor = GeomAdaptor_Curve(Geom_Circle(xy_ax2(), 10.0))
    run_compare(adaptor, gp_Pnt(20.0, 0.0, 0.0))


def test_ExtremaPC_ComparisonTest_Circle_PointInside():
    adaptor = GeomAdaptor_Curve(Geom_Circle(xy_ax2(), 10.0))
    run_compare(adaptor, gp_Pnt(3.0, 0.0, 0.0))


def test_ExtremaPC_ComparisonTest_Circle_PointOffPlane():
    adaptor = GeomAdaptor_Curve(Geom_Circle(xy_ax2(), 10.0))
    run_compare(adaptor, gp_Pnt(15.0, 0.0, 5.0))


def test_ExtremaPC_ComparisonTest_Ellipse_PointOnMajorAxis():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(xy_ax2(), 20.0, 10.0))
    run_compare(adaptor, gp_Pnt(30.0, 0.0, 0.0))


def test_ExtremaPC_ComparisonTest_Ellipse_PointGeneral():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(xy_ax2(), 20.0, 10.0))
    run_compare(adaptor, gp_Pnt(15.0, 12.0, 0.0))


def test_ExtremaPC_ComparisonTest_Parabola_PointNearVertex():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(xy_ax2(), 2.0), -10.0, 10.0)
    run_compare(adaptor, gp_Pnt(1.0, 2.0, 0.0))


def test_ExtremaPC_ComparisonTest_Hyperbola_PointNearBranch():
    adaptor = GeomAdaptor_Curve(Geom_Hyperbola(xy_ax2(), 10.0, 5.0), -2.0, 2.0)
    run_compare(adaptor, gp_Pnt(15.0, 3.0, 0.0))


def test_ExtremaPC_ComparisonTest_BSpline_CubicCurve():
    adaptor = GeomAdaptor_Curve(cubic_bspline())
    run_compare(adaptor, gp_Pnt(1.5, 3.0, 0.0))


def test_ExtremaPC_ComparisonTest_BSpline_MultiSpan():
    poles = [gp_Pnt(0, 0, 0), gp_Pnt(1, 3, 0), gp_Pnt(2, 0, 0), gp_Pnt(3, 3, 0), gp_Pnt(4, 0, 0), gp_Pnt(5, 3, 0)]
    adaptor = GeomAdaptor_Curve(bspline(poles, [0.0, 0.33, 0.67, 1.0], [3, 1, 2, 3], 2))
    point = gp_Pnt(3.0, 4.0, 0.0)

    ext_pc = ExtremaPC_Curve(adaptor)
    new = ext_pc.Perform(point, THE_TOL)
    old = Extrema_ExtPC(point, adaptor)

    # As in the C++: only completion and that the found point lies on the curve are checked.
    assert new.IsDone()
    assert new.NbExt() > 0
    if new.NbExt() > 0:
        ext = new[new.MinIndex()]
        curve_pnt = adaptor.Value(ext.Parameter)
        assert abs(curve_pnt.Distance(ext.Point) - 0.0) <= 1.0e-6

    if old.IsDone() and old.NbExt() > 0 and new.NbExt() > 0:
        old_min_dist = math.sqrt(old_min_square_distance(old))
        new_min_dist = math.sqrt(new.MinSquareDistance())
        print(f"  [INFO] BSpline_MultiSpan: Old min dist = {old_min_dist}, New min dist = {new_min_dist}")


def test_ExtremaPC_ComparisonTest_Bezier_CubicCurve():
    poles = [gp_Pnt(0, 0, 0), gp_Pnt(1, 3, 0), gp_Pnt(3, 3, 0), gp_Pnt(4, 0, 0)]
    adaptor = GeomAdaptor_Curve(Geom_BezierCurve(arr1(poles, gp_Pnt)))
    run_compare(adaptor, gp_Pnt(2.0, 4.0, 0.0))


def test_ExtremaPC_ComparisonTest_OffsetCircle():
    offset_curve = Geom_OffsetCurve(Geom_Circle(xy_ax2(), 10.0), 5.0, gp_Dir(0, 0, 1))
    adaptor = GeomAdaptor_Curve(offset_curve)
    run_compare(adaptor, gp_Pnt(25.0, 0.0, 0.0))


def count_worse_random(adaptor, seed, low, high, num_tests=100):
    rng = random.Random(seed)
    fail_count = 0
    for _ in range(num_tests):
        point = gp_Pnt(rng.uniform(low, high), rng.uniform(low, high), rng.uniform(low, high))
        ext_pc = ExtremaPC_Curve(adaptor)
        new = ext_pc.Perform(point, THE_TOL)
        old = Extrema_ExtPC(point, adaptor)
        if new.IsDone() and old.IsDone() and new.NbExt() > 0 and old.NbExt() > 0:
            new_min = math.sqrt(new.MinSquareDistance())
            old_min = RealLast()
            for j in range(1, old.NbExt() + 1):
                old_min = min(old_min, math.sqrt(old.SquareDistance(j)))
            if new_min > old_min * (1.0 + THE_TOL_REL) + THE_TOL:
                fail_count += 1
    return fail_count


def test_ExtremaPC_ComparisonTest_Circle_RandomPoints():
    adaptor = GeomAdaptor_Curve(Geom_Circle(xy_ax2(), 10.0))
    assert count_worse_random(adaptor, 12345, -30.0, 30.0) == 0


def test_ExtremaPC_ComparisonTest_BSpline_RandomPoints():
    poles = [gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 1), gp_Pnt(2, 1, 2), gp_Pnt(3, 3, 1), gp_Pnt(4, 0, 0)]
    adaptor = GeomAdaptor_Curve(bspline(poles, [0.0, 0.33, 0.67, 1.0], [3, 1, 1, 3], 2))
    assert count_worse_random(adaptor, 54321, -2.0, 7.0) == 0


def test_ExtremaPC_ComparisonTest_PointOnCurve_Circle():
    adaptor = GeomAdaptor_Curve(Geom_Circle(xy_ax2(), 10.0))
    _ext_pc, new = run_compare(adaptor, gp_Pnt(10.0, 0.0, 0.0))
    assert math.sqrt(new.MinSquareDistance()) < THE_TOL


def test_ExtremaPC_ComparisonTest_PointOnCurve_BSpline():
    bs = cubic_bspline()
    adaptor = GeomAdaptor_Curve(bs)
    point = bs.Value(0.5)
    _ext_pc, new = run_compare(adaptor, point)
    assert math.sqrt(new.MinSquareDistance()) < THE_TOL
