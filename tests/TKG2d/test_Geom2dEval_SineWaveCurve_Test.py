# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dEval_SineWaveCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2dEval import Geom2dEval_SineWaveCurve
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


S = Geom2dEval_SineWaveCurve


def test_Geom2dEval_SineWaveCurveTest_Construction_ValidParams():
    c = S(gp_Ax2d(), 2.0, 3.0, 0.0)
    near(c.Amplitude(), 2.0)
    near(c.Omega(), 3.0)


def test_Geom2dEval_SineWaveCurveTest_Construction_InvalidParams_Throws():
    for a, w in ((0.0, 1.0), (1.0, 0.0)):
        with pytest.raises(Standard_ConstructionError):
            S(gp_Ax2d(), a, w)


def test_Geom2dEval_SineWaveCurveTest_EvalD0_AtKnownPoints():
    c = S(gp_Ax2d(), 2.0, 3.0, 0.0)
    p0 = c.EvalD0(0.0)
    near(p0.X(), 0.0)
    near(p0.Y(), 0.0)
    t1 = math.pi / (2.0 * 3.0)
    p1 = c.EvalD0(t1)
    near(p1.X(), t1)
    near(p1.Y(), 2.0)


def test_Geom2dEval_SineWaveCurveTest_IsPeriodic():
    c = S(gp_Ax2d(), 2.0, 3.0, 0.0)
    assert c.IsPeriodic() is False
    with pytest.raises(Standard_NoSuchObject):
        c.Period()


def test_Geom2dEval_SineWaveCurveTest_Reverse_NotImplemented():
    check_reverse_not_implemented(S(gp_Ax2d(), 2.0, 3.0, 0.0))


def test_Geom2dEval_SineWaveCurveTest_Transform_NotImplemented():
    check_transform_not_implemented(S(gp_Ax2d(), 2.0, 3.0, 0.0))


def test_Geom2dEval_SineWaveCurveTest_EvalD1_ConsistentWithD0():
    check_d1(S(gp_Ax2d(), 2.0, 3.0, 0.5), 1.0)


def test_Geom2dEval_SineWaveCurveTest_EvalD2_ConsistentWithD1():
    check_d2(S(gp_Ax2d(), 2.0, 3.0, 0.5), 1.0)


def test_Geom2dEval_SineWaveCurveTest_EvalD3_ConsistentWithD2():
    check_d3(S(gp_Ax2d(), 2.0, 3.0, 0.5), 1.0)


def test_Geom2dEval_SineWaveCurveTest_EvalDN_HigherOrder_ConsistentWithPreviousOrder():
    check_dn(S(gp_Ax2d(), 2.0, 3.0, 0.5), 1.2, 6)


def test_Geom2dEval_SineWaveCurveTest_Copy_Independent():
    cp = S(gp_Ax2d(), 2.0, 3.0, 0.5).Copy()
    assert isinstance(cp, S)
    near(cp.Amplitude(), 2.0)


def test_Geom2dEval_SineWaveCurveTest_DumpJson_NoCrash():
    assert isinstance(S(gp_Ax2d(), 2.0, 3.0, 0.0).DumpJson(), str)
