# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_BSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: the IsDeletable() and address-identity checks of the two WeightsArray tests (C++ ownership;
# a const& result is a copy in Python).
import math

import pytest

from nanocct.Geom2d import Geom2d_BSplineCurve
from nanocct.gp import gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1


def poles(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a[i] = gp_Pnt2d(x, y)
    return a


def reals(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a[i] = w
    return a


def ints(*ms):
    a = NCollection_Array1[int](1, len(ms))
    for i, m in enumerate(ms, 1):
        a[i] = m
    return a


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def curve():
    return Geom2d_BSplineCurve(poles((0, 0), (1, 1), (2, 1), (3, 0)), reals(0.0, 1.0), ints(4, 4), 3)


def rational_quadratic(w2):
    return Geom2d_BSplineCurve(poles((0, 0), (1, 1), (2, 0)), reals(1.0, w2, 1.0), reals(0.0, 1.0), ints(3, 3), 2)


def test_Geom2d_BSplineCurve_Test_CopyConstructorBasicProperties(curve):
    c = Geom2d_BSplineCurve(curve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    assert curve.NbKnots() == c.NbKnots()
    assert curve.IsPeriodic() == c.IsPeriodic()
    assert curve.IsRational() == c.IsRational()


def test_Geom2d_BSplineCurve_Test_CopyConstructorPoles(curve):
    c = Geom2d_BSplineCurve(curve)
    for i in range(1, curve.NbPoles() + 1):
        assert curve.Pole(i).IsEqual(c.Pole(i), 1e-10)


def test_Geom2d_BSplineCurve_Test_CopyConstructorKnots(curve):
    c = Geom2d_BSplineCurve(curve)
    for i in range(1, curve.NbKnots() + 1):
        deq(curve.Knot(i), c.Knot(i))
        assert curve.Multiplicity(i) == c.Multiplicity(i)


def test_Geom2d_BSplineCurve_Test_CopyMethodUsesOptimizedConstructor(curve):
    c = curve.Copy()
    assert isinstance(c, Geom2d_BSplineCurve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert curve.Value(u).IsEqual(c.Value(u), 1e-10)


def test_Geom2d_BSplineCurve_Test_RationalCurveCopyConstructor():
    r = rational_quadratic(2.0)
    c = Geom2d_BSplineCurve(r)
    assert c.IsRational() is True
    for i in range(1, r.NbPoles() + 1):
        deq(r.Weight(i), c.Weight(i))


def test_Geom2d_BSplineCurve_Test_Evaluation_D0(curve):
    p = gp_Pnt2d()
    curve.D0(0.0, p)
    assert p.IsEqual(gp_Pnt2d(0, 0), 1e-10)
    curve.D0(1.0, p)
    assert p.IsEqual(gp_Pnt2d(3, 0), 1e-10)


def test_Geom2d_BSplineCurve_Test_Evaluation_D1(curve):
    p, v1 = gp_Pnt2d(), gp_Vec2d()
    curve.D1(0.5, p, v1)
    assert v1.Magnitude() > 0.0


def test_Geom2d_BSplineCurve_Test_Evaluation_D2(curve):
    p, v1, v2 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
    curve.D2(0.5, p, v1, v2)
    assert v1.Magnitude() > 0.0


def test_Geom2d_BSplineCurve_Test_Evaluation_DN(curve):
    assert curve.DN(0.5, 1).Magnitude() > 0.0
    assert abs(curve.DN(0.5, 4).Magnitude()) <= 1e-10


def test_Geom2d_BSplineCurve_Test_StartEndPoints(curve):
    assert curve.StartPoint().IsEqual(gp_Pnt2d(0, 0), 1e-10)
    assert curve.EndPoint().IsEqual(gp_Pnt2d(3, 0), 1e-10)


def test_Geom2d_BSplineCurve_Test_Properties(curve):
    assert curve.Degree() == 3
    assert curve.IsPeriodic() is False
    assert curve.IsRational() is False
    assert curve.IsClosed() is False
    assert curve.IsCN(3) is True


def test_Geom2d_BSplineCurve_Test_SetPole(curve):
    newp = gp_Pnt2d(1, 5)
    curve.SetPole(2, newp)
    assert curve.Pole(2).IsEqual(newp, 1e-10)


def test_Geom2d_BSplineCurve_Test_IncreaseDegree(curve):
    before = curve.Value(0.5)
    curve.IncreaseDegree(5)
    assert curve.Degree() == 5
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom2d_BSplineCurve_Test_InsertKnot(curve):
    before = curve.Value(0.5)
    curve.InsertKnot(0.5)
    assert curve.NbKnots() == 3
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom2d_BSplineCurve_Test_RemoveKnot(curve):
    curve.InsertKnot(0.5)
    assert curve.NbKnots() == 3
    assert curve.RemoveKnot(2, 0, 1e-6) is True
    assert curve.NbKnots() == 2


def test_Geom2d_BSplineCurve_Test_Segment(curve):
    p25, p75 = curve.Value(0.25), curve.Value(0.75)
    curve.Segment(0.25, 0.75)
    assert abs(curve.FirstParameter() - 0.25) <= 1e-10
    assert abs(curve.LastParameter() - 0.75) <= 1e-10
    assert curve.StartPoint().IsEqual(p25, 1e-6)
    assert curve.EndPoint().IsEqual(p75, 1e-6)


def test_Geom2d_BSplineCurve_Test_Reverse(curve):
    s, e = curve.StartPoint(), curve.EndPoint()
    curve.Reverse()
    assert curve.StartPoint().IsEqual(e, 1e-10)
    assert curve.EndPoint().IsEqual(s, 1e-10)


def test_Geom2d_BSplineCurve_Test_Resolution(curve):
    assert curve.Resolution(1.0) > 0.0


def test_Geom2d_BSplineCurve_Test_Transform(curve):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10, 20))
    before = curve.Value(0.5)
    curve.Transform(t)
    after = curve.Value(0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10


def test_Geom2d_BSplineCurve_Test_PeriodicCurve():
    p = poles((1, 0), (0.309, 0.951), (-0.809, 0.588), (-0.809, -0.588), (0.309, -0.951))
    k = reals(*[(i - 1) * 0.2 for i in range(1, 7)])
    m = NCollection_Array1[int](1, 6)
    m.Init(1)
    c = Geom2d_BSplineCurve(p, k, m, 3, True)
    assert c.IsPeriodic() is True
    v1 = c.Value(0.5)
    c.SetNotPeriodic()
    assert c.IsPeriodic() is False
    assert v1.IsEqual(c.Value(0.5), 1e-10)


def test_Geom2d_BSplineCurve_Test_WeightsAccess_NonRational(curve):
    assert curve.Weights() is None


def test_Geom2d_BSplineCurve_Test_KnotAccess(curve):
    deq(curve.Knot(1), 0.0)
    deq(curve.Knot(2), 1.0)
    assert curve.Knots().Length() == 2
    m = curve.Multiplicities()
    assert m.Length() == 2
    assert m[1] == 4


def test_Geom2d_BSplineCurve_Test_CopyIndependence(curve):
    c = Geom2d_BSplineCurve(curve)
    curve.SetPole(2, gp_Pnt2d(10, 10))
    assert c.Pole(2).IsEqual(gp_Pnt2d(10, 10), 1e-10) is False


def test_Geom2d_BSplineCurve_Test_SetWeight():
    c = rational_quadratic(1.0)
    before = c.Value(0.5)
    c.SetWeight(2, 5.0)
    deq(c.Weight(2), 5.0)
    assert c.IsRational() is True
    assert c.Value(0.5).Y() > before.Y()


def test_Geom2d_BSplineCurve_Test_MovePoint(curve):
    target = gp_Pnt2d(1.5, 0.8)
    first, last = curve.MovePoint(0.5, target, 1, curve.NbPoles())
    assert first > 0
    assert curve.Value(0.5).IsEqual(target, 1e-6)


def test_Geom2d_BSplineCurve_Test_LocateU(curve):
    curve.InsertKnot(0.5)
    i1, i2 = curve.LocateU(0.25, 1e-10)
    assert i1 >= 1
    assert i2 <= curve.NbKnots()


def test_Geom2d_BSplineCurve_Test_LocalD1(curve):
    curve.InsertKnot(0.5)
    p, pl, v1, v1l = gp_Pnt2d(), gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
    curve.D1(0.25, p, v1)
    curve.LocalD1(0.25, 1, 2, pl, v1l)
    assert p.IsEqual(pl, 1e-10)
    assert abs(v1.X() - v1l.X()) <= 1e-10
    assert abs(v1.Y() - v1l.Y()) <= 1e-10


def test_Geom2d_BSplineCurve_Test_RationalCurveSegment():
    c = Geom2d_BSplineCurve(
        poles((1, 0), (1, 1), (0, 1)), reals(1.0, 1.0 / math.sqrt(2.0), 1.0), reals(0.0, 1.0), ints(3, 3), 2
    )
    mid = c.Value(0.5)
    c.Segment(0.25, 0.75)
    assert mid.IsEqual(c.Value(0.5), 1e-6)
    assert c.IsRational() is True


def test_Geom2d_BSplineCurve_Test_ClosedCurve():
    c = Geom2d_BSplineCurve(poles((0, 0), (1, 1), (2, 0), (0, 0)), reals(0.0, 1.0), ints(4, 4), 3)
    assert c.IsClosed() is True


def test_Geom2d_BSplineCurve_Test_InsertKnots_Multiple(curve):
    before = curve.Value(0.5)
    curve.InsertKnots(reals(0.25, 0.75), ints(1, 1))
    assert curve.NbKnots() == 4
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom2d_BSplineCurve_Test_WeightsArray_NonRational_ReturnsUnitWeights(curve):
    assert curve.IsRational() is False
    w = curve.WeightsArray()
    assert w.Length() == curve.NbPoles()
    for i in range(1, w.Length() + 1):
        deq(w[i], 1.0)


def test_Geom2d_BSplineCurve_Test_WeightsArray_Rational_ReturnsOwning():
    r = Geom2d_BSplineCurve(
        poles((0, 0), (1, 1), (2, 1), (3, 0)), reals(1.0, 2.0, 3.0, 1.0), reals(0.0, 1.0), ints(4, 4), 3
    )
    assert r.IsRational() is True
    w = r.WeightsArray()
    assert w.Length() == 4
    for i, e in enumerate((1.0, 2.0, 3.0, 1.0), 1):
        deq(w[i], e)
