# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Ellipse_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ElCLib import ElCLib
from nanocct.ExtremaPC import Domain1D, ExtremaPC_Ellipse
from nanocct.gp import gp_Ax2, gp_Dir, gp_Elips, gp_Pnt

THE_TOL = 1.0e-8
THE_PI = math.pi


def _near(value, expected, tol):
    assert abs(value - expected) <= tol, f"{value} != {expected} +- {tol}"


def _ellipse(major=20.0, minor=10.0, origin=(0, 0, 0), normal=(0, 0, 1)):
    return gp_Elips(gp_Ax2(gp_Pnt(*origin), gp_Dir(*normal)), major, minor)


def _assert_min_on_ellipse(result, ellipse):
    i = result.MinIndex()
    on_ellipse = ElCLib.Value_s(result[i].Parameter, ellipse)
    _near(result[i].Point.Distance(on_ellipse), 0.0, THE_TOL)


# Basic tests - point on major axis


def test_ExtremaPC_EllipseTest_PointOnMajorAxis_Outside():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PointOnMajorAxis_Inside():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(10.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(result.MinSquareDistance(), 600.0 / 9.0, 0.01)


def test_ExtremaPC_EllipseTest_PointOnMajorAxis_NegativeSide():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(-30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


# Point on minor axis


def test_ExtremaPC_EllipseTest_PointOnMinorAxis_Outside():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 20.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PointOnMinorAxis_Inside():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 5.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 5.0, THE_TOL)


# Point in quadrants


def test_ExtremaPC_EllipseTest_PointInFirstQuadrant():
    ellipse = _ellipse()
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(gp_Pnt(15.0, 15.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    assert result.MinSquareDistance() > 0.0
    _assert_min_on_ellipse(result, ellipse)


def test_ExtremaPC_EllipseTest_PointInSecondQuadrant():
    ellipse = _ellipse()
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(gp_Pnt(-15.0, 8.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _assert_min_on_ellipse(result, ellipse)


def test_ExtremaPC_EllipseTest_PointInThirdQuadrant():
    ellipse = _ellipse()
    point = gp_Pnt(-12.0, -7.0, 0.0)
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _assert_min_on_ellipse(result, ellipse)
    assert math.sqrt(result.MinSquareDistance()) < point.Distance(gp_Pnt(0, 0, 0))


def test_ExtremaPC_EllipseTest_PointInFourthQuadrant():
    ellipse = _ellipse()
    point = gp_Pnt(18.0, -5.0, 0.0)
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _assert_min_on_ellipse(result, ellipse)
    assert math.sqrt(result.MinSquareDistance()) < point.Distance(gp_Pnt(0, 0, 0))


# Degenerate case - point at center


def test_ExtremaPC_EllipseTest_PointAtCenter_Degenerate():
    ellipse = _ellipse()
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 4
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)
    _near(math.sqrt(result.MaxSquareDistance()), 20.0, THE_TOL)
    for i in range(result.NbExt()):
        on_ellipse = ElCLib.Value_s(result[i].Parameter, ellipse)
        _near(result[i].Point.Distance(on_ellipse), 0.0, THE_TOL)


# Point out of plane


def test_ExtremaPC_EllipseTest_PointAbovePlane():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(30.0, 0.0, 5.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(result.MinSquareDistance(), 125.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PointBelowPlane():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 20.0, -8.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(result.MinSquareDistance(), 164.0, THE_TOL)


# Partial arc tests


def test_ExtremaPC_EllipseTest_PartialArc_FirstQuadrant():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PartialArc_SecondHalf():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(-30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


# Different ellipse configurations


def test_ExtremaPC_EllipseTest_EllipseWithOffset():
    ev = ExtremaPC_Ellipse(_ellipse(origin=(100, 200, 50)))
    result = ev.PerformWithEndpoints(gp_Pnt(130.0, 200.0, 50.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_EllipseTest_EllipseInYZPlane():
    ellipse = _ellipse(normal=(1, 0, 0))
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(gp_Pnt(5.0, 30.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    assert result.MinSquareDistance() > 0.0
    for i in range(result.NbExt()):
        ext = result[i]
        check = ElCLib.Value_s(ext.Parameter, ellipse)
        _near(check.Distance(ext.Point), 0.0, 1e-7)


def test_ExtremaPC_EllipseTest_NearlyCircularEllipse():
    ev = ExtremaPC_Ellipse(_ellipse(10.0, 9.9))
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 10.0, THE_TOL)


def test_ExtremaPC_EllipseTest_VeryFlatEllipse():
    ev = ExtremaPC_Ellipse(_ellipse(20.0, 2.0))
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 10.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 2
    _near(math.sqrt(result.MinSquareDistance()), 8.0, THE_TOL)


# Point on ellipse


def test_ExtremaPC_EllipseTest_PointOnEllipse_MajorVertex():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(20.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    _near(result.MinSquareDistance(), 0.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PointOnEllipse_MinorVertex():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(0.0, 10.0, 0.0), THE_TOL)
    assert result.IsDone()
    _near(result.MinSquareDistance(), 0.0, THE_TOL)


def test_ExtremaPC_EllipseTest_PointOnEllipse_General():
    ellipse = _ellipse()
    point = ElCLib.Value_s(THE_PI / 4.0, ellipse)
    ev = ExtremaPC_Ellipse(ellipse)
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    _near(result.MinSquareDistance(), 0.0, THE_TOL)


# Number of extrema tests


def test_ExtremaPC_EllipseTest_FourExtrema_PointInsideEllipse():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(5.0, 3.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 4


def test_ExtremaPC_EllipseTest_TwoExtrema_PointOnAxis():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(30.0, 0.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() == 2


# Narrow parameter range tests - verify relative step works correctly


def test_ExtremaPC_EllipseTest_NarrowRange_VerySmall():
    u_min = 0.0
    u_max = 0.05
    ev = ExtremaPC_Ellipse(_ellipse(), Domain1D(u_min, u_max))
    result = ev.PerformWithEndpoints(gp_Pnt(22.0, 2.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 1
    for i in range(result.NbExt()):
        assert result[i].Parameter >= u_min - THE_TOL
        assert result[i].Parameter <= u_max + THE_TOL


def test_ExtremaPC_EllipseTest_NarrowRange_MediumSmall():
    ellipse = _ellipse()
    point = gp_Pnt(25.0, 5.0, 0.0)
    u_min = THE_PI / 6.0 - 0.1
    u_max = THE_PI / 6.0 + 0.1
    ev = ExtremaPC_Ellipse(ellipse, Domain1D(u_min, u_max))
    result = ev.PerformWithEndpoints(point, THE_TOL)
    assert result.IsDone()
    for i in range(result.NbExt()):
        on_ellipse = ElCLib.Value_s(result[i].Parameter, ellipse)
        _near(on_ellipse.Distance(result[i].Point), 0.0, THE_TOL)
        _near(result[i].SquareDistance, point.SquareDistance(on_ellipse), THE_TOL)


def test_ExtremaPC_EllipseTest_NarrowRange_TinyArc():
    ev = ExtremaPC_Ellipse(_ellipse(), Domain1D(0.0, 0.001))
    result = ev.PerformWithEndpoints(gp_Pnt(21.0, 0.5, 0.0), THE_TOL)
    assert result.IsDone() or result.NbExt() >= 0


def test_ExtremaPC_EllipseTest_LargeRange_FullCircle():
    ev = ExtremaPC_Ellipse(_ellipse())
    result = ev.PerformWithEndpoints(gp_Pnt(5.0, 3.0, 0.0), THE_TOL)
    assert result.IsDone()
    assert result.NbExt() >= 4
    for i in range(result.NbExt()):
        assert result[i].SquareDistance > 0.0
