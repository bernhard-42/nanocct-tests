# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_HypParaboloidSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_BezierSurface
from nanocct.GeomEval import GeomEval_HypParaboloidSurface
from nanocct.gp import gp_Ax3, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array2
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

THE_FD_TOL = 1e-5
CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()
SQCONF = Precision.SquareConfusion_s()


def _near_vec(a, b, tol):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def _fd(a, b):
    return gp_Vec((a.XYZ() - b.XYZ()) / (2.0 * CONF))


def _surf(a=2.0, b=3.0):
    return GeomEval_HypParaboloidSurface(gp_Ax3(), a, b)


def test_GeomEval_HypParaboloidSurfaceTest_Construction_ValidParams():
    s = _surf()
    assert abs(s.SemiAxisA() - 2.0) <= CONF
    assert abs(s.SemiAxisB() - 3.0) <= CONF


def test_GeomEval_HypParaboloidSurfaceTest_Construction_InvalidAxes_Throws():
    for a, b in ((-1.0, 1.0), (1.0, 0.0), (0.0, 1.0)):
        with pytest.raises(Standard_ConstructionError):
            GeomEval_HypParaboloidSurface(gp_Ax3(), a, b)


def test_GeomEval_HypParaboloidSurfaceTest_EvalD0_Origin():
    p = _surf().EvalD0(0.0, 0.0)
    assert abs(p.X()) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z()) <= CONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD0_KnownPoint_U():
    a = 2.0
    p = _surf().EvalD0(1.0, 0.0)
    assert abs(p.X() - 1.0) <= CONF
    assert abs(p.Y()) <= CONF
    assert abs(p.Z() - 1.0 / (a * a)) <= CONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD0_KnownPoint_V():
    b = 3.0
    p = _surf().EvalD0(0.0, 1.0)
    assert abs(p.X()) <= CONF
    assert abs(p.Y() - 1.0) <= CONF
    assert abs(p.Z() + 1.0 / (b * b)) <= CONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD1_ConsistentWithD0():
    s = _surf()
    u, v = 1.5, 0.7
    d1 = s.EvalD1(u, v)
    _near_vec(d1.D1U, _fd(s.EvalD0(u + CONF, v), s.EvalD0(u - CONF, v)), THE_FD_TOL)
    _near_vec(d1.D1V, _fd(s.EvalD0(u, v + CONF), s.EvalD0(u, v - CONF)), THE_FD_TOL)


def test_GeomEval_HypParaboloidSurfaceTest_EvalD2_ConstantZComponent():
    a, b = 2.0, 3.0
    s = _surf(a, b)
    exp_u = 2.0 / (a * a)
    exp_v = -2.0 / (b * b)
    for uv in ((0.0, 0.0), (1.0, 2.0), (-3.0, 5.0)):
        d2 = s.EvalD2(*uv)
        assert abs(d2.D2U.Z() - exp_u) <= ANG
        assert abs(d2.D2V.Z() - exp_v) <= ANG


def test_GeomEval_HypParaboloidSurfaceTest_Bounds_Periodicity():
    s = _surf(1.0, 1.0)
    u1, u2, v1, v2 = s.Bounds()
    assert u1 < -1e10
    assert u2 > 1e10
    assert v1 < -1e10
    assert v2 > 1e10
    assert s.IsUPeriodic() is False
    assert s.IsUClosed() is False
    assert s.IsVPeriodic() is False
    assert s.IsVClosed() is False


def test_GeomEval_HypParaboloidSurfaceTest_Iso_NotImplemented():
    s = _surf()
    with pytest.raises(Standard_NotImplemented):
        s.UIso(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VIso(0.5)


def test_GeomEval_HypParaboloidSurfaceTest_Reverse_NotImplemented():
    s = _surf()
    with pytest.raises(Standard_NotImplemented):
        s.UReverse()
    with pytest.raises(Standard_NotImplemented):
        s.VReverse()
    with pytest.raises(Standard_NotImplemented):
        s.UReversedParameter(0.5)
    with pytest.raises(Standard_NotImplemented):
        s.VReversedParameter(0.5)


def test_GeomEval_HypParaboloidSurfaceTest_Coefficients_SatisfiedAtEvalPoints():
    s = _surf()
    a1, a2, a3, b1, b2, b3, c1, c2, c3, d = s.Coefficients()
    for u in (-2.0, -1.0, 0.0, 1.0, 2.0):
        for v in (-2.0, -1.0, 0.0, 1.0, 2.0):
            p = s.EvalD0(u, v)
            x, y, z = p.X(), p.Y(), p.Z()
            val = (
                a1 * x * x + a2 * y * y + a3 * z * z
                + 2.0 * (b1 * x * y + b2 * x * z + b3 * y * z)
                + 2.0 * (c1 * x + c2 * y + c3 * z) + d
            )
            assert abs(val) <= Precision.Intersection_s()


def test_GeomEval_HypParaboloidSurfaceTest_Transform_NotImplemented():
    s = _surf()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        s.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        s.Transformed(trsf)


def test_GeomEval_HypParaboloidSurfaceTest_Copy_Independent():
    cp = _surf().Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_HypParaboloidSurface)
    assert abs(cp.SemiAxisA() - 2.0) <= CONF
    assert abs(cp.SemiAxisB() - 3.0) <= CONF


def test_GeomEval_HypParaboloidSurfaceTest_DumpJson_NoCrash():
    assert isinstance(_surf().DumpJson(), str)


def test_GeomEval_HypParaboloidSurfaceTest_EvalD3_Zero():
    d3 = _surf().EvalD3(1.0, 1.0)
    assert d3.D3U.Magnitude() < SQCONF
    assert d3.D3V.Magnitude() < SQCONF
    assert d3.D3UUV.Magnitude() < SQCONF
    assert d3.D3UVV.Magnitude() < SQCONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD2_CrossDerivative():
    s = _surf()
    for uv in ((0.0, 0.0), (1.5, -2.0), (-3.0, 4.5)):
        d2 = s.EvalD2(*uv)
        assert abs(d2.D2UV.X()) <= SQCONF
        assert abs(d2.D2UV.Y()) <= SQCONF
        assert abs(d2.D2UV.Z()) <= SQCONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD2_KnownValues():
    a, b = 2.0, 3.0
    d2 = _surf(a, b).EvalD2(1.5, -2.7)
    assert abs(d2.D2U.X()) <= SQCONF
    assert abs(d2.D2U.Y()) <= SQCONF
    assert abs(d2.D2U.Z() - 2.0 / (a * a)) <= ANG
    assert abs(d2.D2V.X()) <= SQCONF
    assert abs(d2.D2V.Y()) <= SQCONF
    assert abs(d2.D2V.Z() + 2.0 / (b * b)) <= ANG


def test_GeomEval_HypParaboloidSurfaceTest_EvalDN_HigherOrder():
    s = _surf()
    u, v = 1.0, 1.0
    d2 = s.EvalD2(u, v)
    _near_vec(s.EvalDN(u, v, 2, 0), d2.D2U, CONF)
    _near_vec(s.EvalDN(u, v, 0, 2), d2.D2V, CONF)
    assert s.EvalDN(u, v, 3, 0).Magnitude() < SQCONF


def test_GeomEval_HypParaboloidSurfaceTest_EvalD2_MatchesBezierSurface():
    a, b = 2.0, 3.0
    s = _surf(a, b)
    inv_a2 = 1.0 / (a * a)
    inv_b2 = 1.0 / (b * b)
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        xi = 0.5 * (i - 1)
        zu = inv_a2 if i == 3 else 0.0
        for j in range(1, 4):
            yj = 0.5 * (j - 1)
            zv = -inv_b2 if j == 3 else 0.0
            poles[i, j] = gp_Pnt(xi, yj, zu + zv)
    bez = Geom_BezierSurface(poles)
    for uv in ((0.0, 0.0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.25), (0.3, 0.7), (1.0, 1.0)):
        dh = s.EvalD2(*uv)
        db = bez.EvalD2(*uv)
        assert abs(dh.Point.Distance(db.Point)) <= ANG, f"Point mismatch at {uv}"
        _near_vec(dh.D1U, db.D1U, ANG)
        _near_vec(dh.D1V, db.D1V, ANG)
        _near_vec(dh.D2U, db.D2U, ANG)
        _near_vec(dh.D2V, db.D2V, ANG)
        _near_vec(dh.D2UV, db.D2UV, ANG)
