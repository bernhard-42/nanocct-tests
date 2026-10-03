# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_CircularHelicoidSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomEval import GeomEval_CircularHelicoidSurface, GeomEval_CircularHelixCurve
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

CONF = Precision.Confusion_s()
THE_FD_TOL = 1e-5


def near(a, b, tol):
    return abs(a - b) <= tol


def test_GeomEval_CircularHelicoidSurfaceTest_Construction_ValidParams():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    assert near(s.Pitch(), 10.0, CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_Construction_ZeroPitch_Throws():
    with pytest.raises(Standard_ConstructionError):
        GeomEval_CircularHelicoidSurface(gp_Ax3(), 0.0)


def test_GeomEval_CircularHelicoidSurfaceTest_Construction_NegativePitch_NoThrow():
    GeomEval_CircularHelicoidSurface(gp_Ax3(), -5.0)


def test_GeomEval_CircularHelicoidSurfaceTest_EvalD0_AtKnownPoints():
    p = 10.0
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), p)
    for (u, v), exp in [
        ((0.0, 1.0), (1.0, 0.0, 0.0)),
        ((math.pi / 2.0, 1.0), (0.0, 1.0, p / 4.0)),
        ((1.0, 0.0), (0.0, 0.0, p / (2.0 * math.pi))),
    ]:
        pt = s.EvalD0(u, v)
        assert near(pt.X(), exp[0], CONF)
        assert near(pt.Y(), exp[1], CONF)
        assert near(pt.Z(), exp[2], CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_D2V_IsZero_RuledSurface():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    for u, v in [(0.0, 1.0), (1.0, 2.0), (math.pi, -1.0)]:
        assert near(s.EvalD2(u, v).D2V.Magnitude(), 0.0, CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_D1V_UnitRadial():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    for u in [0.0, 1.0, math.pi / 2.0, math.pi, 3.5]:
        assert near(s.EvalD1(u, 2.0).D1V.Magnitude(), 1.0, CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_ComparisonWithHelix_ConstantV():
    ax3 = gp_Ax3()
    ax2 = gp_Ax2(ax3.Location(), ax3.Direction(), ax3.XDirection())
    p, r = 10.0, 3.0
    s = GeomEval_CircularHelicoidSurface(ax3, p)
    h = GeomEval_CircularHelixCurve(ax2, r, p)
    for u in [0.0, 0.5, 1.0, math.pi, 2.0 * math.pi]:
        assert near(s.EvalD0(u, r).Distance(h.EvalD0(u)), 0.0, CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_EvalD1_ConsistentWithD0():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    u, v = 1.0, 2.0
    d1 = s.EvalD1(u, v)
    pu1, pu2 = s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)
    pv1, pv2 = s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)
    fdu = gp_Vec((pu1.XYZ() - pu2.XYZ()) / (2.0 * CONF))
    fdv = gp_Vec((pv1.XYZ() - pv2.XYZ()) / (2.0 * CONF))
    for a, b in [(d1.D1U, fdu), (d1.D1V, fdv)]:
        assert near(a.X(), b.X(), THE_FD_TOL)
        assert near(a.Y(), b.Y(), THE_FD_TOL)
        assert near(a.Z(), b.Z(), THE_FD_TOL)


def test_GeomEval_CircularHelicoidSurfaceTest_Bounds_Infinite():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    u1, u2, v1, v2 = s.Bounds()
    for x in (u1, u2, v1, v2):
        assert Precision.IsInfinite_s(x)


def test_GeomEval_CircularHelicoidSurfaceTest_Properties():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    assert s.IsUClosed() is False
    assert s.IsVClosed() is False
    assert s.IsUPeriodic() is False
    assert s.IsVPeriodic() is False
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.0)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.0)


def test_GeomEval_CircularHelicoidSurfaceTest_Reverse_NotImplemented():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_CircularHelicoidSurfaceTest_Transform_NotImplemented():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(tr)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(tr)


def test_GeomEval_CircularHelicoidSurfaceTest_Copy_Independent():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    cp = s.Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_CircularHelicoidSurface)
    assert near(cp.Pitch(), 10.0, CONF)


def test_GeomEval_CircularHelicoidSurfaceTest_DumpJson_NoCrash():
    s = GeomEval_CircularHelicoidSurface(gp_Ax3(), 10.0)
    assert isinstance(s.DumpJson(), str)
