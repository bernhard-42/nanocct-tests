# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Parabola_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ElCLib import ElCLib
from nanocct.ExtremaPC import Domain1D, ExtremaPC_Parabola
from nanocct.gp import gp_Ax2, gp_Dir, gp_Parab, gp_Pnt

TOL = 1.0e-8


def _parab(focal=5.0, origin=(0, 0, 0), normal=(0, 0, 1), xdir=(1, 0, 0)):
    return gp_Parab(gp_Ax2(gp_Pnt(*origin), gp_Dir(*normal), gp_Dir(*xdir)), focal)


def _perform(parab, point, domain=None):
    if domain is None:
        ev = ExtremaPC_Parabola(parab)
    else:
        ev = ExtremaPC_Parabola(parab, Domain1D(*domain))
    res = ev.PerformWithEndpoints(point, TOL)
    return ev, res


def _min_on_curve(res, parab):
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, parab)
    assert abs(ext.Point.Distance(on_curve) - 0.0) <= TOL
    return ext, on_curve


def test_ExtremaPC_ParabolaTest_PointOnAxis_AtVertex():
    _ev, res = _perform(_parab(), gp_Pnt(0.0, 0.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_ParabolaTest_PointOnAxis_Positive():
    _ev, res = _perform(_parab(), gp_Pnt(10.0, 0.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(res.MinSquareDistance() - 100.0) <= TOL


def test_ExtremaPC_ParabolaTest_PointOnAxis_Negative():
    _ev, res = _perform(_parab(), gp_Pnt(-10.0, 0.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(res.MinSquareDistance() - 100.0) <= TOL


def test_ExtremaPC_ParabolaTest_PointOffAxis_Positive():
    parab = _parab()
    point = gp_Pnt(5.0, 10.0, 0.0)
    _ev, res = _perform(parab, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, parab)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_ParabolaTest_PointOffAxis_Negative():
    parab = _parab()
    point = gp_Pnt(5.0, -10.0, 0.0)
    _ev, res = _perform(parab, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, parab)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL
    assert ext.Parameter < 0.0


def test_ExtremaPC_ParabolaTest_PointOffAxis_LargeY():
    parab = _parab()
    _ev, res = _perform(parab, gp_Pnt(0.0, 50.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, _on_curve = _min_on_curve(res, parab)
    assert math.sqrt(res.MinSquareDistance()) < 50.0
    assert ext.Parameter > 0.0


def test_ExtremaPC_ParabolaTest_PointAbovePlane():
    _ev, res = _perform(_parab(), gp_Pnt(5.0, 10.0, 7.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert res.MinSquareDistance() >= 49.0


def test_ExtremaPC_ParabolaTest_PointBelowPlane():
    _ev, res = _perform(_parab(), gp_Pnt(0.0, 0.0, -5.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert abs(res.MinSquareDistance() - 25.0) <= TOL


def test_ExtremaPC_ParabolaTest_BoundsPositive():
    _ev, res = _perform(_parab(), gp_Pnt(0.0, -10.0, 0.0), (0.0, 10.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert res[res.MinIndex()].Parameter >= 0.0


def test_ExtremaPC_ParabolaTest_BoundsNegative():
    _ev, res = _perform(_parab(), gp_Pnt(0.0, 10.0, 0.0), (-10.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    assert res[res.MinIndex()].Parameter <= 0.0


def test_ExtremaPC_ParabolaTest_NarrowBounds():
    _ev, res = _perform(_parab(), gp_Pnt(5.0, 5.0, 0.0), (4.0, 6.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    for i in range(res.NbExt()):
        assert res[i].Parameter >= 4.0 - TOL
        assert res[i].Parameter <= 6.0 + TOL


def test_ExtremaPC_ParabolaTest_SmallFocalLength():
    parab = _parab(0.5)
    point = gp_Pnt(1.0, 2.0, 0.0)
    _ev, res = _perform(parab, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, parab)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_ParabolaTest_LargeFocalLength():
    parab = _parab(100.0)
    _ev, res = _perform(parab, gp_Pnt(50.0, 100.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, parab)


def test_ExtremaPC_ParabolaTest_PointOnParabola_AtVertex():
    parab = _parab()
    _ev, res = _perform(parab, ElCLib.Value_s(0.0, parab))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_ParabolaTest_PointOnParabola_Positive():
    parab = _parab()
    _ev, res = _perform(parab, ElCLib.Value_s(10.0, parab))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_ParabolaTest_PointOnParabola_Negative():
    parab = _parab()
    _ev, res = _perform(parab, ElCLib.Value_s(-15.0, parab))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_ParabolaTest_ParabolaWithOffset():
    _ev, res = _perform(_parab(origin=(100, 200, 50)), gp_Pnt(100.0, 200.0, 50.0))
    assert res.IsDone()
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_ParabolaTest_ParabolaWithOffset_PointOff():
    parab = _parab(origin=(100, 200, 50))
    point = gp_Pnt(110.0, 210.0, 50.0)
    _ev, res = _perform(parab, point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext, on_curve = _min_on_curve(res, parab)
    assert abs(ext.SquareDistance - point.SquareDistance(on_curve)) <= TOL


def test_ExtremaPC_ParabolaTest_ParabolaInYZPlane():
    parab = _parab(normal=(1, 0, 0), xdir=(0, 1, 0))
    _ev, res = _perform(parab, gp_Pnt(3.0, 10.0, 5.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, parab)
    assert res.MinSquareDistance() >= 9.0


def test_ExtremaPC_ParabolaTest_ParabolaInXZPlane():
    parab = _parab(normal=(0, 1, 0), xdir=(1, 0, 0))
    _ev, res = _perform(parab, gp_Pnt(10.0, 3.0, 5.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    _min_on_curve(res, parab)
    assert res.MinSquareDistance() >= 9.0


def test_ExtremaPC_ParabolaTest_VerifyProjectedPoint():
    parab = _parab()
    _ev, res = _perform(parab, gp_Pnt(10.0, 15.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    on_curve = ElCLib.Value_s(ext.Parameter, parab)
    assert abs(ext.Point.X() - on_curve.X()) <= TOL
    assert abs(ext.Point.Y() - on_curve.Y()) <= TOL
    assert abs(ext.Point.Z() - on_curve.Z()) <= TOL


def test_ExtremaPC_ParabolaTest_VerifyDistanceConsistency():
    point = gp_Pnt(8.0, 12.0, 3.0)
    _ev, res = _perform(_parab(), point)
    assert res.IsDone()
    assert res.NbExt() >= 1
    ext = res[res.MinIndex()]
    assert abs(ext.SquareDistance - point.SquareDistance(ext.Point)) <= TOL
