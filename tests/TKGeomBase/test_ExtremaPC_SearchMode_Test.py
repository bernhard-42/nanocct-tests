# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_SearchMode_Test.cxx (LGPL-2.1 with the OCCT exception)
# The *_RandomPoints_* cases draw from std::mt19937 with std::uniform_real_distribution; Python's random.Random
# with the same seeds, ranges and counts gives a different (but equally deterministic) point sequence.
import math
import random

from nanocct.Extrema import Extrema_ExtPC
from nanocct.ExtremaPC import ExtremaPC_Curve, SearchMode
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
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import RealLast
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt

TOL = 1.0e-6


def _old_min_distance(old):
    if not old.IsDone() or old.NbExt() == 0:
        return RealLast()
    min_sq = RealLast()
    for i in range(1, old.NbExt() + 1):
        if old.SquareDistance(i) < min_sq:
            min_sq = old.SquareDistance(i)
    return math.sqrt(min_sq)


def _old_max_distance(old):
    if not old.IsDone() or old.NbExt() == 0:
        return 0.0
    max_sq = 0.0
    for i in range(1, old.NbExt() + 1):
        if old.SquareDistance(i) > max_sq:
            max_sq = old.SquareDistance(i)
    return math.sqrt(max_sq)


def _xy_ax2():
    return gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _line(umin, umax):
    return GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), umin, umax)


def _circle(*bounds):
    return GeomAdaptor_Curve(Geom_Circle(_xy_ax2(), 10.0), *bounds)


def _ellipse():
    return GeomAdaptor_Curve(Geom_Ellipse(_xy_ax2(), 20.0, 10.0))


def _parabola():
    return GeomAdaptor_Curve(Geom_Parabola(_xy_ax2(), 5.0), -20.0, 20.0)


def _hyperbola():
    return GeomAdaptor_Curve(Geom_Hyperbola(_xy_ax2(), 10.0, 5.0), -2.0, 2.0)


def _poles(*pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        a.SetValue(i, gp_Pnt(*p))
    return a


def _bspline():
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 4)
    mults.SetValue(2, 4)
    poles = _poles((0, 0, 0), (1, 2, 0), (3, 2, 0), (4, 0, 0))
    return GeomAdaptor_Curve(Geom_BSplineCurve(poles, knots, mults, 3))


def _bezier():
    return GeomAdaptor_Curve(Geom_BezierCurve(_poles((0, 0, 0), (1, 3, 0), (3, 3, 0), (4, 0, 0))))


def _offset_circle():
    return GeomAdaptor_Curve(Geom_OffsetCurve(Geom_Circle(_xy_ax2(), 10.0), 5.0, gp_Dir(0, 0, 1)))


def _check_valid_extremum(adaptor, ext, umin, umax, point_tol):
    assert ext.Parameter >= umin - TOL
    assert ext.Parameter <= umax + TOL
    assert abs(adaptor.Value(ext.Parameter).Distance(ext.Point) - 0.0) <= point_tol


def test_ExtremaPC_SearchModeTest_Line_MinMode():
    adaptor = _line(-100.0, 100.0)
    point = gp_Pnt(25.0, 10.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 1
    new_min = math.sqrt(res.MinSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= TOL
    assert abs(new_min - 10.0) <= TOL


def test_ExtremaPC_SearchModeTest_Line_MaxMode():
    adaptor = _line(-50.0, 50.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.PerformWithEndpoints(gp_Pnt(0.0, 10.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(math.sqrt(res.MaxSquareDistance()) - math.sqrt(2600.0)) <= TOL


def test_ExtremaPC_SearchModeTest_Line_MinMaxMode():
    adaptor = _line(-50.0, 50.0)
    point = gp_Pnt(10.0, 5.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.MinMax)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    new_min = math.sqrt(res.MinSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= TOL
    assert abs(new_min - 5.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_MinMode_PointOutside():
    adaptor = _circle()
    point = gp_Pnt(20.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 1
    new_min = math.sqrt(res.MinSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= TOL
    assert abs(new_min - 10.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_MaxMode_PointOutside():
    adaptor = _circle()
    point = gp_Pnt(20.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Max)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 1
    new_max = math.sqrt(res.MaxSquareDistance())
    assert abs(new_max - _old_max_distance(old)) <= TOL
    assert abs(new_max - 30.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_MinMode_PointInside():
    adaptor = _circle()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(3.0, 0.0, 0.0), TOL, SearchMode.Min)
    assert res.IsDone()
    assert res.NbExt() == 1
    assert abs(math.sqrt(res.MinSquareDistance()) - 7.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_MaxMode_PointInside():
    adaptor = _circle()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(3.0, 0.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    assert res.NbExt() == 1
    assert abs(math.sqrt(res.MaxSquareDistance()) - 13.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_MinMaxMode():
    adaptor = _circle()
    point = gp_Pnt(15.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.MinMax)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 2
    new_min = math.sqrt(res.MinSquareDistance())
    new_max = math.sqrt(res.MaxSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= TOL
    assert abs(new_max - _old_max_distance(old)) <= TOL
    assert abs(new_min - 5.0) <= TOL
    assert abs(new_max - 25.0) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_PartialArc_MinMode():
    adaptor = _circle(0.0, math.pi / 2.0)
    point = gp_Pnt(15.0, 15.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Circle_PartialArc_MaxMode():
    adaptor = _circle(0.0, math.pi / 2.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(15.0, 15.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    if res.NbExt() > 0:
        _check_valid_extremum(adaptor, res[res.MaxIndex()], 0.0, math.pi / 2.0, TOL)


def test_ExtremaPC_SearchModeTest_Ellipse_MinMode_OnMajorAxis():
    adaptor = _ellipse()
    point = gp_Pnt(30.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 1
    new_min = math.sqrt(res.MinSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= TOL
    assert abs(new_min - 10.0) <= TOL


def test_ExtremaPC_SearchModeTest_Ellipse_MaxMode_OnMajorAxis():
    adaptor = _ellipse()
    point = gp_Pnt(30.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Max)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert res.NbExt() == 1
    new_max = math.sqrt(res.MaxSquareDistance())
    assert abs(new_max - _old_max_distance(old)) <= TOL
    assert abs(new_max - 50.0) <= TOL


def test_ExtremaPC_SearchModeTest_Ellipse_MinMode_General():
    adaptor = _ellipse()
    point = gp_Pnt(15.0, 12.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Ellipse_MinMaxMode():
    adaptor = _ellipse()
    point = gp_Pnt(15.0, 8.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.MinMax)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL
    assert abs(math.sqrt(res.MaxSquareDistance()) - _old_max_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Parabola_MinMode_AtVertex():
    adaptor = _parabola()
    point = gp_Pnt(0.0, 5.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Parabola_MaxMode():
    adaptor = _parabola()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.PerformWithEndpoints(gp_Pnt(0.0, 5.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    assert res.NbExt() >= 1
    if res.NbExt() > 0:
        _check_valid_extremum(adaptor, res[res.MaxIndex()], -20.0, 20.0, TOL)


def test_ExtremaPC_SearchModeTest_Parabola_MinMode_OffAxis():
    adaptor = _parabola()
    point = gp_Pnt(10.0, -5.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Hyperbola_MinMode():
    adaptor = _hyperbola()
    point = gp_Pnt(20.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL


def test_ExtremaPC_SearchModeTest_Hyperbola_MaxMode():
    adaptor = _hyperbola()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(20.0, 0.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    if res.NbExt() > 0:
        _check_valid_extremum(adaptor, res[res.MaxIndex()], -2.0, 2.0, TOL)


def test_ExtremaPC_SearchModeTest_BSpline_MinMode():
    adaptor = _bspline()
    point = gp_Pnt(2.0, 3.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= 0.01


def test_ExtremaPC_SearchModeTest_BSpline_MaxMode():
    adaptor = _bspline()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(2.0, 1.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    if res.NbExt() > 0:
        _check_valid_extremum(adaptor, res[res.MaxIndex()], 0.0, 1.0, 0.01)


def test_ExtremaPC_SearchModeTest_BSpline_MinMaxMode():
    adaptor = _bspline()
    point = gp_Pnt(2.0, 1.5, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.MinMax)
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        _check_valid_extremum(adaptor, res[i], 0.0, 1.0, 0.01)
    old = Extrema_ExtPC(point, adaptor)
    if old.IsDone() and old.NbExt() > 0:
        assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= 0.05


def test_ExtremaPC_SearchModeTest_Bezier_MinMode():
    adaptor = _bezier()
    point = gp_Pnt(2.0, 4.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= 0.01


def test_ExtremaPC_SearchModeTest_Bezier_MaxMode():
    adaptor = _bezier()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.PerformWithEndpoints(gp_Pnt(2.0, 1.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(math.sqrt(res.MaxSquareDistance()) - math.sqrt(5.0)) <= 0.01


def test_ExtremaPC_SearchModeTest_OffsetCircle_MinMode():
    adaptor = _offset_circle()
    point = gp_Pnt(25.0, 0.0, 0.0)
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(point, TOL, SearchMode.Min)
    old = Extrema_ExtPC(point, adaptor)
    assert res.IsDone()
    new_min = math.sqrt(res.MinSquareDistance())
    assert abs(new_min - _old_min_distance(old)) <= 0.01
    assert abs(new_min - 10.0) <= 0.01


def test_ExtremaPC_SearchModeTest_OffsetCircle_MaxMode():
    adaptor = _offset_circle()
    ev = ExtremaPC_Curve(adaptor)
    res = ev.Perform(gp_Pnt(25.0, 0.0, 0.0), TOL, SearchMode.Max)
    assert res.IsDone()
    if res.NbExt() > 0:
        ext = res[res.MaxIndex()]
        assert abs(adaptor.Value(ext.Parameter).Distance(ext.Point) - 0.0) <= 0.01
        assert abs(math.sqrt(res.MaxSquareDistance()) - 40.0) <= 0.5


def _random_points_vs_old(adaptor, seed, mode):
    rng = random.Random(seed)
    for i in range(50):
        point = gp_Pnt(rng.uniform(-50.0, 50.0), rng.uniform(-50.0, 50.0), 0.0)
        ev = ExtremaPC_Curve(adaptor)
        res = ev.Perform(point, TOL, mode)
        old = Extrema_ExtPC(point, adaptor)
        if not old.IsDone():
            continue
        assert res.IsDone(), f"iteration {i}"
        if mode == SearchMode.Min:
            assert abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) <= TOL, f"iteration {i}"
        else:
            assert abs(math.sqrt(res.MaxSquareDistance()) - _old_max_distance(old)) <= TOL, f"iteration {i}"


def test_ExtremaPC_SearchModeTest_Circle_RandomPoints_MinMode():
    _random_points_vs_old(_circle(), 12345, SearchMode.Min)


def test_ExtremaPC_SearchModeTest_Circle_RandomPoints_MaxMode():
    _random_points_vs_old(_circle(), 12345, SearchMode.Max)


def test_ExtremaPC_SearchModeTest_Ellipse_RandomPoints_MinMode():
    _random_points_vs_old(_ellipse(), 54321, SearchMode.Min)


def test_ExtremaPC_SearchModeTest_BSpline_RandomPoints_MinMode():
    adaptor = _bspline()
    rng = random.Random(11111)
    pass_count = 0
    test_count = 0
    for _ in range(30):
        point = gp_Pnt(rng.uniform(-2.0, 6.0), rng.uniform(-2.0, 6.0), 0.0)
        ev = ExtremaPC_Curve(adaptor)
        res = ev.Perform(point, TOL, SearchMode.Min)
        old = Extrema_ExtPC(point, adaptor)
        if not old.IsDone() or old.NbExt() == 0:
            continue
        if not res.IsDone() or res.NbExt() == 0:
            continue
        test_count += 1
        if abs(math.sqrt(res.MinSquareDistance()) - _old_min_distance(old)) < 0.1:
            pass_count += 1
    if test_count > 0:
        rate = pass_count / test_count
        assert rate >= 0.8, f"pass rate {rate * 100}% ({pass_count}/{test_count})"
