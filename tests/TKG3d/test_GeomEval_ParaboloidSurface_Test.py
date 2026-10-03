# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_ParaboloidSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomEval import GeomEval_ParaboloidSurface
from nanocct.gp import gp_Ax3, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

THE_FD_TOL = 1e-5
THE_FD_TOL_D3 = 1e-4
CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def _near_vec(a, b, tol):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def _fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def _surf(f=1.0):
    return GeomEval_ParaboloidSurface(gp_Ax3(), f)


def test_GeomEval_ParaboloidSurfaceTest_Construction_ValidParams():
    assert abs(_surf(1.0).Focal() - 1.0) <= CONF


def test_GeomEval_ParaboloidSurfaceTest_Construction_InvalidFocal_Throws():
    with pytest.raises(Standard_ConstructionError):
        GeomEval_ParaboloidSurface(gp_Ax3(), -1.0)
    with pytest.raises(Standard_ConstructionError):
        GeomEval_ParaboloidSurface(gp_Ax3(), 0.0)


def test_GeomEval_ParaboloidSurfaceTest_EvalD0_Origin():
    p = _surf().EvalD0(0.0, 0.0)
    assert abs(p.X()) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z()) <= CONF


def test_GeomEval_ParaboloidSurfaceTest_EvalD0_KnownPoint():
    p = _surf(1.0).EvalD0(0.0, 2.0)
    assert abs(p.X() - 2.0) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z() - 1.0) <= CONF


def test_GeomEval_ParaboloidSurfaceTest_EvalD1_ConsistentWithD0():
    s = _surf(2.0)
    u, v = 1.0, 1.5
    d1 = s.EvalD1(u, v)
    _near_vec(d1.D1U, _fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL)
    _near_vec(d1.D1V, _fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL)


def test_GeomEval_ParaboloidSurfaceTest_Bounds_Periodicity():
    s = _surf(1.0)
    u1, u2, v1, v2 = s.Bounds()
    assert abs(u1) <= CONF
    assert abs(u2 - 2.0 * math.pi) <= CONF
    assert s.IsUPeriodic() is True
    assert s.IsUClosed() is True
    assert s.IsVPeriodic() is False
    assert s.IsVClosed() is False


def test_GeomEval_ParaboloidSurfaceTest_Iso_NotImplemented():
    s = _surf()
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_ParaboloidSurfaceTest_Reverse_NotImplemented():
    s = _surf()
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_ParaboloidSurfaceTest_Coefficients_SatisfiedAtEvalPoints():
    s = _surf(1.5)
    a1, a2, a3, b1, b2, b3, c1, c2, c3, d = s.Coefficients()
    for u in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0):
        for v in (-2.0, -1.0, 0.0, 1.0, 2.0):
            p = s.EvalD0(u, v)
            x, y, z = p.X(), p.Y(), p.Z()
            val = (
                a1 * x * x + a2 * y * y + a3 * z * z
                + 2.0 * (b1 * x * y + b2 * x * z + b3 * y * z)
                + 2.0 * (c1 * x + c2 * y + c3 * z) + d
            )
            assert abs(val) <= Precision.Intersection_s()


def test_GeomEval_ParaboloidSurfaceTest_Transform_NotImplemented():
    s = _surf()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(trsf)


def test_GeomEval_ParaboloidSurfaceTest_Copy_Independent():
    cp = _surf(2.0).Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_ParaboloidSurface)
    assert abs(cp.Focal() - 2.0) <= CONF


def test_GeomEval_ParaboloidSurfaceTest_DumpJson_NoCrash():
    assert isinstance(_surf().DumpJson(), str)


def test_GeomEval_ParaboloidSurfaceTest_EvalD2_ConsistentWithD1():
    s = _surf(2.0)
    u, v = 1.0, 1.5
    d2 = s.EvalD2(u, v)
    uf = s.EvalD1(u + CONF, v)
    ub = s.EvalD1(u - CONF, v)
    vf = s.EvalD1(u, v + CONF)
    vb = s.EvalD1(u, v - CONF)
    _near_vec(d2.D2U, _fd(uf.D1U, ub.D1U), THE_FD_TOL)
    _near_vec(d2.D2V, _fd(vf.D1V, vb.D1V), THE_FD_TOL)
    _near_vec(d2.D2UV, _fd(vf.D1U, vb.D1U), THE_FD_TOL)


def test_GeomEval_ParaboloidSurfaceTest_EvalD3_ConsistentWithD2():
    s = _surf(2.0)
    u, v = 0.7, 1.2
    d3 = s.EvalD3(u, v)
    uf = s.EvalD2(u + CONF, v)
    ub = s.EvalD2(u - CONF, v)
    vf = s.EvalD2(u, v + CONF)
    vb = s.EvalD2(u, v - CONF)
    _near_vec(d3.D3U, _fd(uf.D2U, ub.D2U), THE_FD_TOL_D3)
    _near_vec(d3.D3V, _fd(vf.D2V, vb.D2V), THE_FD_TOL_D3)
    _near_vec(d3.D3UUV, _fd(vf.D2U, vb.D2U), THE_FD_TOL_D3)
    _near_vec(d3.D3UVV, _fd(uf.D2V, ub.D2V), THE_FD_TOL_D3)


def test_GeomEval_ParaboloidSurfaceTest_EvalD2_KnownAnalytical():
    u, v = math.pi / 4.0, 2.0
    d2 = _surf(2.0).EvalD2(u, v)
    assert abs(d2.D2U.X() + v * math.cos(u)) <= ANG
    assert abs(d2.D2U.Y() + v * math.sin(u)) <= ANG
    assert abs(d2.D2U.Z()) <= ANG
    assert abs(d2.D2U.Magnitude() - v) <= ANG


def test_GeomEval_ParaboloidSurfaceTest_EvalDN_Consistency():
    s = _surf(2.0)
    u, v = 1.0, 1.0
    d1 = s.EvalD1(u, v)
    _near_vec(s.EvalDN(u, v, 1, 0), d1.D1U, CONF)
    _near_vec(s.EvalDN(u, v, 0, 1), d1.D1V, CONF)
