# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Circle_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import Domain1D, ExtremaPC_Circle
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt

THE_TOL = 1.0e-10
THE_2PI = 2.0 * math.pi
THE_PI = math.pi
THE_PI_2 = math.pi / 2.0


def xy_circle(radius=10.0):
    return gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), radius)


def min_max_idx(result):
    min_idx = 0 if result[0].SquareDistance < result[1].SquareDistance else 1
    return min_idx, 1 - min_idx


def test_ExtremaPC_CircleTest_PointOutside_OnXAxis():
    ev = ExtremaPC_Circle(xy_circle(), Domain1D(0.0, THE_2PI))
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, max_idx = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 10.0) <= THE_TOL
    assert result[min_idx].IsMinimum
    assert abs(result[min_idx].Parameter - 0.0) <= THE_TOL
    assert abs(math.sqrt(result[max_idx].SquareDistance) - 30.0) <= THE_TOL
    assert not result[max_idx].IsMinimum
    assert abs(result[max_idx].Parameter - THE_PI) <= THE_TOL


def test_ExtremaPC_CircleTest_PointOutside_OnYAxis():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 25.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, max_idx = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 15.0) <= THE_TOL
    assert abs(result[min_idx].Parameter - THE_PI_2) <= THE_TOL
    assert abs(math.sqrt(result[max_idx].SquareDistance) - 35.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointOutside_Diagonal():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 20.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    dist_to_center = math.sqrt(800.0)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - (dist_to_center - 10.0)) <= THE_TOL


def test_ExtremaPC_CircleTest_PointInside_OnXAxis():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(3.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, max_idx = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 7.0) <= THE_TOL
    assert abs(math.sqrt(result[max_idx].SquareDistance) - 13.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointInside_OnYAxis():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 5.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, max_idx = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 5.0) <= THE_TOL
    assert abs(math.sqrt(result[max_idx].SquareDistance) - 15.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointInside_NearCenter():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.1, 0.1, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    dist_to_center = math.sqrt(0.02)
    min_idx, _ = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - (10.0 - dist_to_center)) <= THE_TOL


def test_ExtremaPC_CircleTest_PointAtCenter_Degenerate():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 0.0, 0.0), THE_TOL)
    assert result.IsInfinite()
    assert abs(math.sqrt(result.InfiniteSquareDistance) - 10.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointNearCenter_NotDegenerate():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(1e-8, 0.0, 0.0), 1e-12)
    assert result.IsDone()
    assert result.NbExt() == 2
    offset = 1e-8
    min_idx, max_idx = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - (10.0 - offset)) <= 1e-6
    assert abs(math.sqrt(result[max_idx].SquareDistance) - (10.0 + offset)) <= 1e-6
    assert abs(result[min_idx].Parameter - 0.0) <= THE_TOL
    assert abs(result[max_idx].Parameter - THE_PI) <= THE_TOL


def test_ExtremaPC_CircleTest_PointAbovePlane():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 5.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 125.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointBelowPlane():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 15.0, -7.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 74.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointOnAxis_Degenerate():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 0.0, 15.0), THE_TOL)
    assert result.IsInfinite()
    assert abs(result.InfiniteSquareDistance - 325.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PartialArc_FirstQuadrant():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(math.sqrt(result.MinSquareDistance()) - 10.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PartialArc_SecondQuadrant():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(-20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert abs(math.sqrt(result.MinSquareDistance()) - 10.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PartialArc_ExtremaOutsideRange():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    found_pi = False
    for i in range(result.NbExt()):
        if abs(result[i].Parameter - THE_PI) < 0.1:
            found_pi = True
            assert abs(math.sqrt(result[i].SquareDistance) - 30.0) <= THE_TOL
    assert found_pi


def test_ExtremaPC_CircleTest_CircleWithOffset():
    circle = gp_Circ(gp_Ax2(gp_Pnt(100, 200, 50), gp_Dir(0, 0, 1)), 15.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(130.0, 200.0, 50.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 15.0) <= THE_TOL


def test_ExtremaPC_CircleTest_CircleInYZPlane():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 10.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(5.0, 20.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 125.0) <= THE_TOL


def test_ExtremaPC_CircleTest_CircleInXZPlane():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), 10.0)
    ev = ExtremaPC_Circle(circle)
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 3.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 109.0) <= THE_TOL


def test_ExtremaPC_CircleTest_SmallRadius():
    ev = ExtremaPC_Circle(xy_circle(0.001))
    result = ev.PerformWithEndpoints(gp_Pnt(0.01, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 0.009) <= THE_TOL


def test_ExtremaPC_CircleTest_LargeRadius():
    ev = ExtremaPC_Circle(xy_circle(1000.0))
    result = ev.PerformWithEndpoints(gp_Pnt(1500.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(math.sqrt(result[min_idx].SquareDistance) - 500.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointOnCircle():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(10.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 0.0) <= THE_TOL
    assert abs(result[min_idx].Parameter - 0.0) <= THE_TOL


def test_ExtremaPC_CircleTest_PointOnCircle_AtPi():
    ev = ExtremaPC_Circle(xy_circle())
    result = ev.PerformWithEndpoints(gp_Pnt(-10.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2
    min_idx, _ = min_max_idx(result)
    assert abs(result[min_idx].SquareDistance - 0.0) <= THE_TOL
    assert abs(result[min_idx].Parameter - THE_PI) <= THE_TOL
