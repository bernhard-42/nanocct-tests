# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_CircularHelixCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_Circle
from nanocct.GeomAbs import GeomAbs_CN
from nanocct.GeomEval import GeomEval_CircularHelixCurve
from nanocct.gp import gp_Ax2, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()
THE_FD_TOL = 1e-5


def near(a, b, tol):
    return abs(a - b) <= tol


def test_GeomEval_CircularHelixCurveTest_Construction_ValidParams():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    assert near(c.Radius(), 5.0, CONF)
    assert near(c.Pitch(), 10.0, CONF)


def test_GeomEval_CircularHelixCurveTest_Construction_InvalidRadius_Throws():
    with pytest.raises(Standard_ConstructionError):
        GeomEval_CircularHelixCurve(gp_Ax2(), 0.0, 10.0)
    with pytest.raises(Standard_ConstructionError):
        GeomEval_CircularHelixCurve(gp_Ax2(), -1.0, 10.0)


def test_GeomEval_CircularHelixCurveTest_Construction_NegativePitch_NoThrow():
    GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, -10.0)


def test_GeomEval_CircularHelixCurveTest_EvalD0_AtKnownPoints():
    r, p = 5.0, 10.0
    c = GeomEval_CircularHelixCurve(gp_Ax2(), r, p)
    for t, exp in [
        (0.0, (r, 0.0, 0.0)),
        (math.pi / 2.0, (0.0, r, p / 4.0)),
        (math.pi, (-r, 0.0, p / 2.0)),
        (2.0 * math.pi, (r, 0.0, p)),
    ]:
        pt = c.EvalD0(t)
        assert near(pt.X(), exp[0], CONF)
        assert near(pt.Y(), exp[1], CONF)
        assert near(pt.Z(), exp[2], CONF)


def test_GeomEval_CircularHelixCurveTest_EvalD1_ConstantSpeed():
    r, p = 5.0, 10.0
    c = GeomEval_CircularHelixCurve(gp_Ax2(), r, p)
    zrate = p / (2.0 * math.pi)
    speed = math.sqrt(r * r + zrate * zrate)
    for t in [0.0, 0.5, 1.0, math.pi, 2.0 * math.pi]:
        assert near(c.EvalD1(t).D1.Magnitude(), speed, CONF)


def test_GeomEval_CircularHelixCurveTest_EvalD1_ConsistentWithD0():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    t = 1.5
    d1 = c.EvalD1(t)
    p1 = c.EvalD0(t + CONF)
    p2 = c.EvalD0(t - CONF)
    fd = gp_Vec((p1.XYZ() - p2.XYZ()) / (2.0 * CONF))
    assert near(d1.D1.X(), fd.X(), THE_FD_TOL)
    assert near(d1.D1.Y(), fd.Y(), THE_FD_TOL)
    assert near(d1.D1.Z(), fd.Z(), THE_FD_TOL)


def test_GeomEval_CircularHelixCurveTest_D1_D2_Orthogonal():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    for t in [0.0, 1.0, math.pi, 3.5]:
        assert near(c.EvalD2(t).D2.Magnitude(), 5.0, CONF)


def test_GeomEval_CircularHelixCurveTest_ComparisonWithCircle_ZeroPitch():
    ax = gp_Ax2()
    r = 5.0
    h = GeomEval_CircularHelixCurve(ax, r, 0.0)
    ci = Geom_Circle(ax, r)
    for t in [0.0, math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0]:
        ph, pc = h.EvalD0(t), ci.EvalD0(t)
        assert near(ph.X(), pc.X(), CONF)
        assert near(ph.Y(), pc.Y(), CONF)
        assert near(ph.Z(), pc.Z(), CONF)
        for name, fh, fc in [
            ("D1", h.EvalD1(t), ci.EvalD1(t)),
            ("D2", h.EvalD2(t), ci.EvalD2(t)),
            ("D3", h.EvalD3(t), ci.EvalD3(t)),
        ]:
            vh, vc = getattr(fh, name), getattr(fc, name)
            assert near(vh.X(), vc.X(), ANG)
            assert near(vh.Y(), vc.Y(), ANG)
            assert near(vh.Z(), vc.Z(), ANG)


def test_GeomEval_CircularHelixCurveTest_EvalDN_CyclesPeriod4():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    d1 = c.EvalDN(1.0, 1)
    d5 = c.EvalDN(1.0, 5)
    assert near(d1.X(), d5.X(), CONF)
    assert near(d1.Y(), d5.Y(), CONF)
    assert near(d5.Z(), 0.0, CONF)


def test_GeomEval_CircularHelixCurveTest_Transform_NotImplemented():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(tr)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(tr)


def test_GeomEval_CircularHelixCurveTest_Copy_Independent():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    cp = c.Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_CircularHelixCurve)
    assert near(cp.Radius(), 5.0, CONF)
    assert near(cp.Pitch(), 10.0, CONF)


def test_GeomEval_CircularHelixCurveTest_Reverse_NotImplemented():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(3.0)


def test_GeomEval_CircularHelixCurveTest_Properties():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    assert c.IsClosed() is False
    assert c.IsPeriodic() is False
    assert c.Continuity() == GeomAbs_CN
    assert c.IsCN(100) is True


def test_GeomEval_CircularHelixCurveTest_DumpJson_NoCrash():
    c = GeomEval_CircularHelixCurve(gp_Ax2(), 5.0, 10.0)
    assert isinstance(c.DumpJson(), str)
