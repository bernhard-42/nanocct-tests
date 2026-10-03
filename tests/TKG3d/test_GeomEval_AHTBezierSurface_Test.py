# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_AHTBezierSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.GeomEval import GeomEval_AHTBezierSurface
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array2
from nanocct.Precision import Precision
from nanocct.Standard import Standard_NotImplemented

CONF = Precision.Confusion_s()
THE_FD_TOL_D1 = 1e-5
THE_FD_TOL_D2 = 1e-4


def near(a, b, tol):
    return abs(a - b) <= tol


def vnear(a, b, tol):
    assert near(a.X(), b.X(), tol)
    assert near(a.Y(), b.Y(), tol)
    assert near(a.Z(), b.Z(), tol)


def fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def vec_diff(a, b):
    return (a - b).Magnitude()


def _poles():
    pp = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            pp.SetValue(i, j, gp_Pnt(float(i - 1), float(j - 1), float((i - 1) * (j - 1)) * 0.1))
    return pp


def create_polynomial_surface():
    return GeomEval_AHTBezierSurface(_poles(), 2, 2, 0.0, 0.0, 0.0, 0.0)


def create_polynomial_surface_rational_uniform_weight(w):
    ww = NCollection_Array2[float](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            ww.SetValue(i, j, w)
    return GeomEval_AHTBezierSurface(_poles(), ww, 2, 2, 0.0, 0.0, 0.0, 0.0)


def test_GeomEval_AHTBezierSurfaceTest_Construction_ValidParams():
    s = create_polynomial_surface()
    assert s.NbPolesU() == 3
    assert s.NbPolesV() == 3
    assert s.AlgDegreeU() == 2
    assert s.AlgDegreeV() == 2
    for x in (s.AlphaU(), s.AlphaV(), s.BetaU(), s.BetaV()):
        assert near(x, 0.0, CONF)


def test_GeomEval_AHTBezierSurfaceTest_ParameterRange():
    u1, u2, v1, v2 = create_polynomial_surface().Bounds()
    assert near(u1, 0.0, CONF)
    assert near(u2, 1.0, CONF)
    assert near(v1, 0.0, CONF)
    assert near(v2, 1.0, CONF)


def test_GeomEval_AHTBezierSurfaceTest_EvalD0_Corners():
    s = create_polynomial_surface()
    p00 = s.EvalD0(0.0, 0.0)
    assert p00.Distance(s.EvalD0(1.0, 0.0)) > CONF
    assert p00.Distance(s.EvalD0(0.0, 1.0)) > CONF
    assert p00.Distance(s.EvalD0(1.0, 1.0)) > CONF


def test_GeomEval_AHTBezierSurfaceTest_EvalD1_ConsistentWithD0():
    s = create_polynomial_surface()
    u, v = 0.3, 0.7
    d1 = s.EvalD1(u, v)
    vnear(d1.D1U, fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL_D1)
    vnear(d1.D1V, fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL_D1)


def test_GeomEval_AHTBezierSurfaceTest_Periodicity():
    s = create_polynomial_surface()
    assert s.IsUPeriodic() is False
    assert s.IsVPeriodic() is False
    assert s.IsUClosed() is False
    assert s.IsVClosed() is False


def test_GeomEval_AHTBezierSurfaceTest_Reverse_NotImplemented():
    s = create_polynomial_surface()
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_AHTBezierSurfaceTest_Iso_NotImplemented():
    s = create_polynomial_surface()
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_AHTBezierSurfaceTest_Transform_NotImplemented():
    s = create_polynomial_surface()
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(tr)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(tr)


def test_GeomEval_AHTBezierSurfaceTest_Copy_Independent():
    cp = create_polynomial_surface().Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_AHTBezierSurface)
    assert cp.NbPolesU() == 3
    assert cp.NbPolesV() == 3
    assert cp.AlgDegreeU() == 2


def test_GeomEval_AHTBezierSurfaceTest_DumpJson_NoCrash():
    assert isinstance(create_polynomial_surface().DumpJson(), str)


def test_GeomEval_AHTBezierSurfaceTest_EvalD2_ConsistentWithD1():
    s = create_polynomial_surface()
    u, v = 0.3, 0.4
    d2 = s.EvalD2(u, v)
    up, um = s.EvalD1(u + CONF, v), s.EvalD1(u - CONF, v)
    vp, vm = s.EvalD1(u, v + CONF), s.EvalD1(u, v - CONF)
    vnear(d2.D2U, fd(up.D1U, um.D1U), THE_FD_TOL_D2)
    vnear(d2.D2V, fd(vp.D1V, vm.D1V), THE_FD_TOL_D2)
    vnear(d2.D2UV, fd(vp.D1U, vm.D1U), THE_FD_TOL_D2)


def test_GeomEval_AHTBezierSurfaceTest_EvalD3_ConsistentWithD2():
    s = create_polynomial_surface()
    u, v = 0.4, 0.3
    d3 = s.EvalD3(u, v)
    up, um = s.EvalD2(u + CONF, v), s.EvalD2(u - CONF, v)
    vp, vm = s.EvalD2(u, v + CONF), s.EvalD2(u, v - CONF)
    vnear(d3.D3U, fd(up.D2U, um.D2U), THE_FD_TOL_D2)
    vnear(d3.D3V, fd(vp.D2V, vm.D2V), THE_FD_TOL_D2)
    vnear(d3.D3UUV, fd(vp.D2U, vm.D2U), THE_FD_TOL_D2)
    vnear(d3.D3UVV, fd(up.D2V, um.D2V), THE_FD_TOL_D2)


def test_GeomEval_AHTBezierSurfaceTest_EvalDN_ConsistentWithD1():
    s = create_polynomial_surface()
    d1 = s.EvalD1(0.5, 0.5)
    vnear(d1.D1U, s.EvalDN(0.5, 0.5, 1, 0), CONF)
    vnear(d1.D1V, s.EvalDN(0.5, 0.5, 0, 1), CONF)


def test_GeomEval_AHTBezierSurfaceTest_RationalUniformScale_Invariant():
    w1 = create_polynomial_surface_rational_uniform_weight(1.0)
    w5 = create_polynomial_surface_rational_uniform_weight(5.0)
    u, v = 0.37, 0.62
    assert near(w1.EvalD0(u, v).Distance(w5.EvalD0(u, v)), 0.0, 1e-12)
    for meth, names in [
        ("EvalD1", ("D1U", "D1V")),
        ("EvalD2", ("D2U", "D2V", "D2UV")),
        ("EvalD3", ("D3U", "D3V", "D3UUV", "D3UVV")),
    ]:
        r1, r5 = getattr(w1, meth)(u, v), getattr(w5, meth)(u, v)
        for n in names:
            assert near(vec_diff(getattr(r1, n), getattr(r5, n)), 0.0, 1e-12), (meth, n)
    assert near(vec_diff(w1.EvalDN(u, v, 2, 1), w5.EvalDN(u, v, 2, 1)), 0.0, 1e-12)
