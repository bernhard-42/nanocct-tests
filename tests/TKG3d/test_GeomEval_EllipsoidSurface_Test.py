# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_EllipsoidSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_SphericalSurface
from nanocct.GeomEval import GeomEval_EllipsoidSurface
from nanocct.gp import gp_Ax3, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()
THE_FD_TOL = 1e-5
PI = math.pi


def near(a, b, tol):
    return abs(a - b) <= tol


def vnear(a, b, tol):
    assert near(a.X(), b.X(), tol)
    assert near(a.Y(), b.Y(), tol)
    assert near(a.Z(), b.Z(), tol)


def fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def test_GeomEval_EllipsoidSurfaceTest_Construction_ValidParams():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    assert near(s.SemiAxisA(), 3.0, CONF)
    assert near(s.SemiAxisB(), 2.0, CONF)
    assert near(s.SemiAxisC(), 1.0, CONF)


def test_GeomEval_EllipsoidSurfaceTest_Construction_InvalidAxes_Throws():
    for abc in [(0.0, 1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, 0.0)]:
        with pytest.raises(Standard_ConstructionError):
            GeomEval_EllipsoidSurface(gp_Ax3(), *abc)


def _check_d0(u, v, exp):
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    p = s.EvalD0(u, v)
    assert near(p.X(), exp[0], CONF)
    assert near(p.Y(), exp[1], CONF)
    assert near(p.Z(), exp[2], CONF)


def test_GeomEval_EllipsoidSurfaceTest_EvalD0_XAxis():
    _check_d0(0.0, 0.0, (3.0, 0.0, 0.0))


def test_GeomEval_EllipsoidSurfaceTest_EvalD0_YAxis():
    _check_d0(PI / 2.0, 0.0, (0.0, 2.0, 0.0))


def test_GeomEval_EllipsoidSurfaceTest_EvalD0_ZAxis():
    _check_d0(0.0, PI / 2.0, (0.0, 0.0, 1.0))


def test_GeomEval_EllipsoidSurfaceTest_EvalD1_ConsistentWithD0():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    u, v = 1.0, 0.5
    d1 = s.EvalD1(u, v)
    vnear(d1.D1U, fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL)
    vnear(d1.D1V, fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL)


def test_GeomEval_EllipsoidSurfaceTest_Bounds_Periodicity():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 1.0, 1.0, 1.0)
    u1, u2, v1, v2 = s.Bounds()
    assert near(u1, 0.0, CONF)
    assert near(u2, 2.0 * PI, CONF)
    assert near(v1, -PI / 2.0, CONF)
    assert near(v2, PI / 2.0, CONF)
    assert s.IsUPeriodic() is True
    assert s.IsUClosed() is True
    assert s.IsVPeriodic() is False
    assert s.IsVClosed() is False


def test_GeomEval_EllipsoidSurfaceTest_Iso_NotImplemented():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_EllipsoidSurfaceTest_Reverse_NotImplemented():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_EllipsoidSurfaceTest_Coefficients_SatisfiedAtEvalPoints():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.5)
    a1, a2, a3, b1, b2, b3, c1, c2, c3, d = s.Coefficients()
    tol = Precision.Intersection_s()
    for u in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]:
        for v in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            p = s.EvalD0(u, v)
            x, y, z = p.X(), p.Y(), p.Z()
            val = (a1 * x * x + a2 * y * y + a3 * z * z
                   + 2.0 * (b1 * x * y + b2 * x * z + b3 * y * z)
                   + 2.0 * (c1 * x + c2 * y + c3 * z) + d)
            assert near(val, 0.0, tol)


def test_GeomEval_EllipsoidSurfaceTest_Transform_NotImplemented():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(tr)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(tr)


def test_GeomEval_EllipsoidSurfaceTest_Copy_Independent():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    cp = s.Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_EllipsoidSurface)
    assert near(cp.SemiAxisA(), 3.0, CONF)
    assert near(cp.SemiAxisB(), 2.0, CONF)
    assert near(cp.SemiAxisC(), 1.0, CONF)


def test_GeomEval_EllipsoidSurfaceTest_DumpJson_NoCrash():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    assert isinstance(s.DumpJson(), str)


def _pair(r=5.0):
    return GeomEval_EllipsoidSurface(gp_Ax3(), r, r, r), Geom_SphericalSurface(gp_Ax3(), r)


def test_GeomEval_EllipsoidSurfaceTest_EvalD0_MatchesSphere():
    e, sp = _pair()
    for u, v in [(0.0, 0.0), (PI / 4.0, PI / 4.0), (PI / 2.0, 0.0), (PI, -PI / 4.0), (3.0 * PI / 2.0, 0.0), (1.0, 0.3)]:
        vnear(e.EvalD0(u, v), sp.EvalD0(u, v), CONF)


def test_GeomEval_EllipsoidSurfaceTest_EvalD1_MatchesSphere():
    e, sp = _pair()
    for u, v in [(0.0, 0.0), (PI / 4.0, PI / 4.0), (1.0, 0.3), (PI, -PI / 4.0)]:
        de, ds = e.EvalD1(u, v), sp.EvalD1(u, v)
        vnear(de.Point, ds.Point, CONF)
        for n in ("D1U", "D1V"):
            vnear(getattr(de, n), getattr(ds, n), ANG)


def test_GeomEval_EllipsoidSurfaceTest_EvalD2_MatchesSphere():
    e, sp = _pair()
    for u, v in [(0.0, 0.0), (PI / 4.0, PI / 4.0), (1.0, 0.3)]:
        de, ds = e.EvalD2(u, v), sp.EvalD2(u, v)
        vnear(de.Point, ds.Point, CONF)
        for n in ("D1U", "D1V", "D2U", "D2V", "D2UV"):
            vnear(getattr(de, n), getattr(ds, n), ANG)


def test_GeomEval_EllipsoidSurfaceTest_EvalD3_MatchesSphere():
    e, sp = _pair()
    for u, v in [(PI / 4.0, PI / 4.0), (1.0, 0.3)]:
        de, ds = e.EvalD3(u, v), sp.EvalD3(u, v)
        vnear(de.Point, ds.Point, CONF)
        for n in ("D1U", "D1V", "D2U", "D2V", "D2UV", "D3U", "D3V", "D3UUV", "D3UVV"):
            vnear(getattr(de, n), getattr(ds, n), ANG)


def test_GeomEval_EllipsoidSurfaceTest_EvalD2_ConsistentWithD1():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    u, v = 1.0, 0.5
    d2 = s.EvalD2(u, v)
    up, um = s.EvalD1(u + CONF, v), s.EvalD1(u - CONF, v)
    vp, vm = s.EvalD1(u, v + CONF), s.EvalD1(u, v - CONF)
    vnear(d2.D2U, fd(up.D1U, um.D1U), THE_FD_TOL)
    vnear(d2.D2V, fd(vp.D1V, vm.D1V), THE_FD_TOL)
    vnear(d2.D2UV, fd(vp.D1U, vm.D1U), THE_FD_TOL)


def test_GeomEval_EllipsoidSurfaceTest_EvalD3_ConsistentWithD2():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    u, v = 1.0, 0.5
    d3 = s.EvalD3(u, v)
    up, um = s.EvalD2(u + CONF, v), s.EvalD2(u - CONF, v)
    vp, vm = s.EvalD2(u, v + CONF), s.EvalD2(u, v - CONF)
    vnear(d3.D3U, fd(up.D2U, um.D2U), THE_FD_TOL)
    vnear(d3.D3V, fd(vp.D2V, vm.D2V), THE_FD_TOL)
    vnear(d3.D3UUV, fd(vp.D2U, vm.D2U), THE_FD_TOL)
    vnear(d3.D3UVV, fd(up.D2V, um.D2V), THE_FD_TOL)


def test_GeomEval_EllipsoidSurfaceTest_EvalDN_ConsistentWithD3():
    s = GeomEval_EllipsoidSurface(gp_Ax3(), 3.0, 2.0, 1.0)
    u, v = 1.0, 0.5
    d1 = s.EvalD1(u, v)
    vnear(s.EvalDN(u, v, 1, 0), d1.D1U, ANG)
    vnear(s.EvalDN(u, v, 0, 1), d1.D1V, ANG)
