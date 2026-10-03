# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dEval_CircleInvoluteCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2dEval import Geom2dEval_CircleInvoluteCurve
from nanocct.gp import gp_Ax2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NoSuchObject, Standard_NotImplemented

TOL = Precision.Confusion_s()
FD_TOL = 1e-5
FD_TOL_DN = 1e-4


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def fd_check(exact, plus, minus, tol):
    near(exact.X(), (plus.X() - minus.X()) / (2.0 * TOL), tol)
    near(exact.Y(), (plus.Y() - minus.Y()) / (2.0 * TOL), tol)


def check_d1(c, t):
    fd_check(c.EvalD1(t).D1, c.EvalD0(t + TOL), c.EvalD0(t - TOL), FD_TOL)


def check_d2(c, t):
    fd_check(c.EvalD2(t).D2, c.EvalD1(t + TOL).D1, c.EvalD1(t - TOL).D1, FD_TOL)


def check_d3(c, t):
    fd_check(c.EvalD3(t).D3, c.EvalD2(t + TOL).D2, c.EvalD2(t - TOL).D2, FD_TOL)


def check_dn(c, t, n):
    fd_check(c.EvalDN(t, n), c.EvalDN(t + TOL, n - 1), c.EvalDN(t - TOL, n - 1), FD_TOL_DN)


def check_reverse_not_implemented(c):
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def check_transform_not_implemented(c):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(1.0, 2.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(t)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(t)


S = Geom2dEval_CircleInvoluteCurve


def test_Geom2dEval_CircleInvoluteCurveTest_Construction_ValidParams():
    near(S(gp_Ax2d(), 1.0).Radius(), 1.0)


def test_Geom2dEval_CircleInvoluteCurveTest_Construction_InvalidRadius_Throws():
    for r in (0.0, -1.0):
        with pytest.raises(Standard_ConstructionError):
            S(gp_Ax2d(), r)


def test_Geom2dEval_CircleInvoluteCurveTest_EvalD0_AtT0_OnBaseCircle():
    p = S(gp_Ax2d(), 1.0).EvalD0(0.0)
    near(p.X(), 1.0)
    near(p.Y(), 0.0)


def test_Geom2dEval_CircleInvoluteCurveTest_D1_AtT0_IsZero_Cusp():
    near(S(gp_Ax2d(), 1.0).EvalD1(0.0).D1.Magnitude(), 0.0)


def test_Geom2dEval_CircleInvoluteCurveTest_D1_SpeedLinearInParameter():
    c = S(gp_Ax2d(), 2.0)
    for t in (0.5, 1.0, 2.0, math.pi, 5.0):
        near(c.EvalD1(t).D1.Magnitude(), 2.0 * t)


def test_Geom2dEval_CircleInvoluteCurveTest_EvalD1_ConsistentWithD0():
    check_d1(S(gp_Ax2d(), 1.0), 2.0)


def test_Geom2dEval_CircleInvoluteCurveTest_EvalD2_ConsistentWithD1():
    check_d2(S(gp_Ax2d(), 1.0), 2.0)


def test_Geom2dEval_CircleInvoluteCurveTest_EvalD3_ConsistentWithD2():
    check_d3(S(gp_Ax2d(), 1.0), 2.0)


def test_Geom2dEval_CircleInvoluteCurveTest_EvalDN_HigherOrder_ConsistentWithPreviousOrder():
    check_dn(S(gp_Ax2d(), 1.0), 2.0, 6)


def test_Geom2dEval_CircleInvoluteCurveTest_Properties():
    c = S(gp_Ax2d(), 1.0)
    assert c.IsClosed() is False
    assert c.IsPeriodic() is False
    assert c.Continuity() == GeomAbs_CN
    near(c.FirstParameter(), 0.0)
    assert Precision.IsInfinite_s(c.LastParameter()) is True


def test_Geom2dEval_CircleInvoluteCurveTest_Reverse_NotImplemented():
    check_reverse_not_implemented(S(gp_Ax2d(), 1.0))


def test_Geom2dEval_CircleInvoluteCurveTest_Transform_NotImplemented():
    check_transform_not_implemented(S(gp_Ax2d(), 1.0))


def test_Geom2dEval_CircleInvoluteCurveTest_Copy_Independent():
    cp = S(gp_Ax2d(), 3.0).Copy()
    assert isinstance(cp, S)
    near(cp.Radius(), 3.0)


def test_Geom2dEval_CircleInvoluteCurveTest_DumpJson_NoCrash():
    assert isinstance(S(gp_Ax2d(), 1.0).DumpJson(), str)
