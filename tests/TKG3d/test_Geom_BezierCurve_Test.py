# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_BezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BezierCurve
from nanocct.GeomAbs import GeomAbs_Shape
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_Failure
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec


def _poles(*pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        a[i] = gp_Pnt(*p)
    return a


def _weights(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a[i] = w
    return a


@pytest.fixture
def curve():
    return Geom_BezierCurve(_poles((0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)))


def _quad_rational(w2, w3=1.0):
    return Geom_BezierCurve(_poles((0, 0, 0), (1, 1, 0), (2, 0, 0)), _weights(1.0, w2, w3))


def _arc():
    return Geom_BezierCurve(_poles((1, 0, 0), (1, 1, 0), (0, 1, 0)), _weights(1.0, 1.0 / math.sqrt(2.0), 1.0))


def test_Geom_BezierCurve_Test_CopyConstructorBasicProperties(curve):
    cp = Geom_BezierCurve(curve)
    assert curve.Degree() == cp.Degree()
    assert curve.NbPoles() == cp.NbPoles()
    assert curve.IsRational() == cp.IsRational()
    assert curve.IsClosed() == cp.IsClosed()


def test_Geom_BezierCurve_Test_CopyConstructorPoles(curve):
    cp = Geom_BezierCurve(curve)
    for i in range(1, curve.NbPoles() + 1):
        assert curve.Pole(i).IsEqual(cp.Pole(i), 1e-10)


def test_Geom_BezierCurve_Test_CopyMethodUsesOptimizedConstructor(curve):
    cp = curve.Copy()
    assert isinstance(cp, Geom_BezierCurve)
    assert curve.Degree() == cp.Degree()
    assert curve.NbPoles() == cp.NbPoles()
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert curve.Value(u).IsEqual(cp.Value(u), 1e-10)


def test_Geom_BezierCurve_Test_RationalCurveCopyConstructor():
    rc = _quad_rational(2.0)
    cp = Geom_BezierCurve(rc)
    assert cp.IsRational()
    for i in range(1, rc.NbPoles() + 1):
        assert rc.Weight(i) == pytest.approx(cp.Weight(i))


def test_Geom_BezierCurve_Test_CopyIndependence(curve):
    cp = Geom_BezierCurve(curve)
    new_pole = gp_Pnt(10, 10, 10)
    curve.SetPole(2, new_pole)
    assert not cp.Pole(2).IsEqual(new_pole, 1e-10)


def test_Geom_BezierCurve_Test_Evaluation_D0(curve):
    p = gp_Pnt()
    curve.D0(0.0, p)
    assert p.IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    curve.D0(1.0, p)
    assert p.IsEqual(gp_Pnt(3, 0, 0), 1e-10)


def test_Geom_BezierCurve_Test_Evaluation_D1(curve):
    p, v1 = gp_Pnt(), gp_Vec()
    curve.D1(0.5, p, v1)
    assert v1.Magnitude() > 0.0


def test_Geom_BezierCurve_Test_Evaluation_D2(curve):
    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    curve.D2(0.5, p, v1, v2)
    assert v1.Magnitude() > 0.0


def test_Geom_BezierCurve_Test_Evaluation_D3(curve):
    p, v1, v2, v3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    curve.D3(0.5, p, v1, v2, v3)
    pb, v1b, v2b, v3b = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    curve.D3(0.25, pb, v1b, v2b, v3b)
    assert abs(v3.X() - v3b.X()) <= 1e-8
    assert abs(v3.Y() - v3b.Y()) <= 1e-8


def test_Geom_BezierCurve_Test_Evaluation_DN(curve):
    assert curve.DN(0.5, 1).Magnitude() > 0.0
    assert abs(curve.DN(0.5, 4).Magnitude()) <= 1e-10


def test_Geom_BezierCurve_Test_StartEndPoints(curve):
    assert curve.StartPoint().IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    assert curve.EndPoint().IsEqual(gp_Pnt(3, 0, 0), 1e-10)


def test_Geom_BezierCurve_Test_Properties(curve):
    assert curve.Degree() == 3
    assert not curve.IsPeriodic()
    assert not curve.IsRational()
    assert not curve.IsClosed()
    assert curve.IsCN(100)
    assert curve.Continuity() == GeomAbs_Shape.GeomAbs_CN
    assert curve.FirstParameter() == pytest.approx(0.0)
    assert curve.LastParameter() == pytest.approx(1.0)


def test_Geom_BezierCurve_Test_SetPole(curve):
    new_pole = gp_Pnt(1, 5, 0)
    curve.SetPole(2, new_pole)
    assert curve.Pole(2).IsEqual(new_pole, 1e-10)
    assert curve.StartPoint().IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    assert curve.EndPoint().IsEqual(gp_Pnt(3, 0, 0), 1e-10)


def test_Geom_BezierCurve_Test_SetWeight():
    c = _quad_rational(1.0)
    mid_before = c.Value(0.5)
    c.SetWeight(2, 10.0)
    assert c.Weight(2) == pytest.approx(10.0)
    assert c.IsRational()
    assert c.Value(0.5).Y() > mid_before.Y()


def test_Geom_BezierCurve_Test_InsertPoleAfter(curve):
    nb = curve.NbPoles()
    new_pole = gp_Pnt(1.5, 2.0, 0)
    curve.InsertPoleAfter(2, new_pole)
    assert curve.NbPoles() == nb + 1
    assert curve.Degree() == 4
    assert curve.Pole(3).IsEqual(new_pole, 1e-10)


def test_Geom_BezierCurve_Test_InsertPoleBefore(curve):
    nb = curve.NbPoles()
    new_pole = gp_Pnt(0.5, 2.0, 0)
    curve.InsertPoleBefore(2, new_pole)
    assert curve.NbPoles() == nb + 1
    assert curve.Pole(2).IsEqual(new_pole, 1e-10)


def test_Geom_BezierCurve_Test_RemovePole(curve):
    curve.InsertPoleAfter(2, gp_Pnt(1.5, 2, 0))
    assert curve.NbPoles() == 5
    curve.RemovePole(3)
    assert curve.NbPoles() == 4
    assert curve.Degree() == 3


def test_Geom_BezierCurve_Test_Increase(curve):
    before = curve.Value(0.5)
    curve.Increase(5)
    assert curve.Degree() == 5
    assert curve.NbPoles() == 6
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom_BezierCurve_Test_Segment(curve):
    p25 = curve.Value(0.25)
    p75 = curve.Value(0.75)
    curve.Segment(0.25, 0.75)
    assert curve.StartPoint().IsEqual(p25, 1e-6)
    assert curve.EndPoint().IsEqual(p75, 1e-6)


def test_Geom_BezierCurve_Test_Reverse(curve):
    start = curve.StartPoint()
    end = curve.EndPoint()
    curve.Reverse()
    assert curve.StartPoint().IsEqual(end, 1e-10)
    assert curve.EndPoint().IsEqual(start, 1e-10)


def test_Geom_BezierCurve_Test_Resolution(curve):
    utol = curve.Resolution(1.0)
    assert utol > 0.0


def test_Geom_BezierCurve_Test_Transform(curve):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(10, 20, 30))
    before = curve.Value(0.5)
    curve.Transform(t)
    after = curve.Value(0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10
    assert abs(after.Z() - (before.Z() + 30.0)) <= 1e-10


def test_Geom_BezierCurve_Test_PolesAccess(curve):
    poles = curve.Poles()
    assert poles.Length() == 4
    assert poles[1].IsEqual(gp_Pnt(0, 0, 0), 1e-10)


def test_Geom_BezierCurve_Test_WeightsAccess_NonRational(curve):
    assert curve.Weights() is None


def test_Geom_BezierCurve_Test_RationalCurveEvaluation():
    c = _arc()
    assert c.IsRational()
    mid = c.Value(0.5)
    assert abs(math.hypot(mid.X(), mid.Y()) - 1.0) <= 1e-6


def test_Geom_BezierCurve_Test_MaxDegree():
    assert Geom_BezierCurve.MaxDegree_s() >= 25


def test_Geom_BezierCurve_Test_SetPoleWithWeight():
    c = _quad_rational(1.0)
    new_pole = gp_Pnt(1, 2, 0)
    c.SetPole(2, new_pole, 5.0)
    assert c.Pole(2).IsEqual(new_pole, 1e-10)
    assert c.Weight(2) == pytest.approx(5.0)
    assert c.IsRational()


def test_Geom_BezierCurve_Test_InsertPoleAfterWithWeight():
    c = _quad_rational(2.0)
    c.InsertPoleAfter(2, gp_Pnt(1.5, 0.5, 0), 3.0)
    assert c.NbPoles() == 4
    assert c.Weight(3) == pytest.approx(3.0)
    assert c.IsRational()


def test_Geom_BezierCurve_Test_ClosedCurve():
    c = Geom_BezierCurve(_poles((0, 0, 0), (1, 1, 0), (2, 0, 0), (0, 0, 0)))
    assert c.IsClosed()


def test_Geom_BezierCurve_Test_RationalSegment():
    c = _arc()
    mid = c.Value(0.5)
    c.Segment(0.25, 0.75)
    assert mid.IsEqual(c.Value(0.5), 1e-6)
    assert c.IsRational()


def test_Geom_BezierCurve_Test_RationalIncrease():
    c = _quad_rational(2.0)
    before = c.Value(0.5)
    c.Increase(5)
    assert c.Degree() == 5
    assert c.IsRational()
    assert before.IsEqual(c.Value(0.5), 1e-10)


def test_Geom_BezierCurve_Test_RationalReverse():
    c = _quad_rational(3.0, 2.0)
    start = c.StartPoint()
    end = c.EndPoint()
    c.Reverse()
    assert c.StartPoint().IsEqual(end, 1e-10)
    assert c.EndPoint().IsEqual(start, 1e-10)
    assert c.Weight(1) == pytest.approx(2.0)
    assert c.Weight(3) == pytest.approx(1.0)


def test_Geom_BezierCurve_Test_ReversedParameter(curve):
    assert curve.ReversedParameter(0.3) == pytest.approx(0.7)
    assert curve.ReversedParameter(0.0) == pytest.approx(1.0)


def test_Geom_BezierCurve_Test_LinearCurve():
    c = Geom_BezierCurve(_poles((0, 0, 0), (3, 4, 0)))
    assert c.Degree() == 1
    assert c.Value(0.5).IsEqual(gp_Pnt(1.5, 2.0, 0), 1e-10)
    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    c.D2(0.5, p, v1, v2)
    assert abs(v2.Magnitude()) <= 1e-10


def test_Geom_BezierCurve_Test_WeightsArray_NonRational_ReturnsUnitWeights(curve):
    # IsDeletable() and the address identity of the returned reference are C++ reference semantics:
    # the binding returns a copy, so only the values are checked.
    assert not curve.IsRational()
    w = curve.WeightsArray()
    assert w.Length() == curve.NbPoles()
    for i in range(1, w.Length() + 1):
        assert w[i] == pytest.approx(1.0)


def test_Geom_BezierCurve_Test_WeightsArray_Rational_ReturnsOwning():
    c = _quad_rational(2.0)
    assert c.IsRational()
    w = c.WeightsArray()
    assert w.Length() == 3
    assert w.IsDeletable()
    assert w[1] == pytest.approx(1.0)
    assert w[2] == pytest.approx(2.0)
    assert w[3] == pytest.approx(1.0)


def test_Geom_BezierCurveTest_OCC2569_DegreeEqualsNbPolesMinusOne():
    n = 26
    a = NCollection_Array1[gp_Pnt](1, n)
    for i in range(1, n + 1):
        a.SetValue(i, gp_Pnt(i + 10, i * 2 + 20, i * 3 + 45))
    c = Geom_BezierCurve(a)
    assert c.Degree() == n - 1


def test_Geom_BezierCurveTest_OCC2569_ThrowsForTooManyPoles():
    n = 29
    a = NCollection_Array1[gp_Pnt](1, n)
    for i in range(1, n + 1):
        a.SetValue(i, gp_Pnt(i + 10, i * 2 + 20, i * 3 + 45))
    with pytest.raises(Standard_Failure):
        Geom_BezierCurve(a)
