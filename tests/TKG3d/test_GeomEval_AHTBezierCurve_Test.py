# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_AHTBezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_Circle, Geom_Ellipse
from nanocct.GeomEval import GeomEval_AHTBezierCurve
from nanocct.gp import gp_Ax2, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.Standard import Standard_NotImplemented

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()
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


def poles(*pts):
    arr = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, start=1):
        arr[i] = gp_Pnt(*p)
    return arr


def create_full_basis_curve():
    pp = poles((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1))
    return GeomEval_AHTBezierCurve(pp, 1, 1.0, 1.0)


def create_trig_circle_arc():
    return GeomEval_AHTBezierCurve(poles((0, 0, 0), (0, 1, 0), (1, 0, 0)), 0, 0.0, 1.0)


def create_trig_ellipse_arc():
    return GeomEval_AHTBezierCurve(poles((0, 0, 0), (0, 2, 0), (3, 0, 0)), 0, 0.0, 1.0)


def create_polynomial_curve():
    return GeomEval_AHTBezierCurve(poles((0, 0, 0), (1, 1, 0), (2, 0, 0)), 2, 0.0, 0.0)


def test_GeomEval_AHTBezierCurveTest_Construction_FullBasis():
    c = create_full_basis_curve()
    assert c.NbPoles() == 6
    assert c.AlgDegree() == 1
    assert near(c.Alpha(), 1.0, CONF)
    assert near(c.Beta(), 1.0, CONF)
    assert c.IsRational() is False


def test_GeomEval_AHTBezierCurveTest_Construction_Polynomial():
    c = create_polynomial_curve()
    assert c.NbPoles() == 3
    assert c.AlgDegree() == 2
    assert near(c.Alpha(), 0.0, CONF)
    assert near(c.Beta(), 0.0, CONF)


def test_GeomEval_AHTBezierCurveTest_ParameterRange():
    c = create_full_basis_curve()
    assert near(c.FirstParameter(), 0.0, CONF)
    assert near(c.LastParameter(), 1.0, CONF)


def test_GeomEval_AHTBezierCurveTest_EvalD0_Endpoints():
    c = create_full_basis_curve()
    assert near(c.EvalD0(c.FirstParameter()).Distance(c.StartPoint()), 0.0, CONF)
    assert near(c.EvalD0(c.LastParameter()).Distance(c.EndPoint()), 0.0, CONF)


def test_GeomEval_AHTBezierCurveTest_EvalD1_ConsistentWithD0():
    c = create_full_basis_curve()
    u = 0.4
    vnear(c.EvalD1(u).D1, fd(c.EvalD0(u + CONF), c.EvalD0(u - CONF)), THE_FD_TOL_D1)


def test_GeomEval_AHTBezierCurveTest_Periodicity():
    assert create_full_basis_curve().IsPeriodic() is False


def test_GeomEval_AHTBezierCurveTest_Reverse_NotImplemented():
    c = create_full_basis_curve()
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def test_GeomEval_AHTBezierCurveTest_Construction_Rational():
    pp = poles((0, 0, 0), (1, 1, 0), (2, 0, 0))
    w = NCollection_Array1[float](1, 3)
    w[1], w[2], w[3] = 1.0, 2.0, 1.0
    c = GeomEval_AHTBezierCurve(pp, w, 2, 0.0, 0.0)
    assert c.IsRational() is True


def test_GeomEval_AHTBezierCurveTest_Transform_NotImplemented():
    c = create_full_basis_curve()
    tr = gp_Trsf()
    tr.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(tr)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(tr)


def test_GeomEval_AHTBezierCurveTest_Copy_Independent():
    cp = create_full_basis_curve().Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_AHTBezierCurve)
    assert cp.NbPoles() == 6
    assert cp.AlgDegree() == 1


def test_GeomEval_AHTBezierCurveTest_DumpJson_NoCrash():
    assert isinstance(create_full_basis_curve().DumpJson(), str)


def test_GeomEval_AHTBezierCurveTest_EvalD2_ConsistentWithD1():
    c = create_full_basis_curve()
    u = 0.3
    vnear(c.EvalD2(u).D2, fd(c.EvalD1(u + CONF).D1, c.EvalD1(u - CONF).D1), THE_FD_TOL_D2)


def test_GeomEval_AHTBezierCurveTest_EvalD3_ConsistentWithD2():
    c = create_full_basis_curve()
    u = 0.4
    vnear(c.EvalD3(u).D3, fd(c.EvalD2(u + CONF).D2, c.EvalD2(u - CONF).D2), THE_FD_TOL_D2)


def test_GeomEval_AHTBezierCurveTest_EvalDN_ConsistentWithD1():
    c = create_full_basis_curve()
    vnear(c.EvalD1(0.5).D1, c.EvalDN(0.5, 1), CONF)


def test_GeomEval_AHTBezierCurveTest_EvalD0_PurePolynomial_KnownValues():
    p0, p1, p2 = gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.5, 1.0, 0.0), gp_Pnt(1.0, 0.0, 0.0)
    arr = NCollection_Array1[gp_Pnt](1, 3)
    arr[1], arr[2], arr[3] = p0, p1, p2
    c = GeomEval_AHTBezierCurve(arr, 2, 0.0, 0.0)
    assert near(c.EvalD0(0.0).Distance(p0), 0.0, CONF)
    e05 = gp_Pnt(*(a + 0.5 * b + 0.25 * d for a, b, d in zip(p0.Coord__float__float__float(), p1.Coord__float__float__float(), p2.Coord__float__float__float())))
    assert near(c.EvalD0(0.5).Distance(e05), 0.0, CONF)
    e1 = gp_Pnt(*(a + b + d for a, b, d in zip(p0.Coord__float__float__float(), p1.Coord__float__float__float(), p2.Coord__float__float__float())))
    assert near(c.EvalD0(1.0).Distance(e1), 0.0, CONF)


def test_GeomEval_AHTBezierCurveTest_EvalD0_MatchesCircle():
    aht = create_trig_circle_arc()
    circ = Geom_Circle(gp_Ax2(), 1.0)
    for u in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
        assert near(aht.EvalD0(u).Distance(circ.EvalD0(u)), 0.0, ANG), u


def test_GeomEval_AHTBezierCurveTest_EvalD3_MatchesCircle():
    aht = create_trig_circle_arc()
    circ = Geom_Circle(gp_Ax2(), 1.0)
    for u in [0.1, 0.25, 0.5, 0.75, 0.9]:
        dt, dc = aht.EvalD3(u), circ.EvalD3(u)
        assert near(dt.Point.Distance(dc.Point), 0.0, ANG)
        vnear(dt.D1, dc.D1, ANG)
        vnear(dt.D2, dc.D2, ANG)
        vnear(dt.D3, dc.D3, ANG)


def test_GeomEval_AHTBezierCurveTest_EvalD2_MatchesEllipse():
    aht = create_trig_ellipse_arc()
    el = Geom_Ellipse(gp_Ax2(), 3.0, 2.0)
    for u in [0.1, 0.25, 0.5, 0.75, 0.9]:
        dt, dc = aht.EvalD2(u), el.EvalD2(u)
        assert near(dt.Point.Distance(dc.Point), 0.0, ANG)
        vnear(dt.D1, dc.D1, ANG)
        vnear(dt.D2, dc.D2, ANG)
