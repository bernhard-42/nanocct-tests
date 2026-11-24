# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Hyperbola_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ElCLib import ElCLib
from nanocct.ExtremaPC import Domain1D, ExtremaPC_Hyperbola
from nanocct.gp import gp_Ax2, gp_Dir, gp_Hypr, gp_Pnt

TOL = 1.0e-8


def _hypr(major=20.0, minor=10.0, origin=(0, 0, 0), normal=(0, 0, 1)):
    return gp_Hypr(gp_Ax2(gp_Pnt(*origin), gp_Dir(*normal)), major, minor)


def _perform(hypr, point, domain=None):
    if domain is None:
        ev = ExtremaPC_Hyperbola(hypr)
    else:
        ev = ExtremaPC_Hyperbola(hypr, Domain1D(*domain))
    res = ev.PerformWithEndpoints(point, TOL)
    return ev, res


def _min_on_curve(res, hypr):
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, hypr)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= TOL
    return ext, on_curve


def test_ExtremaPC_HyperbolaTest_PointOnMajorAxis_Outside():
    _ev, res = _perform(_hypr(), gp_Pnt(50.0, 0.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(res.MinSquareDistance() - 400.0) <= 1.0


def test_ExtremaPC_HyperbolaTest_PointOnMajorAxis_AtVertex():
    _ev, res = _perform(_hypr(), gp_Pnt(20.0, 0.0, 0.0))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOnMajorAxis_BetweenBranches():
    _ev, res = _perform(_hypr(), gp_Pnt(0.0, 0.0, 0.0))
    assert res.IsDone()
    assert abs(math.sqrt(res.MinSquareDistance()) - 20.0) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOffAxis_FirstQuadrant():
    hypr = _hypr()
    point = gp_Pnt(30.0, 15.0, 0.0)
    _ev, res = _perform(hypr, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, hypr)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOffAxis_FourthQuadrant():
    hypr = _hypr()
    point = gp_Pnt(30.0, -15.0, 0.0)
    _ev, res = _perform(hypr, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, hypr)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL
    assert ext.Parameter < 0.0


def test_ExtremaPC_HyperbolaTest_PointInsideAsymptotes():
    hypr = _hypr()
    _ev, res = _perform(hypr, gp_Pnt(25.0, 5.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, hypr)
    assert math.sqrt(res.MinSquareDistance()) < 26.0


def test_ExtremaPC_HyperbolaTest_PointAbovePlane():
    _ev, res = _perform(_hypr(), gp_Pnt(30.0, 0.0, 5.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert res.MinSquareDistance() >= 25.0


def test_ExtremaPC_HyperbolaTest_PointBelowPlane():
    _ev, res = _perform(_hypr(), gp_Pnt(20.0, 0.0, -8.0))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 64.0) <= TOL


def test_ExtremaPC_HyperbolaTest_BoundsPositive():
    _ev, res = _perform(_hypr(), gp_Pnt(30.0, -20.0, 0.0), (0.0, 10.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert res[i].Parameter >= 0.0 - TOL


def test_ExtremaPC_HyperbolaTest_BoundsNegative():
    _ev, res = _perform(_hypr(), gp_Pnt(30.0, 20.0, 0.0), (-10.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert res[i].Parameter <= 0.0 + TOL


def test_ExtremaPC_HyperbolaTest_NarrowBounds():
    _ev, res = _perform(_hypr(), gp_Pnt(30.0, 10.0, 0.0), (0.5, 1.5))
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert res[i].Parameter >= 0.5 - TOL
        assert res[i].Parameter <= 1.5 + TOL


def test_ExtremaPC_HyperbolaTest_SmallSemiAxes():
    hypr = _hypr(2.0, 1.0)
    point = gp_Pnt(5.0, 2.0, 0.0)
    _ev, res = _perform(hypr, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, hypr)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_HyperbolaTest_LargeSemiAxes():
    hypr = _hypr(200.0, 100.0)
    _ev, res = _perform(hypr, gp_Pnt(300.0, 100.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, hypr)


def test_ExtremaPC_HyperbolaTest_NearlyRectangular():
    hypr = _hypr(10.0, 10.0)
    point = gp_Pnt(20.0, 15.0, 0.0)
    _ev, res = _perform(hypr, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, hypr)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOnHyperbola_AtVertex():
    hypr = _hypr()
    _ev, res = _perform(hypr, ElCLib.Value_s(0.0, hypr))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOnHyperbola_Positive():
    hypr = _hypr()
    _ev, res = _perform(hypr, ElCLib.Value_s(1.5, hypr))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_HyperbolaTest_PointOnHyperbola_Negative():
    hypr = _hypr()
    _ev, res = _perform(hypr, ElCLib.Value_s(-2.0, hypr))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_HyperbolaTest_HyperbolaWithOffset():
    _ev, res = _perform(_hypr(origin=(100, 200, 50)), gp_Pnt(120.0, 200.0, 50.0))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_HyperbolaTest_HyperbolaWithOffset_PointOff():
    hypr = _hypr(origin=(100, 200, 50))
    point = gp_Pnt(150.0, 210.0, 50.0)
    _ev, res = _perform(hypr, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, hypr)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_HyperbolaTest_HyperbolaInYZPlane():
    hypr = _hypr(normal=(1, 0, 0))
    _ev, res = _perform(hypr, gp_Pnt(5.0, 30.0, 10.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, hypr)
    assert res.MinSquareDistance() >= 25.0


def test_ExtremaPC_HyperbolaTest_HyperbolaInXZPlane():
    hypr = _hypr(normal=(0, 1, 0))
    _ev, res = _perform(hypr, gp_Pnt(30.0, 5.0, 10.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, hypr)
    assert res.MinSquareDistance() >= 25.0


def test_ExtremaPC_HyperbolaTest_VerifyProjectedPoint():
    hypr = _hypr()
    _ev, res = _perform(hypr, gp_Pnt(35.0, 20.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, hypr)
    assert abs(ext.Point.X() - on_curve.X()) <= TOL
    assert abs(ext.Point.Y() - on_curve.Y()) <= TOL
    assert abs(ext.Point.Z() - on_curve.Z()) <= TOL


def test_ExtremaPC_HyperbolaTest_VerifyDistanceConsistency():
    point = gp_Pnt(40.0, 25.0, 3.0)
    _ev, res = _perform(_hypr(), point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    assert abs(ext.SquareDistance - point.SquareDistance(ext.Point)) <= TOL
