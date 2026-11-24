# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ExtremaPC_Line_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.ExtremaPC import Domain1D, ExtremaPC_Line
from nanocct.gp import gp_Dir, gp_Lin, gp_Pnt

TOL = 1.0e-10


def _perform(origin, direction, point, umin=-100.0, umax=100.0):
    line = gp_Lin(gp_Pnt(*origin), gp_Dir(*direction))
    ev = ExtremaPC_Line(line, Domain1D(umin, umax))
    res = ev.PerformWithEndpoints(gp_Pnt(*point), TOL)
    return ev, res


def _check_min(res, nb, param, sq_dist=None, tol=TOL):
    assert res.IsDone()
    assert res.NbExt() == nb
    ext = res[res.MinIndex()]
    assert abs(ext.Parameter - param) <= tol
    if sq_dist is not None:
        assert abs(ext.SquareDistance - sq_dist) <= tol
    return ext


def test_ExtremaPC_LineTest_PointOnLine_AtOrigin():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (0.0, 0.0, 0.0))
    ext = _check_min(res, 3, 0.0, 0.0)
    assert ext.IsMinimum


def test_ExtremaPC_LineTest_PointOnLine_Positive():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (5.0, 0.0, 0.0))
    _check_min(res, 3, 5.0, 0.0)


def test_ExtremaPC_LineTest_PointOnLine_Negative():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (-7.5, 0.0, 0.0))
    _check_min(res, 3, -7.5, 0.0)


def test_ExtremaPC_LineTest_PointOffLine_YOffset():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (5.0, 3.0, 0.0))
    _check_min(res, 3, 5.0, 9.0)


def test_ExtremaPC_LineTest_PointOffLine_ZOffset():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (5.0, 0.0, 4.0))
    _check_min(res, 3, 5.0, 16.0)


def test_ExtremaPC_LineTest_PointOffLine_YZOffset():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (5.0, 3.0, 4.0))
    _check_min(res, 3, 5.0, 25.0)


def test_ExtremaPC_LineTest_ProjectionOutsideBounds_Left():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (-50.0, 3.0, 4.0), 0.0, 100.0)
    _check_min(res, 2, 0.0)


def test_ExtremaPC_LineTest_ProjectionOutsideBounds_Right():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (150.0, 3.0, 4.0), 0.0, 100.0)
    _check_min(res, 2, 100.0)


def test_ExtremaPC_LineTest_ProjectionAtLowerBound():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (10.0, 5.0, 0.0), 10.0, 100.0)
    _check_min(res, 2, 10.0)


def test_ExtremaPC_LineTest_ProjectionAtUpperBound():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (100.0, 5.0, 0.0))
    _check_min(res, 2, 100.0)


def test_ExtremaPC_LineTest_NarrowBounds():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (50.0, 1.0, 0.0))
    _check_min(res, 3, 50.0)


def test_ExtremaPC_LineTest_LineAlongY():
    _ev, res = _perform((0, 0, 0), (0, 1, 0), (3.0, 5.0, 4.0))
    _check_min(res, 3, 5.0, 25.0)


def test_ExtremaPC_LineTest_LineAlongZ():
    _ev, res = _perform((0, 0, 0), (0, 0, 1), (3.0, 4.0, 10.0))
    _check_min(res, 3, 10.0, 25.0)


def test_ExtremaPC_LineTest_LineDiagonal_XY():
    _ev, res = _perform((0, 0, 0), (1, 1, 0), (5.0, 5.0, 3.0))
    _check_min(res, 3, 5.0 * math.sqrt(2.0), 9.0)


def test_ExtremaPC_LineTest_LineDiagonal_XYZ():
    _ev, res = _perform((0, 0, 0), (1, 1, 1), (3.0, 3.0, 3.0))
    assert res.IsDone()
    assert res.NbExt() == 3
    assert abs(res.MinSquareDistance() - 0.0) <= TOL


def test_ExtremaPC_LineTest_LineWithOffset_XAxis():
    _ev, res = _perform((10, 20, 30), (1, 0, 0), (15.0, 20.0, 30.0))
    _check_min(res, 3, 5.0, 0.0)


def test_ExtremaPC_LineTest_LineWithOffset_PointOff():
    _ev, res = _perform((10, 20, 30), (1, 0, 0), (15.0, 23.0, 34.0))
    _check_min(res, 3, 5.0, 25.0)


def test_ExtremaPC_LineTest_NegativeParameters():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (-25.0, 0.0, 0.0))
    _check_min(res, 3, -25.0)


def test_ExtremaPC_LineTest_NegativeBoundsClamp():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (-5.0, 1.0, 0.0), -50.0, -10.0)
    _check_min(res, 2, -10.0)


def test_ExtremaPC_LineTest_LargeCoordinates():
    _ev, res = _perform((1e6, 1e6, 1e6), (1, 0, 0), (1e6 + 100.0, 1e6 + 3.0, 1e6 + 4.0), -100.0, 200.0)
    _check_min(res, 3, 100.0, 25.0, tol=1e-6)


def test_ExtremaPC_LineTest_SmallCoordinates():
    _ev, res = _perform((1e-6, 1e-6, 1e-6), (1, 0, 0), (1e-6 + 1e-3, 1e-6 + 3e-4, 1e-6 + 4e-4))
    _check_min(res, 3, 1e-3, 25e-8)


def test_ExtremaPC_LineTest_VerifyProjectedPoint():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (7.0, 5.0, 0.0))
    assert res.IsDone()
    assert res.NbExt() == 3
    pt = res[res.MinIndex()].Point
    assert abs(pt.X() - 7.0) <= TOL
    assert abs(pt.Y() - 0.0) <= TOL
    assert abs(pt.Z() - 0.0) <= TOL


def test_ExtremaPC_LineTest_VerifyDistanceConsistency():
    point = gp_Pnt(10.0, 6.0, 8.0)
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (10.0, 6.0, 8.0))
    assert res.IsDone()
    assert res.NbExt() == 3
    ext = res[res.MinIndex()]
    assert abs(ext.SquareDistance - point.SquareDistance(ext.Point)) <= TOL
    assert abs(res.MinSquareDistance() - 100.0) <= TOL


def test_ExtremaPC_LineTest_EndpointsAsMaxima():
    _ev, res = _perform((0, 0, 0), (1, 0, 0), (5.0, 1.0, 0.0), 0.0, 10.0)
    _check_min(res, 3, 5.0, 1.0)
    max_param = res[res.MaxIndex()].Parameter
    assert abs(max_param - 0.0) < TOL or abs(max_param - 10.0) < TOL
