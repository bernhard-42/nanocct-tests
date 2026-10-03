# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_HyperboloidSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomEval import GeomEval_HyperboloidSurface
from nanocct.gp import gp_Ax3, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

THE_FD_TOL = 1e-5
THE_FD_TOL_D3 = 1e-4
CONF = Precision.Confusion_s()
Mode = GeomEval_HyperboloidSurface.SheetMode


def _near_vec(a, b, tol):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def _fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def _check_coefficients(surf):
    a1, a2, a3, b1, b2, b3, c1, c2, c3, d = surf.Coefficients()
    u = 0.0
    while u < 6.0:
        v = -1.0
        while v <= 1.0:
            p = surf.EvalD0(u, v)
            x, y, z = p.X(), p.Y(), p.Z()
            val = (
                a1 * x * x + a2 * y * y + a3 * z * z
                + 2.0 * (b1 * x * y + b2 * x * z + b3 * y * z)
                + 2.0 * (c1 * x + c2 * y + c3 * z) + d
            )
            assert abs(val) <= Precision.Intersection_s()
            v += 0.5
        u += 1.0


def _check_d2(surf, u, v):
    d2 = surf.EvalD2(u, v)
    uf = surf.EvalD1(u + CONF, v)
    ub = surf.EvalD1(u - CONF, v)
    vf = surf.EvalD1(u, v + CONF)
    vb = surf.EvalD1(u, v - CONF)
    _near_vec(d2.D2U, _fd(uf.D1U, ub.D1U), THE_FD_TOL)
    _near_vec(d2.D2V, _fd(vf.D1V, vb.D1V), THE_FD_TOL)
    _near_vec(d2.D2UV, _fd(vf.D1U, vb.D1U), THE_FD_TOL)


def test_GeomEval_HyperboloidSurfaceTest_Construction_ValidParams_OneSheet():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    assert abs(s.R1() - 2.0) <= CONF
    assert abs(s.R2() - 3.0) <= CONF
    assert s.Mode() == Mode.OneSheet


def test_GeomEval_HyperboloidSurfaceTest_Construction_ValidParams_TwoSheets():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0, Mode.TwoSheets)
    assert s.Mode() == Mode.TwoSheets


def test_GeomEval_HyperboloidSurfaceTest_Construction_InvalidRadii_Throws():
    ax = gp_Ax3()
    for r1, r2 in ((0.0, 1.0), (1.0, 0.0), (-1.0, 1.0), (1.0, -1.0), (-2.0, -3.0)):
        with pytest.raises(Standard_ConstructionError):
            GeomEval_HyperboloidSurface(ax, r1, r2)


def test_GeomEval_HyperboloidSurfaceTest_Setters_ZeroRadii_Throw():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    with pytest.raises(Standard_ConstructionError):
        s.SetR1(0.0)
    with pytest.raises(Standard_ConstructionError):
        s.SetR2(0.0)


def test_GeomEval_HyperboloidSurfaceTest_EvalD0_OneSheet_Origin():
    p = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0).EvalD0(0.0, 0.0)
    assert abs(p.X() - 2.0) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z()) <= CONF


def test_GeomEval_HyperboloidSurfaceTest_EvalD0_OneSheet_HalfPi():
    p = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0).EvalD0(math.pi / 2.0, 0.0)
    assert abs(p.X()) <= CONF
    assert abs(p.Y() - 2.0) <= CONF
    assert abs(p.Z()) <= CONF


def test_GeomEval_HyperboloidSurfaceTest_EvalD0_TwoSheets_Origin():
    p = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0, Mode.TwoSheets).EvalD0(0.0, 0.0)
    assert abs(p.X()) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z() - 2.0) <= CONF


def test_GeomEval_HyperboloidSurfaceTest_EvalD1_ConsistentWithD0():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    u, v = 1.0, 0.5
    d1 = s.EvalD1(u, v)
    _near_vec(d1.D1U, _fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL)
    _near_vec(d1.D1V, _fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL)


def test_GeomEval_HyperboloidSurfaceTest_Bounds_Periodicity():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 1.0, 1.0)
    u1, u2, v1, v2 = s.Bounds()
    assert abs(u1) <= CONF
    assert abs(u2 - 2.0 * math.pi) <= CONF
    assert s.IsUPeriodic() is True
    assert s.IsUClosed() is True
    assert s.IsVPeriodic() is False
    assert s.IsVClosed() is False


def test_GeomEval_HyperboloidSurfaceTest_Iso_NotImplemented():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_HyperboloidSurfaceTest_Reverse_NotImplemented():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_HyperboloidSurfaceTest_Coefficients_OneSheet_SatisfiedAtEvalPoints():
    _check_coefficients(GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0))


def test_GeomEval_HyperboloidSurfaceTest_Coefficients_TwoSheets_SatisfiedAtEvalPoints():
    _check_coefficients(GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0, Mode.TwoSheets))


def test_GeomEval_HyperboloidSurfaceTest_Transform_NotImplemented():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(trsf)


def test_GeomEval_HyperboloidSurfaceTest_Copy_Independent():
    cp = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0).Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_HyperboloidSurface)
    assert abs(cp.R1() - 2.0) <= CONF
    assert abs(cp.R2() - 3.0) <= CONF


def test_GeomEval_HyperboloidSurfaceTest_DumpJson_NoCrash():
    assert isinstance(GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0).DumpJson(), str)


def test_GeomEval_HyperboloidSurfaceTest_EvalD2_ConsistentWithD1():
    _check_d2(GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0), 0.7, 0.5)


def test_GeomEval_HyperboloidSurfaceTest_EvalD3_ConsistentWithD2():
    s = GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0)
    u, v = 1.0, 0.3
    d3 = s.EvalD3(u, v)
    uf = s.EvalD2(u + CONF, v)
    ub = s.EvalD2(u - CONF, v)
    vf = s.EvalD2(u, v + CONF)
    vb = s.EvalD2(u, v - CONF)
    _near_vec(d3.D3U, _fd(uf.D2U, ub.D2U), THE_FD_TOL_D3)
    _near_vec(d3.D3V, _fd(vf.D2V, vb.D2V), THE_FD_TOL_D3)
    _near_vec(d3.D3UUV, _fd(vf.D2U, vb.D2U), THE_FD_TOL_D3)
    _near_vec(d3.D3UVV, _fd(uf.D2V, ub.D2V), THE_FD_TOL_D3)


def test_GeomEval_HyperboloidSurfaceTest_EvalD2_TwoSheets_ConsistentWithD1():
    _check_d2(GeomEval_HyperboloidSurface(gp_Ax3(), 2.0, 3.0, Mode.TwoSheets), 0.7, 0.5)
