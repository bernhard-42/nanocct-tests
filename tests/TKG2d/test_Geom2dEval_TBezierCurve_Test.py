# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dEval_TBezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2d import Geom2d_Circle, Geom2d_Ellipse
from nanocct.Geom2dEval import Geom2dEval_TBezierCurve as TB
from nanocct.gp import gp_Ax22d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

TOL = Precision.Confusion_s()
ANG = Precision.Angular_s()
FD_D1, FD_D2, FD_D3 = 1e-5, 1e-4, 1e-3


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def poles(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a.SetValue(i, gp_Pnt2d(x, y))
    return a


def reals(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a.SetValue(i, w)
    return a


def semicircle():
    return TB(poles((0, 0), (0, 1), (1, 0)), 1.0)


def semiellipse():
    return TB(poles((0, 0), (0, 2), (3, 0)), 1.0)


def simple():
    return TB(poles((0, 0), (1, 1), (2, 0)), 1.0)


def quadratic():
    return TB(poles((0, 0), (1, 2), (2, 0), (3, -1), (4, 0.5)), 0.5)


def fd_check(exact, plus, minus, tol):
    near(exact.X(), (plus.X() - minus.X()) / (2.0 * TOL), tol)
    near(exact.Y(), (plus.Y() - minus.Y()) / (2.0 * TOL), tol)


def test_Geom2dEval_TBezierCurveTest_Construction_Linear():
    c = simple()
    assert c.NbPoles() == 3
    assert c.Order() == 1
    near(c.Alpha(), 1.0)
    assert c.IsRational() is False


def test_Geom2dEval_TBezierCurveTest_Construction_Quadratic():
    c = quadratic()
    assert c.NbPoles() == 5
    assert c.Order() == 2
    near(c.Alpha(), 0.5)
    assert c.IsRational() is False


def test_Geom2dEval_TBezierCurveTest_Construction_InvalidParams_Throws():
    with pytest.raises(Standard_ConstructionError):
        TB(poles((0, 0), (1, 0)), 1.0)
    with pytest.raises(Standard_ConstructionError):
        TB(poles((0, 0)), 1.0)
    p3 = poles((0, 0), (1, 0), (2, 0))
    with pytest.raises(Standard_ConstructionError):
        TB(p3, 0.0)
    with pytest.raises(Standard_ConstructionError):
        TB(p3, -1.0)


def test_Geom2dEval_TBezierCurveTest_EvalD0_Endpoints():
    c = simple()
    near(c.EvalD0(c.FirstParameter()).Distance(c.StartPoint()), 0.0)
    near(c.EvalD0(c.LastParameter()).Distance(c.EndPoint()), 0.0)


def test_Geom2dEval_TBezierCurveTest_EvalD0_Midpoint():
    c = simple()
    p = c.EvalD0((c.FirstParameter() + c.LastParameter()) / 2.0)
    assert math.isfinite(p.X())
    assert math.isfinite(p.Y())


def test_Geom2dEval_TBezierCurveTest_EvalD1_ConsistentWithD0():
    c, u = simple(), math.pi / 3.0
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_TBezierCurveTest_EvalD1_QuadraticConsistentWithD0():
    c, u = quadratic(), math.pi / 4.0
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_TBezierCurveTest_Bounds():
    c = simple()
    near(c.FirstParameter(), 0.0)
    near(c.LastParameter(), math.pi / 1.0)
    c2 = quadratic()
    near(c2.FirstParameter(), 0.0)
    near(c2.LastParameter(), math.pi / 0.5)


def test_Geom2dEval_TBezierCurveTest_IsRational_NonRational():
    assert simple().IsRational() is False


def test_Geom2dEval_TBezierCurveTest_IsRational_WithWeights():
    c = TB(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 2.0, 1.0), 1.0)
    assert c.IsRational() is True
    assert c.Weights().Size() == 3


def test_Geom2dEval_TBezierCurveTest_Construction_Rational_MismatchedWeights_Throws():
    with pytest.raises(Standard_ConstructionError):
        TB(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 1.0, 1.0, 1.0, 1.0), 1.0)


def test_Geom2dEval_TBezierCurveTest_Construction_Rational_NegativeWeight_Throws():
    with pytest.raises(Standard_ConstructionError):
        TB(poles((0, 0), (1, 1), (2, 0)), reals(1.0, -1.0, 1.0), 1.0)


def test_Geom2dEval_TBezierCurveTest_NbPoles_Alpha():
    c = simple()
    assert c.NbPoles() == 3
    near(c.Alpha(), 1.0)
    c2 = quadratic()
    assert c2.NbPoles() == 5
    near(c2.Alpha(), 0.5)


def test_Geom2dEval_TBezierCurveTest_Transform_NotImplemented():
    c = simple()
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(1.0, 2.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(t)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(t)


def test_Geom2dEval_TBezierCurveTest_Copy_Independent():
    c = simple()
    cp = c.Copy()
    assert isinstance(cp, TB)
    assert cp.NbPoles() == 3
    near(cp.Alpha(), 1.0)
    u = math.pi / 4.0
    near(c.EvalD0(u).Distance(cp.EvalD0(u)), 0.0)


def test_Geom2dEval_TBezierCurveTest_Copy_Modification_Independent():
    c = simple()
    cp = c.Copy()
    assert isinstance(cp, TB)
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10.0, 10.0))
    with pytest.raises(Standard_NotImplemented):
        cp.Transform(t)
    u = math.pi / 4.0
    near(c.EvalD0(u).Distance(cp.EvalD0(u)), 0.0)


def test_Geom2dEval_TBezierCurveTest_DumpJson_NoCrash():
    assert isinstance(simple().DumpJson(), str)


def test_Geom2dEval_TBezierCurveTest_DumpJson_Rational_NoCrash():
    assert isinstance(TB(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 2.0, 1.0), 1.0).DumpJson(), str)


def test_Geom2dEval_TBezierCurveTest_PeriodicityAndContinuity():
    c = simple()
    assert c.IsPeriodic() is False
    assert c.Continuity() == GeomAbs_CN
    assert c.IsCN(0) is True
    assert c.IsCN(10) is True


def test_Geom2dEval_TBezierCurveTest_Reverse_NotImplemented():
    c = simple()
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def test_Geom2dEval_TBezierCurveTest_EvalD1_Rational_ConsistentWithD0():
    c = TB(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 3.0, 1.0), 1.0)
    u = math.pi / 3.0
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_TBezierCurveTest_EvalD2_ConsistentWithD1():
    c, u = simple(), math.pi / 4.0
    fd_check(c.EvalD2(u).D2, c.EvalD1(u + TOL).D1, c.EvalD1(u - TOL).D1, FD_D2)


def test_Geom2dEval_TBezierCurveTest_EvalD3_ConsistentWithD2():
    c, u = simple(), math.pi / 3.0
    fd_check(c.EvalD3(u).D3, c.EvalD2(u + TOL).D2, c.EvalD2(u - TOL).D2, FD_D3)


def test_Geom2dEval_TBezierCurveTest_EvalDN_ConsistentWithD1():
    c, u = simple(), math.pi / 6.0
    d1, dn = c.EvalD1(u).D1, c.EvalDN(u, 1)
    near(d1.X(), dn.X())
    near(d1.Y(), dn.Y())


def test_Geom2dEval_TBezierCurveTest_EvalD0_MultiplePoints():
    c = simple()
    f, l = c.FirstParameter(), c.LastParameter()
    for i in range(6):
        p = c.EvalD0(f + (l - f) * i / 5)
        assert math.isfinite(p.X())
        assert math.isfinite(p.Y())


def test_Geom2dEval_TBezierCurveTest_EvalD3_MatchesCircle():
    tb = semicircle()
    circ = Geom2d_Circle(gp_Ax22d(), 1.0)
    for u in (math.pi / 6.0, math.pi / 3.0, math.pi / 2.0, 2.0 * math.pi / 3.0):
        dt, dc = tb.EvalD3(u), circ.EvalD3(u)
        near(dt.Point.Distance(dc.Point), 0.0, ANG)
        for a, b in ((dt.D1, dc.D1), (dt.D2, dc.D2), (dt.D3, dc.D3)):
            near(a.X(), b.X(), ANG)
            near(a.Y(), b.Y(), ANG)


def test_Geom2dEval_TBezierCurveTest_EvalD2_MatchesEllipse():
    tb = semiellipse()
    ell = Geom2d_Ellipse(gp_Ax22d(), 3.0, 2.0)
    for u in (math.pi / 6.0, math.pi / 4.0, math.pi / 2.0, 3.0 * math.pi / 4.0):
        dt, dc = tb.EvalD2(u), ell.EvalD2(u)
        near(dt.Point.Distance(dc.Point), 0.0, ANG)
        for a, b in ((dt.D1, dc.D1), (dt.D2, dc.D2)):
            near(a.X(), b.X(), ANG)
            near(a.Y(), b.Y(), ANG)
