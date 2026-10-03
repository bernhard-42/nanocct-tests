# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_BSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BSplineCurve
from nanocct.GeomAbs import GeomAbs_CN, GeomAbs_PiecewiseBezier
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1


def _pnts(*pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts):
        a[i + 1] = gp_Pnt(*p)
    return a


def _reals(*vals):
    a = NCollection_Array1[float](1, len(vals))
    for i, v in enumerate(vals):
        a[i + 1] = float(v)
    return a


def _ints(*vals):
    a = NCollection_Array1[int](1, len(vals))
    for i, v in enumerate(vals):
        a[i + 1] = v
    return a


@pytest.fixture
def curve():
    poles = _pnts((0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0))
    return Geom_BSplineCurve(poles, _reals(0.0, 1.0), _ints(4, 4), 3)


def _rational_parabola(w2):
    poles = _pnts((0, 0, 0), (1, 1, 0), (2, 0, 0))
    return Geom_BSplineCurve(poles, _reals(1.0, w2, 1.0), _reals(0.0, 1.0), _ints(3, 3), 2)


def _periodic():
    poles = _pnts((1, 0, 0), (0.309, 0.951, 0), (-0.809, 0.588, 0), (-0.809, -0.588, 0), (0.309, -0.951, 0))
    knots = _reals(*[(i - 1) * 0.2 for i in range(1, 7)])
    mults = NCollection_Array1[int](1, 6)
    mults.Init(1)
    return Geom_BSplineCurve(poles, knots, mults, 3, True)


def test_Geom_BSplineCurve_Test_CopyConstructorBasicProperties(curve):
    c = Geom_BSplineCurve(curve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    assert curve.NbKnots() == c.NbKnots()
    assert curve.IsPeriodic() == c.IsPeriodic()
    assert curve.IsRational() == c.IsRational()


def test_Geom_BSplineCurve_Test_CopyConstructorPoles(curve):
    c = Geom_BSplineCurve(curve)
    for i in range(1, curve.NbPoles() + 1):
        assert curve.Pole(i).IsEqual(c.Pole(i), 1e-10)


def test_Geom_BSplineCurve_Test_CopyConstructorKnots(curve):
    c = Geom_BSplineCurve(curve)
    for i in range(1, curve.NbKnots() + 1):
        assert curve.Knot(i) == pytest.approx(c.Knot(i))
        assert curve.Multiplicity(i) == c.Multiplicity(i)


def test_Geom_BSplineCurve_Test_CopyMethodUsesOptimizedConstructor(curve):
    c = curve.Copy()
    assert isinstance(c, Geom_BSplineCurve)
    assert curve.Degree() == c.Degree()
    assert curve.NbPoles() == c.NbPoles()
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert curve.Value(u).IsEqual(c.Value(u), 1e-10)


def test_Geom_BSplineCurve_Test_RationalCurveCopyConstructor():
    r = _rational_parabola(2.0)
    c = Geom_BSplineCurve(r)
    assert c.IsRational()
    for i in range(1, r.NbPoles() + 1):
        assert r.Weight(i) == pytest.approx(c.Weight(i))


def test_Geom_BSplineCurve_Test_Evaluation_D0(curve):
    p = gp_Pnt()
    curve.D0(0.0, p)
    assert p.IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    curve.D0(1.0, p)
    assert p.IsEqual(gp_Pnt(3, 0, 0), 1e-10)


def test_Geom_BSplineCurve_Test_Evaluation_D1(curve):
    p, v1 = gp_Pnt(), gp_Vec()
    curve.D1(0.5, p, v1)
    assert v1.Magnitude() > 0.0


def test_Geom_BSplineCurve_Test_Evaluation_D2(curve):
    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    curve.D2(0.5, p, v1, v2)
    assert v1.Magnitude() > 0.0


def test_Geom_BSplineCurve_Test_Evaluation_D3(curve):
    p, v1, v2, v3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    curve.D3(0.5, p, v1, v2, v3)
    pb, v1b, v2b, v3b = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    curve.D3(0.25, pb, v1b, v2b, v3b)
    assert abs(v3.X() - v3b.X()) <= 1e-8
    assert abs(v3.Y() - v3b.Y()) <= 1e-8
    assert abs(v3.Z() - v3b.Z()) <= 1e-8


def test_Geom_BSplineCurve_Test_Evaluation_DN(curve):
    assert curve.DN(0.5, 1).Magnitude() > 0.0
    assert abs(curve.DN(0.5, 4).Magnitude()) <= 1e-10


def test_Geom_BSplineCurve_Test_StartEndPoints(curve):
    assert curve.StartPoint().IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    assert curve.EndPoint().IsEqual(gp_Pnt(3, 0, 0), 1e-10)


def test_Geom_BSplineCurve_Test_SetPole(curve):
    newp = gp_Pnt(1, 2, 3)
    curve.SetPole(2, newp)
    assert curve.Pole(2).IsEqual(newp, 1e-10)
    assert curve.StartPoint().IsEqual(gp_Pnt(0, 0, 0), 1e-10)


def test_Geom_BSplineCurve_Test_SetWeight():
    c = _rational_parabola(1.0)
    before = c.Value(0.5)
    c.SetWeight(2, 5.0)
    assert c.Weight(2) == pytest.approx(5.0)
    assert c.IsRational()
    after = c.Value(0.5)
    assert not before.IsEqual(after, 1e-6)


def test_Geom_BSplineCurve_Test_IncreaseDegree(curve):
    before = curve.Value(0.5)
    curve.IncreaseDegree(5)
    assert curve.Degree() == 5
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_InsertKnot(curve):
    before = curve.Value(0.5)
    curve.InsertKnot(0.5)
    assert curve.NbKnots() == 3
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_RemoveKnot(curve):
    curve.InsertKnot(0.5)
    assert curve.NbKnots() == 3
    before = curve.Value(0.25)
    assert curve.RemoveKnot(2, 0, 1e-6)
    assert curve.NbKnots() == 2
    assert before.IsEqual(curve.Value(0.25), 1e-6)


def test_Geom_BSplineCurve_Test_Segment(curve):
    p25 = curve.Value(0.25)
    p75 = curve.Value(0.75)
    curve.Segment(0.25, 0.75)
    assert abs(curve.FirstParameter() - 0.25) <= 1e-10
    assert abs(curve.LastParameter() - 0.75) <= 1e-10
    assert curve.StartPoint().IsEqual(p25, 1e-6)
    assert curve.EndPoint().IsEqual(p75, 1e-6)


def test_Geom_BSplineCurve_Test_Reverse(curve):
    start = curve.StartPoint()
    end = curve.EndPoint()
    curve.Reverse()
    assert curve.StartPoint().IsEqual(end, 1e-10)
    assert curve.EndPoint().IsEqual(start, 1e-10)


def test_Geom_BSplineCurve_Test_Resolution(curve):
    utol = curve.Resolution(1.0)
    assert utol > 0.0


def test_Geom_BSplineCurve_Test_Properties(curve):
    assert curve.Degree() == 3
    assert not curve.IsPeriodic()
    assert not curve.IsRational()
    assert not curve.IsClosed()
    assert curve.IsCN(3)
    assert curve.Continuity() == GeomAbs_CN


def test_Geom_BSplineCurve_Test_Transform(curve):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(10, 20, 30))
    before = curve.Value(0.5)
    curve.Transform(trsf)
    after = curve.Value(0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10
    assert abs(after.Z() - (before.Z() + 30.0)) <= 1e-10


def test_Geom_BSplineCurve_Test_PeriodicCurve():
    c = _periodic()
    assert c.IsPeriodic()
    v1 = c.Value(0.5)
    c.SetNotPeriodic()
    assert not c.IsPeriodic()
    assert v1.IsEqual(c.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_MultiKnotSpan():
    poles = _pnts((0, 0, 0), (1, 2, 0), (2, 0, 0), (3, 2, 0), (4, 0, 0))
    c = Geom_BSplineCurve(poles, _reals(0, 1, 2, 3), _ints(3, 1, 1, 3), 2)
    assert c.NbKnots() == 4
    assert c.NbPoles() == 5
    p = gp_Pnt()
    c.D0(0.0, p)
    assert p.IsEqual(gp_Pnt(0, 0, 0), 1e-10)
    c.D0(3.0, p)
    assert p.IsEqual(gp_Pnt(4, 0, 0), 1e-10)


def test_Geom_BSplineCurve_Test_IncreaseMultiplicity(curve):
    curve.InsertKnot(0.5, 1)
    assert curve.NbKnots() == 3
    assert curve.Multiplicity(2) == 1
    before = curve.Value(0.5)
    curve.IncreaseMultiplicity(2, 2)
    assert curve.Multiplicity(2) == 2
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_KnotAccess(curve):
    assert curve.Knot(1) == pytest.approx(0.0)
    assert curve.Knot(2) == pytest.approx(1.0)
    assert curve.FirstUKnotIndex() == 1
    assert curve.LastUKnotIndex() == 2
    assert curve.Knots().Length() == 2
    assert curve.KnotSequence().Length() == 8
    mults = curve.Multiplicities()
    assert mults.Length() == 2
    assert mults[1] == 4
    assert mults[2] == 4


def test_Geom_BSplineCurve_Test_PolesAccess(curve):
    poles = curve.Poles()
    assert poles.Length() == 4
    assert poles[1].IsEqual(gp_Pnt(0, 0, 0), 1e-10)


def test_Geom_BSplineCurve_Test_WeightsAccess_NonRational(curve):
    assert curve.Weights() is None


def test_Geom_BSplineCurve_Test_WeightsAccess_Rational():
    c = _rational_parabola(2.0)
    w = c.Weights()
    assert w is not None
    assert w[2] == pytest.approx(2.0)


def test_Geom_BSplineCurve_Test_LocalEvaluation(curve):
    curve.InsertKnot(0.5)
    assert curve.NbKnots() == 3
    assert curve.Value(0.25).IsEqual(curve.LocalValue(0.25, 1, 2), 1e-10)


def test_Geom_BSplineCurve_Test_SetKnot():
    poles = _pnts((0, 0, 0), (1, 1, 0), (2, 0, 0), (3, 1, 0))
    c = Geom_BSplineCurve(poles, _reals(0.0, 0.5, 1.0), _ints(3, 1, 3), 2)
    c.SetKnot(2, 0.6)
    assert c.Knot(2) == pytest.approx(0.6)


def test_Geom_BSplineCurve_Test_CopyIndependence(curve):
    c = Geom_BSplineCurve(curve)
    curve.SetPole(2, gp_Pnt(10, 10, 10))
    assert not c.Pole(2).IsEqual(gp_Pnt(10, 10, 10), 1e-10)


def test_Geom_BSplineCurve_Test_MovePoint(curve):
    target = gp_Pnt(1.5, 0.8, 0)
    first, last = curve.MovePoint(0.5, target, 1, curve.NbPoles())
    assert first > 0
    assert curve.Value(0.5).IsEqual(target, 1e-6)


def test_Geom_BSplineCurve_Test_LocateU(curve):
    curve.InsertKnot(0.5)
    i1, i2 = curve.LocateU(0.25, 1e-10)
    assert i1 >= 1
    assert i2 <= curve.NbKnots()
    assert curve.Knot(i1) <= 0.25 + 1e-10
    assert curve.Knot(i2) >= 0.25 - 1e-10


def test_Geom_BSplineCurve_Test_IsEqual(curve):
    c = Geom_BSplineCurve(curve)
    assert curve.IsEqual(c, 1e-10)
    c.SetPole(2, gp_Pnt(10, 10, 10))
    assert not curve.IsEqual(c, 1e-10)


def test_Geom_BSplineCurve_Test_KnotDistribution(curve):
    assert curve.KnotDistribution() == GeomAbs_PiecewiseBezier


def test_Geom_BSplineCurve_Test_RationalCurveSegment():
    poles = _pnts((1, 0, 0), (1, 1, 0), (0, 1, 0))
    c = Geom_BSplineCurve(poles, _reals(1.0, 1.0 / math.sqrt(2.0), 1.0), _reals(0.0, 1.0), _ints(3, 3), 2)
    assert c.IsRational()
    mid = c.Value(0.5)
    c.Segment(0.25, 0.75)
    assert mid.IsEqual(c.Value(0.5), 1e-6)
    assert c.IsRational()


def test_Geom_BSplineCurve_Test_RationalCurveIncreaseDegree():
    c = _rational_parabola(2.0)
    before = c.Value(0.5)
    c.IncreaseDegree(4)
    assert c.Degree() == 4
    assert c.IsRational()
    assert before.IsEqual(c.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_PeriodicCurve_SetOrigin():
    c = _periodic()
    assert c.IsPeriodic()
    c.SetOrigin(3)
    assert c.IsPeriodic()
    v = c.Value(c.FirstParameter())
    assert v.X() * v.X() + v.Y() * v.Y() > 0.0


def test_Geom_BSplineCurve_Test_InsertKnots_Multiple(curve):
    before = curve.Value(0.5)
    curve.InsertKnots(_reals(0.25, 0.75), _ints(1, 1))
    assert curve.NbKnots() == 4
    assert before.IsEqual(curve.Value(0.5), 1e-10)


def test_Geom_BSplineCurve_Test_ClosedCurve():
    poles = _pnts((0, 0, 0), (1, 1, 0), (2, 0, 0), (0, 0, 0))
    c = Geom_BSplineCurve(poles, _reals(0.0, 1.0), _ints(4, 4), 3)
    assert c.IsClosed()


def test_Geom_BSplineCurve_Test_LocalD1(curve):
    curve.InsertKnot(0.5)
    p, v1, pl, v1l = gp_Pnt(), gp_Vec(), gp_Pnt(), gp_Vec()
    curve.D1(0.25, p, v1)
    curve.LocalD1(0.25, 1, 2, pl, v1l)
    assert p.IsEqual(pl, 1e-10)
    assert abs(v1.X() - v1l.X()) <= 1e-10
    assert abs(v1.Y() - v1l.Y()) <= 1e-10


def test_Geom_BSplineCurve_Test_WeightsArray_NonRational_ReturnsUnitWeights(curve):
    assert not curve.IsRational()
    w = curve.WeightsArray()
    assert w.Length() == curve.NbPoles()
    for i in range(1, w.Length() + 1):
        assert w[i] == pytest.approx(1.0)
    # IsDeletable() and the reference-identity check (&aWeights == &WeightsArray()) are C++ memory
    # semantics: nanocct copies const& results by design (Design.md 6), so the copy always owns its data.


def test_Geom_BSplineCurve_Test_WeightsArray_Rational_ReturnsOwning():
    poles = _pnts((0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0))
    c = Geom_BSplineCurve(poles, _reals(1.0, 2.0, 3.0, 1.0), _reals(0.0, 1.0), _ints(4, 4), 3)
    assert c.IsRational()
    w = c.WeightsArray()
    assert w.Length() == 4
    assert w[1] == pytest.approx(1.0)
    assert w[2] == pytest.approx(2.0)
    assert w[3] == pytest.approx(3.0)
    assert w[4] == pytest.approx(1.0)
