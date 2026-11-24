# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_ExtendedGeometry_Test.cxx (LGPL-2.1 with the OCCT exception)
# Random_Circle_100Points, Random_Ellipse_100Points, Random_Parabola_100Points: Python's random.Random with the C++
# seeds (12345, 54321, 11111) and uniform distributions over the same ranges, 3 draws per point and 100 points,
# instead of std::mt19937 with std::uniform_real_distribution; the point sequence differs from the C++ one.
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


def _near(value, expected, tol):
    assert abs(value - expected) <= tol, f"{value} != {expected} +- {tol}"


def _array(values, typ):
    arr = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        arr.SetValue(i, v)
    return arr


def _bspline(points, knots, mults, degree):
    return Geom_BSplineCurve(_array(points, gp_Pnt), _array(knots, float), _array(mults, int), degree)


def _bezier(points):
    return Geom_BezierCurve(_array(points, gp_Pnt))


def _ax2(origin, normal):
    return gp_Ax2(gp_Pnt(*origin), gp_Dir(*normal))


def _compare_min_distance(new, old, name, tol=THE_TOL):
    if not old.IsDone() or old.NbExt() == 0:
        return
    assert new.IsDone(), f"{name}: New implementation failed"
    assert new.NbExt() > 0, f"{name}: No extrema found"
    old_min_sq = RealLast()
    for i in range(1, old.NbExt() + 1):
        if old.SquareDistance(i) < old_min_sq:
            old_min_sq = old.SquareDistance(i)
    _near(math.sqrt(new.MinSquareDistance()), math.sqrt(old_min_sq), tol)


def _compare_max_distance(new, old, name, tol=THE_TOL):
    if not old.IsDone() or old.NbExt() == 0:
        return
    assert new.IsDone(), f"{name}: New implementation failed"
    assert new.NbExt() > 0, f"{name}: No extrema found"
    old_max_sq = 0.0
    for i in range(1, old.NbExt() + 1):
        if old.SquareDistance(i) > old_max_sq:
            old_max_sq = old.SquareDistance(i)
    _near(math.sqrt(new.MaxSquareDistance()), math.sqrt(old_max_sq), tol)


def _compare_min_max(new, old, name, tol=THE_TOL):
    _compare_min_distance(new, old, name, tol)
    _compare_max_distance(new, old, name, tol)


def _run(adaptor, point):
    """Returns (evaluator, new result, old Extrema_ExtPC); the evaluator owns the result."""
    ext = ExtremaPC_Curve(adaptor)
    result = ext.Perform(point, THE_TOL)
    old = Extrema_ExtPC(point, adaptor)
    return ext, result, old


# Transformed geometry tests - Circle


def test_ExtremaPC_ExtendedGeometryTest_Circle_Translated():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((100, 200, 50), (0, 0, 1)), 25.0))
    _ext, new, old = _run(adaptor, gp_Pnt(150.0, 200.0, 50.0))
    _compare_min_max(new, old, "Circle_Translated")


def test_ExtremaPC_ExtendedGeometryTest_Circle_Rotated_XY_Plane():
    normal = (1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0), 0)
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), normal), 15.0))
    _ext, new, old = _run(adaptor, gp_Pnt(20.0, 20.0, 5.0))
    _compare_min_max(new, old, "Circle_Rotated_XY")


def test_ExtremaPC_ExtendedGeometryTest_Circle_Rotated_XZ_Plane():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 1, 0)), 10.0))
    _ext, new, old = _run(adaptor, gp_Pnt(15.0, 5.0, 0.0))
    _compare_min_max(new, old, "Circle_Rotated_XZ")


def test_ExtremaPC_ExtendedGeometryTest_Circle_Rotated_YZ_Plane():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (1, 0, 0)), 10.0))
    _ext, new, old = _run(adaptor, gp_Pnt(5.0, 15.0, 0.0))
    _compare_min_max(new, old, "Circle_Rotated_YZ")


def test_ExtremaPC_ExtendedGeometryTest_Circle_Arbitrary_Orientation():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((10, 20, 30), (1, 1, 1)), 8.0))
    _ext, new, old = _run(adaptor, gp_Pnt(15.0, 25.0, 35.0))
    _compare_min_max(new, old, "Circle_Arbitrary")


def test_ExtremaPC_ExtendedGeometryTest_Circle_VerySmall():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 0.001))
    _ext, new, old = _run(adaptor, gp_Pnt(0.002, 0.0, 0.0))
    _compare_min_max(new, old, "Circle_VerySmall", 1.0e-9)


def test_ExtremaPC_ExtendedGeometryTest_Circle_VeryLarge():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 1000.0))
    _ext, new, old = _run(adaptor, gp_Pnt(1500.0, 0.0, 0.0))
    _compare_min_max(new, old, "Circle_VeryLarge")


# Transformed geometry tests - Ellipse


def test_ExtremaPC_ExtendedGeometryTest_Ellipse_Translated():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((50, 100, 25), (0, 0, 1)), 30.0, 15.0))
    _ext, new, old = _run(adaptor, gp_Pnt(90.0, 100.0, 25.0))
    _compare_min_max(new, old, "Ellipse_Translated")


def test_ExtremaPC_ExtendedGeometryTest_Ellipse_Rotated():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((0, 0, 0), (0, 1, 0)), 20.0, 8.0))
    _ext, new, old = _run(adaptor, gp_Pnt(25.0, 10.0, 5.0))
    _compare_min_max(new, old, "Ellipse_Rotated")


def test_ExtremaPC_ExtendedGeometryTest_Ellipse_HighEccentricity():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((0, 0, 0), (0, 0, 1)), 50.0, 2.0))
    _ext, new, old = _run(adaptor, gp_Pnt(40.0, 5.0, 0.0))
    _compare_min_max(new, old, "Ellipse_HighEccentricity")


def test_ExtremaPC_ExtendedGeometryTest_Ellipse_NearlyCircular():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((0, 0, 0), (0, 0, 1)), 10.1, 10.0))
    _ext, new, old = _run(adaptor, gp_Pnt(15.0, 8.0, 0.0))
    _compare_min_max(new, old, "Ellipse_NearlyCircular")


# Transformed geometry tests - Line


def test_ExtremaPC_ExtendedGeometryTest_Line_Diagonal():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 1, 1)), -100.0, 100.0)
    _ext, new, old = _run(adaptor, gp_Pnt(10.0, 0.0, 0.0))
    _compare_min_distance(new, old, "Line_Diagonal")


def test_ExtremaPC_ExtendedGeometryTest_Line_Arbitrary():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(10, 20, 30), gp_Dir(2, 3, 1)), -50.0, 50.0)
    _ext, new, old = _run(adaptor, gp_Pnt(25.0, 35.0, 40.0))
    _compare_min_distance(new, old, "Line_Arbitrary")


def test_ExtremaPC_ExtendedGeometryTest_Line_PointOnLine():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -100.0, 100.0)
    _ext, new, _old = _run(adaptor, gp_Pnt(50.0, 0.0, 0.0))
    assert new.IsDone()
    _near(math.sqrt(new.MinSquareDistance()), 0.0, THE_TOL)


# Parabola tests with different configurations


def test_ExtremaPC_ExtendedGeometryTest_Parabola_Translated():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(_ax2((10, 20, 0), (0, 0, 1)), 3.0), -15.0, 15.0)
    _ext, new, old = _run(adaptor, gp_Pnt(20.0, 30.0, 0.0))
    _compare_min_distance(new, old, "Parabola_Translated")


def test_ExtremaPC_ExtendedGeometryTest_Parabola_InXZPlane():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(_ax2((0, 0, 0), (0, 1, 0)), 5.0), -10.0, 10.0)
    _ext, new, old = _run(adaptor, gp_Pnt(5.0, 5.0, 10.0))
    _compare_min_distance(new, old, "Parabola_InXZPlane")


def test_ExtremaPC_ExtendedGeometryTest_Parabola_SmallFocalLength():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(_ax2((0, 0, 0), (0, 0, 1)), 0.5), -5.0, 5.0)
    _ext, new, old = _run(adaptor, gp_Pnt(2.0, 3.0, 0.0))
    _compare_min_distance(new, old, "Parabola_SmallFocalLength")


def test_ExtremaPC_ExtendedGeometryTest_Parabola_LargeFocalLength():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(_ax2((0, 0, 0), (0, 0, 1)), 50.0), -100.0, 100.0)
    _ext, new, old = _run(adaptor, gp_Pnt(50.0, 25.0, 0.0))
    _compare_min_distance(new, old, "Parabola_LargeFocalLength")


# Hyperbola tests with different configurations


def test_ExtremaPC_ExtendedGeometryTest_Hyperbola_Translated():
    adaptor = GeomAdaptor_Curve(Geom_Hyperbola(_ax2((50, 50, 0), (0, 0, 1)), 15.0, 8.0), -1.5, 1.5)
    _ext, new, old = _run(adaptor, gp_Pnt(80.0, 50.0, 0.0))
    _compare_min_distance(new, old, "Hyperbola_Translated")


def test_ExtremaPC_ExtendedGeometryTest_Hyperbola_InXZPlane():
    adaptor = GeomAdaptor_Curve(Geom_Hyperbola(_ax2((0, 0, 0), (0, 1, 0)), 10.0, 5.0), -2.0, 2.0)
    _ext, new, old = _run(adaptor, gp_Pnt(20.0, 5.0, 0.0))
    _compare_min_distance(new, old, "Hyperbola_InXZPlane")


def test_ExtremaPC_ExtendedGeometryTest_Hyperbola_HighEccentricity():
    adaptor = GeomAdaptor_Curve(Geom_Hyperbola(_ax2((0, 0, 0), (0, 0, 1)), 30.0, 3.0), -1.0, 1.0)
    point = gp_Pnt(50.0, 10.0, 0.0)
    ext = ExtremaPC_Curve(adaptor)
    new = ext.Perform(point, THE_TOL)
    assert new.IsDone()
    assert new.NbExt() > 0
    i = new.MinIndex()
    min_point = new[i].Point
    _near(point.SquareDistance(min_point), new[i].SquareDistance, THE_TOL)


# BSpline with different configurations


def test_ExtremaPC_ExtendedGeometryTest_BSpline_Linear():
    bspline = _bspline(
        [gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(2, 0, 0), gp_Pnt(3, 1, 0)], [0.0, 0.33, 0.67, 1.0], [2, 1, 1, 2], 1
    )
    adaptor = GeomAdaptor_Curve(bspline)
    _ext, new, old = _run(adaptor, gp_Pnt(1.5, 1.5, 0.0))
    _compare_min_distance(new, old, "BSpline_Linear", 0.01)


def test_ExtremaPC_ExtendedGeometryTest_BSpline_Quadratic():
    bspline = _bspline(
        [gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(2, 0, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0)],
        [0.0, 0.5, 1.0],
        [3, 2, 3],
        2,
    )
    adaptor = GeomAdaptor_Curve(bspline)
    _ext, new, old = _run(adaptor, gp_Pnt(2.0, 2.5, 0.0))
    _compare_min_distance(new, old, "BSpline_Quadratic", 0.01)


def test_ExtremaPC_ExtendedGeometryTest_BSpline_3D_Helix():
    bspline = _bspline(
        [
            gp_Pnt(10, 0, 0),
            gp_Pnt(7, 7, 5),
            gp_Pnt(0, 10, 10),
            gp_Pnt(-7, 7, 15),
            gp_Pnt(-10, 0, 20),
            gp_Pnt(-7, -7, 25),
            gp_Pnt(0, -10, 30),
        ],
        [0.0, 1.0],
        [7, 7],
        6,
    )
    adaptor = GeomAdaptor_Curve(bspline)
    _ext, new, old = _run(adaptor, gp_Pnt(0.0, 0.0, 15.0))
    _compare_min_distance(new, old, "BSpline_3D_Helix", 0.05)


# Bezier with different configurations


def test_ExtremaPC_ExtendedGeometryTest_Bezier_Quadratic():
    adaptor = GeomAdaptor_Curve(_bezier([gp_Pnt(0, 0, 0), gp_Pnt(5, 10, 0), gp_Pnt(10, 0, 0)]))
    _ext, new, old = _run(adaptor, gp_Pnt(5.0, 8.0, 0.0))
    _compare_min_distance(new, old, "Bezier_Quadratic", 0.01)


def test_ExtremaPC_ExtendedGeometryTest_Bezier_HighDegree():
    bezier = _bezier(
        [
            gp_Pnt(0, 0, 0),
            gp_Pnt(1, 3, 0),
            gp_Pnt(2, -1, 0),
            gp_Pnt(3, 4, 0),
            gp_Pnt(4, 0, 0),
            gp_Pnt(5, 2, 0),
            gp_Pnt(6, 1, 0),
        ]
    )
    adaptor = GeomAdaptor_Curve(bezier)
    _ext, new, old = _run(adaptor, gp_Pnt(3.0, 3.0, 0.0))
    _compare_min_distance(new, old, "Bezier_HighDegree", 0.01)


def test_ExtremaPC_ExtendedGeometryTest_Bezier_3D_SCurve():
    adaptor = GeomAdaptor_Curve(_bezier([gp_Pnt(0, 0, 0), gp_Pnt(3, 5, 2), gp_Pnt(6, 0, 4), gp_Pnt(9, 5, 6)]))
    _ext, new, old = _run(adaptor, gp_Pnt(4.5, 3.0, 3.0))
    _compare_min_distance(new, old, "Bezier_3D_SCurve", 0.01)


# Offset curves with different bases


def test_ExtremaPC_ExtendedGeometryTest_OffsetEllipse():
    base = Geom_Ellipse(_ax2((0, 0, 0), (0, 0, 1)), 20.0, 10.0)
    adaptor = GeomAdaptor_Curve(Geom_OffsetCurve(base, 3.0, gp_Dir(0, 0, 1)))
    _ext, new, old = _run(adaptor, gp_Pnt(30.0, 5.0, 0.0))
    _compare_min_distance(new, old, "OffsetEllipse", 0.05)


def test_ExtremaPC_ExtendedGeometryTest_OffsetBezier():
    base = _bezier([gp_Pnt(0, 0, 0), gp_Pnt(2, 4, 0), gp_Pnt(4, 4, 0), gp_Pnt(6, 0, 0)])
    adaptor = GeomAdaptor_Curve(Geom_OffsetCurve(base, 1.0, gp_Dir(0, 0, 1)))
    _ext, new, old = _run(adaptor, gp_Pnt(3.0, 5.0, 0.0))
    _compare_min_distance(new, old, "OffsetBezier", 0.05)


def test_ExtremaPC_ExtendedGeometryTest_OffsetNegative():
    base = Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 15.0)
    adaptor = GeomAdaptor_Curve(Geom_OffsetCurve(base, -5.0, gp_Dir(0, 0, 1)))
    _ext, new, old = _run(adaptor, gp_Pnt(20.0, 0.0, 0.0))
    _compare_min_distance(new, old, "OffsetNegative", 0.01)
    _near(math.sqrt(new.MinSquareDistance()), 10.0, 0.01)


# Arc (partial curve) tests


def test_ExtremaPC_ExtendedGeometryTest_CircleArc_FirstQuadrant():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0), 0.0, math.pi / 2.0)
    _ext, new, old = _run(adaptor, gp_Pnt(15.0, 15.0, 0.0))
    _compare_min_distance(new, old, "CircleArc_FirstQuadrant")


def test_ExtremaPC_ExtendedGeometryTest_CircleArc_ThirdQuadrant():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0), math.pi, 3.0 * math.pi / 2.0)
    _ext, new, old = _run(adaptor, gp_Pnt(-15.0, -5.0, 0.0))
    _compare_min_distance(new, old, "CircleArc_ThirdQuadrant")


def test_ExtremaPC_ExtendedGeometryTest_EllipseArc_SemiEllipse():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((0, 0, 0), (0, 0, 1)), 20.0, 10.0), 0.0, math.pi)
    _ext, new, old = _run(adaptor, gp_Pnt(0.0, 20.0, 0.0))
    _compare_min_distance(new, old, "EllipseArc_SemiEllipse")


# Edge cases and degenerate situations


def test_ExtremaPC_ExtendedGeometryTest_Point_ExactlyOnCurve_Circle():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0))
    ext = ExtremaPC_Curve(adaptor)
    new = ext.Perform(gp_Pnt(10.0, 0.0, 0.0), THE_TOL)
    assert new.IsDone()
    _near(math.sqrt(new.MinSquareDistance()), 0.0, THE_TOL)


def test_ExtremaPC_ExtendedGeometryTest_Point_ExactlyOnCurve_BSpline():
    bspline = _bspline([gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0)], [0.0, 1.0], [4, 4], 3)
    adaptor = GeomAdaptor_Curve(bspline)
    point = adaptor.Value(0.5)
    ext = ExtremaPC_Curve(adaptor)
    new = ext.Perform(point, THE_TOL)
    assert new.IsDone()
    _near(math.sqrt(new.MinSquareDistance()), 0.0, 0.01)


def test_ExtremaPC_ExtendedGeometryTest_Point_VeryFar():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0))
    _ext, new, old = _run(adaptor, gp_Pnt(10000.0, 10000.0, 0.0))
    _compare_min_max(new, old, "Point_VeryFar")


def test_ExtremaPC_ExtendedGeometryTest_Point_VeryClose():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0))
    _ext, new, _old = _run(adaptor, gp_Pnt(10.0001, 0.0, 0.0))
    assert new.IsDone()
    _near(math.sqrt(new.MinSquareDistance()), 0.0001, 1.0e-5)


# Random stress tests for all geometry types


def _random_min_pass_count(adaptor, seed, low, high):
    rng = random.Random(seed)
    pass_count = 0
    for _ in range(100):
        point = gp_Pnt(rng.uniform(low, high), rng.uniform(low, high), rng.uniform(low, high))
        _ext, new, old = _run(adaptor, point)
        if not old.IsDone():
            continue
        if new.IsDone() and new.NbExt() > 0:
            new_min = math.sqrt(new.MinSquareDistance())
            old_min_sq = RealLast()
            for j in range(1, old.NbExt() + 1):
                if old.SquareDistance(j) < old_min_sq:
                    old_min_sq = old.SquareDistance(j)
            if abs(new_min - math.sqrt(old_min_sq)) < THE_TOL:
                pass_count += 1
    return pass_count


def test_ExtremaPC_ExtendedGeometryTest_Random_Circle_100Points():
    adaptor = GeomAdaptor_Curve(Geom_Circle(_ax2((0, 0, 0), (0, 0, 1)), 10.0))
    pass_count = _random_min_pass_count(adaptor, 12345, -100.0, 100.0)
    assert pass_count >= 95, "At least 95% of random tests should pass"


def test_ExtremaPC_ExtendedGeometryTest_Random_Ellipse_100Points():
    adaptor = GeomAdaptor_Curve(Geom_Ellipse(_ax2((0, 0, 0), (0, 0, 1)), 20.0, 10.0))
    pass_count = _random_min_pass_count(adaptor, 54321, -100.0, 100.0)
    assert pass_count >= 95, "At least 95% of random tests should pass"


def test_ExtremaPC_ExtendedGeometryTest_Random_Parabola_100Points():
    adaptor = GeomAdaptor_Curve(Geom_Parabola(_ax2((0, 0, 0), (0, 0, 1)), 5.0), -20.0, 20.0)
    rng = random.Random(11111)
    pass_count = 0
    valid_count = 0
    for _ in range(100):
        point = gp_Pnt(rng.uniform(-50.0, 50.0), rng.uniform(-50.0, 50.0), rng.uniform(-50.0, 50.0))
        _ext, new, old = _run(adaptor, point)
        if not old.IsDone() or old.NbExt() == 0:
            continue
        if not new.IsDone() or new.NbExt() == 0:
            continue
        valid_count += 1
        new_min = math.sqrt(new.MinSquareDistance())
        old_min = RealLast()
        for j in range(1, old.NbExt() + 1):
            if old.SquareDistance(j) < old_min * old_min:
                old_min = math.sqrt(old.SquareDistance(j))
        if abs(new_min - old_min) < 0.01:
            pass_count += 1
    if valid_count > 0:
        assert pass_count / valid_count >= 0.80, "At least 80% of random tests should pass"
