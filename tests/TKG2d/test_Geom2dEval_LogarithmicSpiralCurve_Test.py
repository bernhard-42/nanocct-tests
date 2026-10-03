# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dEval_LogarithmicSpiralCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2dEval import Geom2dEval_LogarithmicSpiralCurve
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


S = Geom2dEval_LogarithmicSpiralCurve


def test_Geom2dEval_LogarithmicSpiralCurveTest_Construction_ValidParams():
    c = S(gp_Ax2d(), 1.0, 0.2)
    near(c.Scale(), 1.0)
    near(c.GrowthExponent(), 0.2)


def test_Geom2dEval_LogarithmicSpiralCurveTest_Construction_InvalidParams_Throws():
    for a, b in ((0.0, 0.2), (-1.0, 0.2), (1.0, 0.0), (1.0, -0.2)):
        with pytest.raises(Standard_ConstructionError):
            S(gp_Ax2d(), a, b)


def test_Geom2dEval_LogarithmicSpiralCurveTest_SelfSimilarity():
    ax = gp_Ax2d()
    c = S(ax, 1.0, 0.2)
    k = 2.0
    scale = math.exp(0.2 * k)
    o = ax.Location()
    for t in (0.0, 1.0, 2.0, math.pi):
        d1 = o.Distance(c.EvalD0(t))
        d2 = o.Distance(c.EvalD0(t + k))
        if d1 > TOL:
            near(d2 / d1, scale, 1e-10)


def test_Geom2dEval_LogarithmicSpiralCurveTest_ConstantAngle():
    ax = gp_Ax2d()
    c = S(ax, 1.0, 0.2)
    expected = math.atan(1.0 / 0.2)
    o = ax.Location()
    for t in (1.0, 2.0, math.pi, 5.0):
        r = c.EvalD1(t)
        radial = gp_Vec2d(o, r.Point)
        angle = abs(math.atan2(abs(r.D1.Crossed(radial)), r.D1.Dot(radial)))
        near(angle, expected, 1e-10)


def test_Geom2dEval_LogarithmicSpiralCurveTest_EvalD1_ConsistentWithD0():
    check_d1(S(gp_Ax2d(), 1.0, 0.3), 2.0)


def test_Geom2dEval_LogarithmicSpiralCurveTest_EvalD2_ConsistentWithD1():
    check_d2(S(gp_Ax2d(), 1.0, 0.3), 2.0)


def test_Geom2dEval_LogarithmicSpiralCurveTest_EvalD3_ConsistentWithD2():
    check_d3(S(gp_Ax2d(), 1.0, 0.3), 2.0)


def test_Geom2dEval_LogarithmicSpiralCurveTest_EvalDN_HigherOrder_ConsistentWithPreviousOrder():
    check_dn(S(gp_Ax2d(), 1.0, 0.3), 1.2, 6)


def test_Geom2dEval_LogarithmicSpiralCurveTest_Properties():
    c = S(gp_Ax2d(), 1.0, 0.2)
    assert c.IsClosed() is False
    assert c.IsPeriodic() is False
    assert c.Continuity() == GeomAbs_CN


def test_Geom2dEval_LogarithmicSpiralCurveTest_Reverse_NotImplemented():
    check_reverse_not_implemented(S(gp_Ax2d(), 1.0, 0.2))


def test_Geom2dEval_LogarithmicSpiralCurveTest_Transform_NotImplemented():
    check_transform_not_implemented(S(gp_Ax2d(), 1.0, 0.2))


def test_Geom2dEval_LogarithmicSpiralCurveTest_Copy_Independent():
    cp = S(gp_Ax2d(), 1.0, 0.2).Copy()
    assert isinstance(cp, S)
    near(cp.Scale(), 1.0)
    near(cp.GrowthExponent(), 0.2)


def test_Geom2dEval_LogarithmicSpiralCurveTest_DumpJson_NoCrash():
    assert isinstance(S(gp_Ax2d(), 1.0, 0.2).DumpJson(), str)
