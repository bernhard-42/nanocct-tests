# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_TBezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_Circle, Geom_Ellipse
from nanocct.GeomEval import GeomEval_TBezierCurve
from nanocct.gp import gp_Ax2, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

THE_FD_TOL_D1 = 1e-5
THE_FD_TOL_D2 = 1e-4
CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def _poles(pts):
    arr = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, start=1):
        arr[i] = gp_Pnt(*p)
    return arr


def create_semicircle():
    return GeomEval_TBezierCurve(_poles([(0, 0, 0), (0, 1, 0), (1, 0, 0)]), 1.0)


def create_semi_ellipse():
    return GeomEval_TBezierCurve(_poles([(0, 0, 0), (0, 2, 0), (3, 0, 0)]), 1.0)


def create_simple_curve():
    return GeomEval_TBezierCurve(_poles([(0, 0, 0), (1, 1, 0), (2, 0, 0)]), 1.0)


def _near_vec(a, b, tol):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def test_GeomEval_TBezierCurveTest_Construction_ValidParams():
    c = create_simple_curve()
    assert c.NbPoles() == 3
    assert c.Order() == 1
    assert abs(c.Alpha() - 1.0) <= CONF
    assert c.IsRational() is False


def test_GeomEval_TBezierCurveTest_Construction_InvalidParams_Throws():
    with pytest.raises(Standard_ConstructionError):
        GeomEval_TBezierCurve(_poles([(0, 0, 0), (1, 0, 0)]), 1.0)
    p3 = _poles([(0, 0, 0), (1, 0, 0), (2, 0, 0)])
    with pytest.raises(Standard_ConstructionError):
        GeomEval_TBezierCurve(p3, 0.0)
    with pytest.raises(Standard_ConstructionError):
        GeomEval_TBezierCurve(p3, -1.0)


def test_GeomEval_TBezierCurveTest_EvalD0_Endpoints():
    c = create_simple_curve()
    start = c.EvalD0(c.FirstParameter())
    end = c.EvalD0(c.LastParameter())
    assert abs(start.Distance(c.StartPoint())) <= CONF
    assert abs(end.Distance(c.EndPoint())) <= CONF


def test_GeomEval_TBezierCurveTest_ParameterRange():
    c = create_simple_curve()
    assert abs(c.FirstParameter() - 0.0) <= CONF
    assert abs(c.LastParameter() - math.pi / 1.0) <= CONF


def test_GeomEval_TBezierCurveTest_EvalD1_ConsistentWithD0():
    c = create_simple_curve()
    u = math.pi / 3.0
    d1 = c.EvalD1(u)
    p1 = c.EvalD0(u + CONF)
    p2 = c.EvalD0(u - CONF)
    fd = gp_Vec((p1.XYZ() - p2.XYZ()) / (2.0 * CONF))
    _near_vec(d1.D1, fd, THE_FD_TOL_D1)


def test_GeomEval_TBezierCurveTest_PeriodicityAndClosure():
    assert create_simple_curve().IsPeriodic() is False


def test_GeomEval_TBezierCurveTest_Reverse_NotImplemented():
    c = create_simple_curve()
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def test_GeomEval_TBezierCurveTest_Construction_Rational():
    poles = _poles([(0, 0, 0), (1, 1, 0), (2, 0, 0)])
    w = NCollection_Array1[float](1, 3)
    w[1] = 1.0
    w[2] = 2.0
    w[3] = 1.0
    c = GeomEval_TBezierCurve(poles, w, 1.0)
    assert c.IsRational() is True
    assert c.Weights().Size() == 3


def test_GeomEval_TBezierCurveTest_Transform_NotImplemented():
    c = create_simple_curve()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(trsf)


def test_GeomEval_TBezierCurveTest_Copy_Independent():
    cp = create_simple_curve().Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_TBezierCurve)
    assert cp.NbPoles() == 3
    assert abs(cp.Alpha() - 1.0) <= CONF


def test_GeomEval_TBezierCurveTest_DumpJson_NoCrash():
    assert isinstance(create_simple_curve().DumpJson(), str)


def test_GeomEval_TBezierCurveTest_EvalD2_ConsistentWithD1():
    c = create_simple_curve()
    u = math.pi / 4.0
    d2 = c.EvalD2(u)
    dp = c.EvalD1(u + CONF)
    dm = c.EvalD1(u - CONF)
    fd = gp_Vec((dp.D1.XYZ() - dm.D1.XYZ()) / (2.0 * CONF))
    _near_vec(d2.D2, fd, THE_FD_TOL_D2)


def test_GeomEval_TBezierCurveTest_EvalD3_ConsistentWithD2():
    c = create_simple_curve()
    u = math.pi / 3.0
    d3 = c.EvalD3(u)
    dp = c.EvalD2(u + CONF)
    dm = c.EvalD2(u - CONF)
    fd = gp_Vec((dp.D2.XYZ() - dm.D2.XYZ()) / (2.0 * CONF))
    _near_vec(d3.D3, fd, THE_FD_TOL_D2)


def test_GeomEval_TBezierCurveTest_EvalDN_ConsistentWithD1():
    c = create_simple_curve()
    u = math.pi / 6.0
    d1 = c.EvalD1(u)
    dn = c.EvalDN(u, 1)
    _near_vec(d1.D1, dn, CONF)


def test_GeomEval_TBezierCurveTest_EvalD0_MatchesCircle():
    tb = create_semicircle()
    circ = Geom_Circle(gp_Ax2(), 1.0)
    params = [0.0, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2, 2 * math.pi / 3, 3 * math.pi / 4, math.pi]
    for u in params:
        assert abs(tb.EvalD0(u).Distance(circ.EvalD0(u))) <= ANG, f"D0 mismatch at u={u}"


def test_GeomEval_TBezierCurveTest_EvalD3_MatchesCircle():
    tb = create_semicircle()
    circ = Geom_Circle(gp_Ax2(), 1.0)
    for u in (math.pi / 6, math.pi / 3, math.pi / 2, 2 * math.pi / 3):
        dt = tb.EvalD3(u)
        dc = circ.EvalD3(u)
        assert abs(dt.Point.Distance(dc.Point)) <= ANG
        _near_vec(dt.D1, dc.D1, ANG)
        _near_vec(dt.D2, dc.D2, ANG)
        _near_vec(dt.D3, dc.D3, ANG)


def test_GeomEval_TBezierCurveTest_EvalD2_MatchesEllipse():
    tb = create_semi_ellipse()
    ell = Geom_Ellipse(gp_Ax2(), 3.0, 2.0)
    for u in (math.pi / 6, math.pi / 4, math.pi / 2, 3 * math.pi / 4):
        dt = tb.EvalD2(u)
        dc = ell.EvalD2(u)
        assert abs(dt.Point.Distance(dc.Point)) <= ANG
        _near_vec(dt.D1, dc.D1, ANG)
        _near_vec(dt.D2, dc.D2, ANG)


def test_GeomEval_TBezierCurveTest_EvalD0_MultiplePoints():
    c = create_simple_curve()
    first, last = c.FirstParameter(), c.LastParameter()
    n = 10
    step = (last - first) / n
    prev = c.EvalD0(first)
    for i in range(1, n + 1):
        p = c.EvalD0(first + step * i)
        assert math.isfinite(p.X())
        assert math.isfinite(p.Y())
        assert math.isfinite(p.Z())
        assert prev.Distance(p) < 10.0 * step
        prev = p
