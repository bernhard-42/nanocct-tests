# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dEval_AHTBezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2dEval import Geom2dEval_AHTBezierCurve as AHT
from nanocct.gp import gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NotImplemented

TOL = Precision.Confusion_s()
FD_D1, FD_D2, FD_D3 = 1e-5, 1e-4, 1e-3


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def poles(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a.SetValue(i, gp_Pnt2d(x, y))
    return a


def reals(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a.SetValue(i, w)
    return a


def full_basis():
    return AHT(poles((0, 0), (1, 0), (1, 1), (0, 1), (0, 1), (1, 0)), 1, 1.0, 1.0)


def polynomial():
    return AHT(poles((0, 0), (1, 1), (2, 0)), 2, 0.0, 0.0)


def rational():
    return AHT(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 2.0, 1.0), 2, 0.0, 0.0)


def fd_check(exact, plus, minus, tol):
    near(exact.X(), (plus.X() - minus.X()) / (2.0 * TOL), tol)
    near(exact.Y(), (plus.Y() - minus.Y()) / (2.0 * TOL), tol)


def test_Geom2dEval_AHTBezierCurveTest_Construction_FullBasis():
    c = full_basis()
    assert c.NbPoles() == 6
    assert c.AlgDegree() == 1
    near(c.Alpha(), 1.0)
    near(c.Beta(), 1.0)
    assert c.IsRational() is False


def test_Geom2dEval_AHTBezierCurveTest_Construction_Polynomial():
    c = polynomial()
    assert c.NbPoles() == 3
    assert c.AlgDegree() == 2
    near(c.Alpha(), 0.0)
    near(c.Beta(), 0.0)
    assert c.IsRational() is False


def test_Geom2dEval_AHTBezierCurveTest_Construction_HyperbolicOnly():
    c = AHT(poles((0, 0), (1, 1), (2, 0)), 0, 2.0, 0.0)
    assert c.NbPoles() == 3
    assert c.AlgDegree() == 0
    near(c.Alpha(), 2.0)
    near(c.Beta(), 0.0)


def test_Geom2dEval_AHTBezierCurveTest_Construction_Rational():
    c = rational()
    assert c.IsRational() is True
    assert c.NbPoles() == 3
    assert c.AlgDegree() == 2


def test_Geom2dEval_AHTBezierCurveTest_IsRational_NonRational():
    assert polynomial().IsRational() is False


def test_Geom2dEval_AHTBezierCurveTest_Bounds():
    c = full_basis()
    near(c.FirstParameter(), 0.0)
    near(c.LastParameter(), 1.0)


def test_Geom2dEval_AHTBezierCurveTest_EvalD0_Endpoints():
    c = full_basis()
    near(c.EvalD0(c.FirstParameter()).Distance(c.StartPoint()), 0.0)
    near(c.EvalD0(c.LastParameter()).Distance(c.EndPoint()), 0.0)


def test_Geom2dEval_AHTBezierCurveTest_EvalD0_KnownPoint():
    p = polynomial().EvalD0(0.5)
    near(p.X(), 1.0)
    near(p.Y(), 0.5)


def test_Geom2dEval_AHTBezierCurveTest_EvalD1_ConsistentWithD0():
    c, u = full_basis(), 0.4
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_AHTBezierCurveTest_EvalD1_Polynomial_ConsistentWithD0():
    c, u = polynomial(), 0.3
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_AHTBezierCurveTest_EvalD1_Rational_ConsistentWithD0():
    c, u = rational(), 0.5
    fd_check(c.EvalD1(u).D1, c.EvalD0(u + TOL), c.EvalD0(u - TOL), FD_D1)


def test_Geom2dEval_AHTBezierCurveTest_Accessors():
    c = AHT(poles((0, 0), (1, 0), (2, 1), (3, 1), (4, 0)), 2, 0.0, 3.5)
    assert c.NbPoles() == 5
    assert c.AlgDegree() == 2
    near(c.Alpha(), 0.0)
    near(c.Beta(), 3.5)


def test_Geom2dEval_AHTBezierCurveTest_Periodicity():
    assert full_basis().IsPeriodic() is False


def test_Geom2dEval_AHTBezierCurveTest_Continuity():
    c = full_basis()
    assert c.Continuity() == GeomAbs_CN
    assert c.IsCN(0) is True
    assert c.IsCN(5) is True
    assert c.IsCN(100) is True


def test_Geom2dEval_AHTBezierCurveTest_Transform_NotImplemented():
    c = full_basis()
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(1.0, 2.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(t)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(t)


def test_Geom2dEval_AHTBezierCurveTest_Copy_Independent():
    c = full_basis()
    cp = c.Copy()
    assert isinstance(cp, AHT)
    assert cp.NbPoles() == 6
    assert cp.AlgDegree() == 1
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        near(c.EvalD0(u).Distance(cp.EvalD0(u)), 0.0)
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10.0, 10.0))
    with pytest.raises(Standard_NotImplemented):
        cp.Transform(t)
    near(c.EvalD0(0.5).Distance(cp.EvalD0(0.5)), 0.0)


def test_Geom2dEval_AHTBezierCurveTest_Copy_Rational():
    cp = rational().Copy()
    assert isinstance(cp, AHT)
    assert cp.IsRational() is True


def test_Geom2dEval_AHTBezierCurveTest_DumpJson_NoCrash():
    assert isinstance(full_basis().DumpJson(), str)


def test_Geom2dEval_AHTBezierCurveTest_DumpJson_Rational_NoCrash():
    assert isinstance(rational().DumpJson(), str)


def test_Geom2dEval_AHTBezierCurveTest_Construction_PoleCountMismatch_Throws():
    with pytest.raises(Standard_ConstructionError):
        AHT(poles((0, 0), (1, 0), (1, 1), (0, 1)), 1, 1.0, 1.0)


def test_Geom2dEval_AHTBezierCurveTest_Construction_NegativeAlpha_Throws():
    with pytest.raises(Standard_ConstructionError):
        AHT(poles((0, 0), (1, 0), (2, 0)), 2, -1.0, 0.0)


def test_Geom2dEval_AHTBezierCurveTest_Construction_NegativeBeta_Throws():
    with pytest.raises(Standard_ConstructionError):
        AHT(poles((0, 0), (1, 0), (2, 0)), 2, 0.0, -1.0)


def test_Geom2dEval_AHTBezierCurveTest_Construction_WeightCountMismatch_Throws():
    with pytest.raises(Standard_ConstructionError):
        AHT(poles((0, 0), (1, 1), (2, 0)), reals(1.0, 1.0), 2, 0.0, 0.0)


def test_Geom2dEval_AHTBezierCurveTest_Construction_NonPositiveWeight_Throws():
    with pytest.raises(Standard_ConstructionError):
        AHT(poles((0, 0), (1, 1), (2, 0)), reals(1.0, -1.0, 1.0), 2, 0.0, 0.0)


def test_Geom2dEval_AHTBezierCurveTest_Reverse_NotImplemented():
    c = full_basis()
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def test_Geom2dEval_AHTBezierCurveTest_EvalD2_ConsistentWithD1():
    c, u = full_basis(), 0.3
    fd_check(c.EvalD2(u).D2, c.EvalD1(u + TOL).D1, c.EvalD1(u - TOL).D1, FD_D2)


def test_Geom2dEval_AHTBezierCurveTest_EvalD3_ConsistentWithD2():
    c, u = full_basis(), 0.4
    fd_check(c.EvalD3(u).D3, c.EvalD2(u + TOL).D2, c.EvalD2(u - TOL).D2, FD_D3)


def test_Geom2dEval_AHTBezierCurveTest_EvalDN_ConsistentWithD1():
    c, u = full_basis(), 0.5
    d1, dn = c.EvalD1(u).D1, c.EvalDN(u, 1)
    near(d1.X(), dn.X())
    near(d1.Y(), dn.Y())


def test_Geom2dEval_AHTBezierCurveTest_EvalD0_PurePolynomial_Line():
    c = AHT(poles((0, 0), (1, 1)), 1, 0.0, 0.0)
    p = c.EvalD0(0.5)
    near(p.X(), 0.5)
    near(p.Y(), 0.5)
    e = c.EvalD0(1.0)
    near(e.X(), 1.0)
    near(e.Y(), 1.0)
