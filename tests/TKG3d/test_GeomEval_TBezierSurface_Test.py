# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_TBezierSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_SphericalSurface
from nanocct.GeomEval import GeomEval_TBezierSurface
from nanocct.gp import gp_Ax3, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array2
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

THE_FD_TOL_D1 = 1e-5
THE_FD_TOL_D2 = 1e-4
CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def _near_vec(a, b, tol):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def _fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def create_sphere_patch():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles[i, j] = gp_Pnt(0.0, 0.0, 0.0)
    poles[1, 2] = gp_Pnt(0.0, 0.0, 1.0)
    poles[2, 3] = gp_Pnt(0.0, 1.0, 0.0)
    poles[3, 3] = gp_Pnt(1.0, 0.0, 0.0)
    return GeomEval_TBezierSurface(poles, 1.0, 1.0)


def create_simple_surface():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles[i, j] = gp_Pnt(float(i - 1), float(j - 1), 0.0)
    return GeomEval_TBezierSurface(poles, 1.0, 1.0)


def test_GeomEval_TBezierSurfaceTest_Construction_ValidParams():
    s = create_simple_surface()
    assert s.NbUPoles() == 3
    assert s.NbVPoles() == 3
    assert s.OrderU() == 1
    assert s.OrderV() == 1
    assert abs(s.AlphaU() - 1.0) <= CONF
    assert abs(s.AlphaV() - 1.0) <= CONF
    assert s.IsRational() is False


def test_GeomEval_TBezierSurfaceTest_Construction_InvalidParams_Throws():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 3)
    for i in range(1, 3):
        for j in range(1, 4):
            poles[i, j] = gp_Pnt(float(i), float(j), 0.0)
    with pytest.raises(Standard_ConstructionError):
        GeomEval_TBezierSurface(poles, 1.0, 1.0)


def test_GeomEval_TBezierSurfaceTest_ParameterRange():
    u1, u2, v1, v2 = create_simple_surface().Bounds()
    assert abs(u1) <= CONF
    assert abs(u2 - math.pi) <= CONF
    assert abs(v1) <= CONF
    assert abs(v2 - math.pi) <= CONF


def test_GeomEval_TBezierSurfaceTest_EvalD0_Corners():
    s = create_simple_surface()
    u1, u2, v1, v2 = s.Bounds()
    p00 = s.EvalD0(u1, v1)
    p10 = s.EvalD0(u2, v1)
    p01 = s.EvalD0(u1, v2)
    p11 = s.EvalD0(u2, v2)
    assert p00.Distance(p10) > CONF
    assert p00.Distance(p01) > CONF
    assert p00.Distance(p11) > CONF


def test_GeomEval_TBezierSurfaceTest_EvalD1_ConsistentWithD0():
    s = create_simple_surface()
    u, v = math.pi / 3.0, math.pi / 4.0
    d1 = s.EvalD1(u, v)
    _near_vec(d1.D1U, _fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL_D1)
    _near_vec(d1.D1V, _fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL_D1)


def test_GeomEval_TBezierSurfaceTest_Periodicity():
    s = create_simple_surface()
    assert s.IsUPeriodic() is False
    assert s.IsVPeriodic() is False


def test_GeomEval_TBezierSurfaceTest_Reverse_NotImplemented():
    s = create_simple_surface()
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_TBezierSurfaceTest_Iso_NotImplemented():
    s = create_simple_surface()
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_TBezierSurfaceTest_Transform_NotImplemented():
    s = create_simple_surface()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(trsf)


def test_GeomEval_TBezierSurfaceTest_Copy_Independent():
    cp = create_simple_surface().Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_TBezierSurface)
    assert cp.NbUPoles() == 3
    assert cp.NbVPoles() == 3


def test_GeomEval_TBezierSurfaceTest_DumpJson_NoCrash():
    assert isinstance(create_simple_surface().DumpJson(), str)


def test_GeomEval_TBezierSurfaceTest_EvalD2_ConsistentWithD1():
    s = create_simple_surface()
    u, v = math.pi / 4.0, math.pi / 4.0
    d2 = s.EvalD2(u, v)
    up = s.EvalD1(u + CONF, v)
    um = s.EvalD1(u - CONF, v)
    _near_vec(d2.D2U, _fd(up.D1U, um.D1U), THE_FD_TOL_D2)
    vp = s.EvalD1(u, v + CONF)
    vm = s.EvalD1(u, v - CONF)
    _near_vec(d2.D2V, _fd(vp.D1V, vm.D1V), THE_FD_TOL_D2)
    _near_vec(d2.D2UV, _fd(vp.D1U, vm.D1U), THE_FD_TOL_D2)


def test_GeomEval_TBezierSurfaceTest_EvalD3_ConsistentWithD2():
    s = create_simple_surface()
    u, v = math.pi / 3.0, math.pi / 3.0
    d3 = s.EvalD3(u, v)
    up = s.EvalD2(u + CONF, v)
    um = s.EvalD2(u - CONF, v)
    _near_vec(d3.D3U, _fd(up.D2U, um.D2U), THE_FD_TOL_D2)
    vp = s.EvalD2(u, v + CONF)
    vm = s.EvalD2(u, v - CONF)
    _near_vec(d3.D3V, _fd(vp.D2V, vm.D2V), THE_FD_TOL_D2)
    _near_vec(d3.D3UUV, _fd(vp.D2U, vm.D2U), THE_FD_TOL_D2)
    _near_vec(d3.D3UVV, _fd(up.D2V, um.D2V), THE_FD_TOL_D2)


def test_GeomEval_TBezierSurfaceTest_EvalDN_ConsistentWithD1():
    s = create_simple_surface()
    u, v = math.pi / 4.0, math.pi / 3.0
    d1 = s.EvalD1(u, v)
    _near_vec(d1.D1U, s.EvalDN(u, v, 1, 0), CONF)
    _near_vec(d1.D1V, s.EvalDN(u, v, 0, 1), CONF)


def test_GeomEval_TBezierSurfaceTest_EvalD0_MatchesSphere():
    tb = create_sphere_patch()
    sph = Geom_SphericalSurface(gp_Ax3(), 1.0)
    us = (0.1, math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2, 2 * math.pi / 3, 2.5)
    vs = (0.1, math.pi / 6, math.pi / 4, math.pi / 3, 1.2)
    for u in us:
        for v in vs:
            d = tb.EvalD0(u, v).Distance(sph.EvalD0(u, v))
            assert abs(d) <= ANG, f"D0 mismatch at u={u} v={v}"


def test_GeomEval_TBezierSurfaceTest_EvalD1_MatchesSphere():
    tb = create_sphere_patch()
    sph = Geom_SphericalSurface(gp_Ax3(), 1.0)
    for u in (math.pi / 6, math.pi / 3, math.pi / 2, 2 * math.pi / 3):
        for v in (0.2, math.pi / 4, math.pi / 3, 1.0):
            dt = tb.EvalD1(u, v)
            ds = sph.EvalD1(u, v)
            assert abs(dt.Point.Distance(ds.Point)) <= ANG
            _near_vec(dt.D1U, ds.D1U, ANG)
            _near_vec(dt.D1V, ds.D1V, ANG)


def test_GeomEval_TBezierSurfaceTest_EvalD2_MatchesSphere():
    tb = create_sphere_patch()
    sph = Geom_SphericalSurface(gp_Ax3(), 1.0)
    for u in (math.pi / 6, math.pi / 3, math.pi / 2):
        for v in (0.3, math.pi / 4, 1.0):
            dt = tb.EvalD2(u, v)
            ds = sph.EvalD2(u, v)
            assert abs(dt.Point.Distance(ds.Point)) <= ANG
            _near_vec(dt.D1U, ds.D1U, ANG)
            _near_vec(dt.D1V, ds.D1V, ANG)
            _near_vec(dt.D2U, ds.D2U, ANG)
            _near_vec(dt.D2V, ds.D2V, ANG)
            _near_vec(dt.D2UV, ds.D2UV, ANG)
