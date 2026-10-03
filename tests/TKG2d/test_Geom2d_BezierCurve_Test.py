# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_BezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: the IsDeletable() and address-identity checks of the two WeightsArray tests (C++ ownership;
# a const& result is a copy in Python).
import math

import pytest

from nanocct.Geom2d import Geom2d_BezierCurve
from nanocct.gp import gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1


def poles(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a[i] = gp_Pnt2d(x, y)
    return a


def weights(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a[i] = w
    return a


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def curve():
    return Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 1), (3, 0)))


def test_Geom2d_BezierCurve_Test_CopyConstructorBasicProperties(curve):
    c = Geom2d_BezierCurve(curve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    assert curve.IsRational() == c.IsRational()
    assert curve.IsClosed() == c.IsClosed()


def test_Geom2d_BezierCurve_Test_CopyConstructorPoles(curve):
    c = Geom2d_BezierCurve(curve)
    for i in range(1, curve.NbPoles() + 1):
        assert curve.Pole(i).IsEqual(c.Pole(i), 1e-10)


def test_Geom2d_BezierCurve_Test_CopyMethodUsesOptimizedConstructor(curve):
    c = curve.Copy()
    assert isinstance(c, Geom2d_BezierCurve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert curve.Value(u).IsEqual(c.Value(u), 1e-10)


def test_Geom2d_BezierCurve_Test_RationalCurveCopyConstructor():
    r = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 2.0, 1.0))
    c = Geom2d_BezierCurve(r)
    assert c.IsRational() is True
    for i in range(1, r.NbPoles() + 1):
        deq(r.Weight(i), c.Weight(i))


def test_Geom2d_BezierCurve_Test_CopyIndependence(curve):
    c = Geom2d_BezierCurve(curve)
    newp = gp_Pnt2d(10, 10)
    curve.SetPole(2, newp)
    assert c.Pole(2).IsEqual(newp, 1e-10) is False


def test_Geom2d_BezierCurve_Test_Evaluation_D0(curve):
    p = gp_Pnt2d()
    curve.D0(0.0, p)
    assert p.IsEqual(gp_Pnt2d(0, 0), 1e-10)
    curve.D0(1.0, p)
    assert p.IsEqual(gp_Pnt2d(3, 0), 1e-10)


def test_Geom2d_BezierCurve_Test_Evaluation_D1(curve):
    p, v1 = gp_Pnt2d(), gp_Vec2d()
    curve.D1(0.5, p, v1)
    assert v1.Magnitude() > 0.0


def test_Geom2d_BezierCurve_Test_Evaluation_D2(curve):
    p, v1, v2 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
    curve.D2(0.5, p, v1, v2)
    assert v1.Magnitude() > 0.0


def test_Geom2d_BezierCurve_Test_Evaluation_DN(curve):
    assert curve.DN(0.5, 1).Magnitude() > 0.0
    assert abs(curve.DN(0.5, 4).Magnitude()) <= 1e-10


def test_Geom2d_BezierCurve_Test_StartEndPoints(curve):
    assert curve.StartPoint().IsEqual(gp_Pnt2d(0, 0), 1e-10)
    assert curve.EndPoint().IsEqual(gp_Pnt2d(3, 0), 1e-10)


def test_Geom2d_BezierCurve_Test_Properties(curve):
    assert curve.Degree() == 3
    assert curve.IsPeriodic() is False
    assert curve.IsRational() is False
    assert curve.IsClosed() is False
    assert curve.IsCN(100) is True
    deq(curve.FirstParameter(), 0.0)
    deq(curve.LastParameter(), 1.0)


def test_Geom2d_BezierCurve_Test_SetPole(curve):
    newp = gp_Pnt2d(1, 5)
    curve.SetPole(2, newp)
    assert curve.Pole(2).IsEqual(newp, 1e-10)
    assert curve.StartPoint().IsEqual(gp_Pnt2d(0, 0), 1e-10)


def test_Geom2d_BezierCurve_Test_SetWeight():
    c = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 1.0, 1.0))
    before = c.Value(0.5)
    c.SetWeight(2, 10.0)
    deq(c.Weight(2), 10.0)
    assert c.IsRational() is True
    assert c.Value(0.5).Y() > before.Y()


def test_Geom2d_BezierCurve_Test_InsertPoleAfter(curve):
    n = curve.NbPoles()
    curve.InsertPoleAfter(2, gp_Pnt2d(1.5, 2))
    assert curve.NbPoles() == n + 1
    assert curve.Degree() == 4


def test_Geom2d_BezierCurve_Test_RemovePole(curve):
    curve.InsertPoleAfter(2, gp_Pnt2d(1.5, 2))
    assert curve.NbPoles() == 5
    curve.RemovePole(3)
    assert curve.NbPoles() == 4


def test_Geom2d_BezierCurve_Test_Increase(curve):
    before = curve.Value(0.5)
    curve.Increase(5)
    assert curve.Degree() == 5
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom2d_BezierCurve_Test_Segment(curve):
    p25, p75 = curve.Value(0.25), curve.Value(0.75)
    curve.Segment(0.25, 0.75)
    assert curve.StartPoint().IsEqual(p25, 1e-6)
    assert curve.EndPoint().IsEqual(p75, 1e-6)


def test_Geom2d_BezierCurve_Test_Reverse(curve):
    s, e = curve.StartPoint(), curve.EndPoint()
    curve.Reverse()
    assert curve.StartPoint().IsEqual(e, 1e-10)
    assert curve.EndPoint().IsEqual(s, 1e-10)


def test_Geom2d_BezierCurve_Test_Resolution(curve):
    assert curve.Resolution(1.0) > 0.0


def test_Geom2d_BezierCurve_Test_Transform(curve):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10, 20))
    before = curve.Value(0.5)
    curve.Transform(t)
    after = curve.Value(0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10


def test_Geom2d_BezierCurve_Test_PolesAccess(curve):
    p = curve.Poles()
    assert p.Length() == 4
    assert p[1].IsEqual(gp_Pnt2d(0, 0), 1e-10)


def test_Geom2d_BezierCurve_Test_WeightsAccess_NonRational(curve):
    assert curve.Weights() is None


def test_Geom2d_BezierCurve_Test_MaxDegree():
    assert Geom2d_BezierCurve.MaxDegree_s() >= 25


def test_Geom2d_BezierCurve_Test_RationalCurveEvaluation():
    c = Geom2d_BezierCurve(poles((1, 0), (1, 1), (0, 1)), weights(1.0, 1.0 / math.sqrt(2.0), 1.0))
    assert c.IsRational() is True
    m = c.Value(0.5)
    assert abs(math.hypot(m.X(), m.Y()) - 1.0) <= 1e-6


def test_Geom2d_BezierCurve_Test_SetPoleWithWeight():
    c = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 1.0, 1.0))
    c.SetPole(2, gp_Pnt2d(1, 2), 5.0)
    assert c.Pole(2).IsEqual(gp_Pnt2d(1, 2), 1e-10)
    deq(c.Weight(2), 5.0)
    assert c.IsRational() is True


def test_Geom2d_BezierCurve_Test_InsertPoleBeforeWithWeight():
    c = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 2.0, 1.0))
    c.InsertPoleBefore(2, gp_Pnt2d(0.5, 0.5), 3.0)
    assert c.NbPoles() == 4
    deq(c.Weight(2), 3.0)


def test_Geom2d_BezierCurve_Test_ClosedCurve():
    assert Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0), (0, 0))).IsClosed() is True


def test_Geom2d_BezierCurve_Test_RationalSegment():
    c = Geom2d_BezierCurve(poles((1, 0), (1, 1), (0, 1)), weights(1.0, 1.0 / math.sqrt(2.0), 1.0))
    mid = c.Value(0.5)
    c.Segment(0.25, 0.75)
    assert mid.IsEqual(c.Value(0.5), 1e-6)
    assert c.IsRational() is True


def test_Geom2d_BezierCurve_Test_RationalReverse():
    c = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 3.0, 2.0))
    s, e = c.StartPoint(), c.EndPoint()
    c.Reverse()
    assert c.StartPoint().IsEqual(e, 1e-10)
    assert c.EndPoint().IsEqual(s, 1e-10)
    deq(c.Weight(1), 2.0)
    deq(c.Weight(3), 1.0)


def test_Geom2d_BezierCurve_Test_Evaluation_D3(curve):
    p, v1, v2, v3 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d(), gp_Vec2d()
    curve.D3(0.5, p, v1, v2, v3)
    pb, v1b, v2b, v3b = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d(), gp_Vec2d()
    curve.D3(0.25, pb, v1b, v2b, v3b)
    assert abs(v3.X() - v3b.X()) <= 1e-8
    assert abs(v3.Y() - v3b.Y()) <= 1e-8


def test_Geom2d_BezierCurve_Test_ReversedParameter(curve):
    deq(curve.ReversedParameter(0.3), 0.7)
    deq(curve.ReversedParameter(0.0), 1.0)


def test_Geom2d_BezierCurve_Test_LinearCurve():
    c = Geom2d_BezierCurve(poles((0, 0), (3, 4)))
    assert c.Degree() == 1
    assert c.Value(0.5).IsEqual(gp_Pnt2d(1.5, 2.0), 1e-10)


def test_Geom2d_BezierCurve_Test_RationalIncrease():
    c = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 2.0, 1.0))
    before = c.Value(0.5)
    c.Increase(5)
    assert c.Degree() == 5
    assert c.IsRational() is True
    assert before.IsEqual(c.Value(0.5), 1e-10)


def test_Geom2d_BezierCurve_Test_WeightsArray_NonRational_ReturnsUnitWeights(curve):
    assert curve.IsRational() is False
    w = curve.WeightsArray()
    assert w.Length() == curve.NbPoles()
    for i in range(1, w.Length() + 1):
        deq(w[i], 1.0)


def test_Geom2d_BezierCurve_Test_WeightsArray_Rational_ReturnsOwning():
    r = Geom2d_BezierCurve(poles((0, 0), (1, 1), (2, 0)), weights(1.0, 2.0, 1.0))
    assert r.IsRational() is True
    w = r.WeightsArray()
    assert w.Length() == 3
    deq(w[1], 1.0)
    deq(w[2], 2.0)
    deq(w[3], 1.0)
