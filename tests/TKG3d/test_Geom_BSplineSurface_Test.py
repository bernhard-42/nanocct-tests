# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_BSplineSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BSplineSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2


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


def _pnts1(*pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts):
        a[i + 1] = gp_Pnt(*p)
    return a


def _poles(nu, nv, f):
    a = NCollection_Array2[gp_Pnt](1, nu, 1, nv)
    for i in range(1, nu + 1):
        for j in range(1, nv + 1):
            a[i, j] = gp_Pnt(*f(i, j))
    return a


def _weights(nu, nv, f):
    a = NCollection_Array2[float](1, nu, 1, nv)
    for i in range(1, nu + 1):
        for j in range(1, nv + 1):
            a[i, j] = float(f(i, j))
    return a


@pytest.fixture
def surf():
    poles = _poles(3, 3, lambda i, j: (i, j, (i + j) * 0.1))
    return Geom_BSplineSurface(poles, _reals(0, 1), _reals(0, 1), _ints(3, 3), _ints(3, 3), 2, 2)


def _rational_bump(center_weight):
    poles = _poles(3, 3, lambda i, j: (i, j, 1.0 if (i == 2 and j == 2) else 0.0))
    weights = _weights(3, 3, lambda i, j: center_weight if (i == 2 and j == 2) else 1.0)
    return Geom_BSplineSurface(poles, weights, _reals(0, 1), _reals(0, 1), _ints(3, 3), _ints(3, 3), 2, 2)


def _u_periodic_poles(i, j):
    return (math.cos(2.0 * math.pi * (i - 1) / 3.0), math.sin(2.0 * math.pi * (i - 1) / 3.0), j * 0.5)


def _v_periodic_poles(i, j):
    return (i * 0.5, math.cos(2.0 * math.pi * (j - 1) / 3.0), math.sin(2.0 * math.pi * (j - 1) / 3.0))


def _ones(n):
    a = NCollection_Array1[int](1, n)
    a.Init(1)
    return a


def test_Geom_BSplineSurface_Test_CopyConstructorBasicProperties(surf):
    c = Geom_BSplineSurface(surf)
    assert surf.UDegree() == c.UDegree()
    assert surf.VDegree() == c.VDegree()
    assert surf.NbUPoles() == c.NbUPoles()
    assert surf.NbVPoles() == c.NbVPoles()
    assert surf.NbUKnots() == c.NbUKnots()
    assert surf.NbVKnots() == c.NbVKnots()
    assert surf.IsUPeriodic() == c.IsUPeriodic()
    assert surf.IsVPeriodic() == c.IsVPeriodic()


def test_Geom_BSplineSurface_Test_CopyConstructorPoles(surf):
    c = Geom_BSplineSurface(surf)
    for i in range(1, surf.NbUPoles() + 1):
        for j in range(1, surf.NbVPoles() + 1):
            assert surf.Pole(i, j).IsEqual(c.Pole(i, j), 1e-10)


def test_Geom_BSplineSurface_Test_CopyConstructorKnots(surf):
    c = Geom_BSplineSurface(surf)
    for i in range(1, surf.NbUKnots() + 1):
        assert surf.UKnot(i) == pytest.approx(c.UKnot(i))
        assert surf.UMultiplicity(i) == c.UMultiplicity(i)
    for i in range(1, surf.NbVKnots() + 1):
        assert surf.VKnot(i) == pytest.approx(c.VKnot(i))
        assert surf.VMultiplicity(i) == c.VMultiplicity(i)


def test_Geom_BSplineSurface_Test_CopyMethodUsesOptimizedConstructor(surf):
    c = surf.Copy()
    assert isinstance(c, Geom_BSplineSurface)
    assert surf.UDegree() == c.UDegree()
    assert surf.VDegree() == c.VDegree()
    for u in (0.0, 0.5, 1.0):
        for v in (0.0, 0.5, 1.0):
            assert surf.Value(u, v).IsEqual(c.Value(u, v), 1e-10)


def test_Geom_BSplineSurface_Test_CopyIndependence(surf):
    c = Geom_BSplineSurface(surf)
    newp = gp_Pnt(10, 10, 10)
    surf.SetPole(2, 2, newp)
    assert not c.Pole(2, 2).IsEqual(newp, 1e-10)


def test_Geom_BSplineSurface_Test_Evaluation_D0(surf):
    p = gp_Pnt()
    surf.D0(0.0, 0.0, p)
    assert p.IsEqual(gp_Pnt(1, 1, 0.2), 1e-10)
    surf.D0(1.0, 1.0, p)
    assert p.IsEqual(gp_Pnt(3, 3, 0.6), 1e-10)


def test_Geom_BSplineSurface_Test_Evaluation_D1(surf):
    p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
    surf.D1(0.5, 0.5, p, d1u, d1v)
    assert d1u.Magnitude() > 0.0
    assert d1v.Magnitude() > 0.0


def test_Geom_BSplineSurface_Test_Evaluation_D2(surf):
    p = gp_Pnt()
    d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
    surf.D2(0.5, 0.5, p, d1u, d1v, d2u, d2v, d2uv)
    assert d1u.Magnitude() > 0.0


def test_Geom_BSplineSurface_Test_Evaluation_DN(surf):
    assert surf.DN(0.5, 0.5, 1, 0).Magnitude() > 0.0
    assert surf.DN(0.5, 0.5, 0, 1).Magnitude() > 0.0


def test_Geom_BSplineSurface_Test_Properties(surf):
    assert surf.UDegree() == 2
    assert surf.VDegree() == 2
    assert not surf.IsUPeriodic()
    assert not surf.IsVPeriodic()
    assert not surf.IsURational()
    assert not surf.IsVRational()
    assert surf.NbUPoles() == 3
    assert surf.NbVPoles() == 3
    assert surf.NbUKnots() == 2
    assert surf.NbVKnots() == 2


def test_Geom_BSplineSurface_Test_Bounds(surf):
    u1, u2, v1, v2 = surf.Bounds()
    assert u1 == pytest.approx(0.0)
    assert u2 == pytest.approx(1.0)
    assert v1 == pytest.approx(0.0)
    assert v2 == pytest.approx(1.0)


def test_Geom_BSplineSurface_Test_SetPole(surf):
    newp = gp_Pnt(5, 5, 5)
    surf.SetPole(2, 2, newp)
    assert surf.Pole(2, 2).IsEqual(newp, 1e-10)


def test_Geom_BSplineSurface_Test_SetWeight():
    s = _rational_bump(2.0)
    assert s.IsURational() or s.IsVRational()
    before = s.Value(0.5, 0.5)
    s.SetWeight(2, 2, 10.0)
    assert s.Weight(2, 2) == pytest.approx(10.0)
    after = s.Value(0.5, 0.5)
    assert after.Z() > before.Z()


def test_Geom_BSplineSurface_Test_IncreaseDegree(surf):
    before = surf.Value(0.5, 0.5)
    surf.IncreaseDegree(4, 3)
    assert surf.UDegree() == 4
    assert surf.VDegree() == 3
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_InsertUKnot(surf):
    before = surf.Value(0.5, 0.5)
    surf.InsertUKnot(0.5, 1, 0.0)
    assert surf.NbUKnots() == 3
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_InsertVKnot(surf):
    before = surf.Value(0.5, 0.5)
    surf.InsertVKnot(0.5, 1, 0.0)
    assert surf.NbVKnots() == 3
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_RemoveUKnot(surf):
    surf.InsertUKnot(0.5, 1, 0.0)
    assert surf.NbUKnots() == 3
    before = surf.Value(0.25, 0.5)
    assert surf.RemoveUKnot(2, 0, 1e-6)
    assert surf.NbUKnots() == 2
    assert before.IsEqual(surf.Value(0.25, 0.5), 1e-6)


def test_Geom_BSplineSurface_Test_Segment(surf):
    before = surf.Value(0.5, 0.5)
    surf.Segment(0.25, 0.75, 0.25, 0.75)
    u1, u2, v1, v2 = surf.Bounds()
    assert abs(u1 - 0.25) <= 1e-10
    assert abs(u2 - 0.75) <= 1e-10
    assert abs(v1 - 0.25) <= 1e-10
    assert abs(v2 - 0.75) <= 1e-10
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-6)


def test_Geom_BSplineSurface_Test_ExchangeUV(surf):
    before = surf.Value(0.3, 0.7)
    udeg = surf.UDegree()
    vdeg = surf.VDegree()
    surf.ExchangeUV()
    assert surf.UDegree() == vdeg
    assert surf.VDegree() == udeg
    assert before.IsEqual(surf.Value(0.7, 0.3), 1e-10)


def test_Geom_BSplineSurface_Test_UReverse(surf):
    before = surf.Value(0.3, 0.5)
    surf.UReverse()
    assert before.IsEqual(surf.Value(0.7, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_VReverse(surf):
    before = surf.Value(0.5, 0.3)
    surf.VReverse()
    assert before.IsEqual(surf.Value(0.5, 0.7), 1e-10)


def test_Geom_BSplineSurface_Test_UIso(surf):
    iso = surf.UIso(0.5)
    assert iso is not None
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert surf.Value(0.5, v).IsEqual(iso.Value(v), 1e-10)


def test_Geom_BSplineSurface_Test_VIso(surf):
    iso = surf.VIso(0.5)
    assert iso is not None
    for u in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert surf.Value(u, 0.5).IsEqual(iso.Value(u), 1e-10)


def test_Geom_BSplineSurface_Test_Resolution(surf):
    utol, vtol = surf.Resolution(1.0)
    assert utol > 0.0
    assert vtol > 0.0


def test_Geom_BSplineSurface_Test_Transform(surf):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(10, 20, 30))
    before = surf.Value(0.5, 0.5)
    surf.Transform(trsf)
    after = surf.Value(0.5, 0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10
    assert abs(after.Z() - (before.Z() + 30.0)) <= 1e-10


def test_Geom_BSplineSurface_Test_KnotsAccess(surf):
    uk = surf.UKnots()
    assert uk.Length() == 2
    assert uk[1] == pytest.approx(0.0)
    assert uk[2] == pytest.approx(1.0)
    assert surf.VKnots().Length() == 2
    um = surf.UMultiplicities()
    assert um.Length() == 2
    assert um[1] == 3
    assert surf.VMultiplicities().Length() == 2


def test_Geom_BSplineSurface_Test_WeightsAccess_NonRational(surf):
    assert surf.Weights() is None


def test_Geom_BSplineSurface_Test_PeriodicSurface_SetUNotPeriodic():
    poles = _poles(3, 3, _u_periodic_poles)
    s = Geom_BSplineSurface(poles, _reals(0, 1, 2, 3), _reals(0, 1), _ones(4), _ints(3, 3), 2, 2, True, False)
    assert s.IsUPeriodic()
    val = s.Value(0.5, 0.5)
    s.SetUNotPeriodic()
    assert not s.IsUPeriodic()
    assert val.IsEqual(s.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_PeriodicSurface_SetVNotPeriodic():
    poles = _poles(3, 3, _v_periodic_poles)
    s = Geom_BSplineSurface(poles, _reals(0, 1), _reals(0, 1, 2, 3), _ints(3, 3), _ones(4), 2, 2, False, True)
    assert s.IsVPeriodic()
    val = s.Value(0.5, 0.5)
    s.SetVNotPeriodic()
    assert not s.IsVPeriodic()
    assert val.IsEqual(s.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_RationalSurface():
    poles = _poles(3, 3, lambda i, j: (i, j, 0))
    weights = _weights(3, 3, lambda i, j: 3.0 if (i == 2 and j == 2) else 1.0)
    s = Geom_BSplineSurface(poles, weights, _reals(0, 1), _reals(0, 1), _ints(3, 3), _ints(3, 3), 2, 2)
    assert s.IsURational()
    assert s.IsVRational()
    w = s.Weights()
    assert w is not None
    assert w[2, 2] == pytest.approx(3.0)
    mid = s.Value(0.5, 0.5)
    assert abs(mid.X() - 2.0) <= 0.1
    assert abs(mid.Y() - 2.0) <= 0.1


def test_Geom_BSplineSurface_Test_LocalEvaluation(surf):
    surf.InsertUKnot(0.5, 1, 0.0)
    assert surf.NbUKnots() == 3
    glob = surf.Value(0.25, 0.5)
    loc = gp_Pnt()
    surf.LocalD0(0.25, 0.5, 1, 2, 1, 2, loc)
    assert glob.IsEqual(loc, 1e-10)


def test_Geom_BSplineSurface_Test_SetPoleRow(surf):
    surf.SetPoleRow(2, _pnts1((10, 1, 0), (10, 2, 0), (10, 3, 0)))
    for j in range(1, 4):
        assert abs(surf.Pole(2, j).X() - 10.0) <= 1e-10


def test_Geom_BSplineSurface_Test_SetPoleCol(surf):
    surf.SetPoleCol(2, _pnts1((1, 10, 0), (2, 10, 0), (3, 10, 0)))
    for i in range(1, 4):
        assert abs(surf.Pole(i, 2).Y() - 10.0) <= 1e-10


def test_Geom_BSplineSurface_Test_SetWeightRow():
    s = _rational_bump(2.0)
    s.SetWeightRow(2, _reals(3.0, 4.0, 5.0))
    assert s.Weight(2, 1) == pytest.approx(3.0)
    assert s.Weight(2, 2) == pytest.approx(4.0)
    assert s.Weight(2, 3) == pytest.approx(5.0)


def test_Geom_BSplineSurface_Test_SetWeightCol():
    s = _rational_bump(2.0)
    s.SetWeightCol(2, _reals(6.0, 7.0, 8.0))
    assert s.Weight(1, 2) == pytest.approx(6.0)
    assert s.Weight(2, 2) == pytest.approx(7.0)
    assert s.Weight(3, 2) == pytest.approx(8.0)


def test_Geom_BSplineSurface_Test_RemoveVKnot(surf):
    surf.InsertVKnot(0.5, 1, 0.0)
    assert surf.NbVKnots() == 3
    before = surf.Value(0.5, 0.25)
    assert surf.RemoveVKnot(2, 0, 1e-6)
    assert surf.NbVKnots() == 2
    assert before.IsEqual(surf.Value(0.5, 0.25), 1e-6)


def test_Geom_BSplineSurface_Test_MovePoint(surf):
    target = gp_Pnt(2, 2, 1)
    surf.MovePoint(0.5, 0.5, target, 1, surf.NbUPoles(), 1, surf.NbVPoles())
    assert surf.Value(0.5, 0.5).IsEqual(target, 1e-6)


def test_Geom_BSplineSurface_Test_LocateU(surf):
    surf.InsertUKnot(0.5, 1, 0.0)
    i1, i2 = surf.LocateU(0.25, 1e-10)
    assert i1 >= 1
    assert i2 <= surf.NbUKnots()


def test_Geom_BSplineSurface_Test_LocateV(surf):
    surf.InsertVKnot(0.5, 1, 0.0)
    i1, i2 = surf.LocateV(0.25, 1e-10)
    assert i1 >= 1
    assert i2 <= surf.NbVKnots()


def test_Geom_BSplineSurface_Test_RationalSurface_SetUNotPeriodic():
    poles = _poles(3, 3, _u_periodic_poles)
    weights = _weights(3, 3, lambda i, j: 1.0 + 0.5 * (i - 1))
    s = Geom_BSplineSurface(
        poles, weights, _reals(0, 1, 2, 3), _reals(0, 1), _ones(4), _ints(3, 3), 2, 2, True, False
    )
    assert s.IsUPeriodic()
    assert s.IsURational() or s.IsVRational()
    val = s.Value(0.5, 0.5)
    s.SetUNotPeriodic()
    assert not s.IsUPeriodic()
    assert val.IsEqual(s.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_RationalSurface_SetVNotPeriodic():
    poles = _poles(3, 3, _v_periodic_poles)
    weights = _weights(3, 3, lambda i, j: 1.0 + 0.5 * (j - 1))
    s = Geom_BSplineSurface(
        poles, weights, _reals(0, 1), _reals(0, 1, 2, 3), _ints(3, 3), _ones(4), 2, 2, False, True
    )
    assert s.IsVPeriodic()
    assert s.IsURational() or s.IsVRational()
    val = s.Value(0.5, 0.5)
    s.SetVNotPeriodic()
    assert not s.IsVPeriodic()
    assert val.IsEqual(s.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_Evaluation_D3(surf):
    p = gp_Pnt()
    v = [gp_Vec() for _ in range(9)]
    surf.D3(0.5, 0.5, p, *v)
    d3u, d3v = v[5], v[6]
    assert abs(d3u.Magnitude()) <= 1e-10
    assert abs(d3v.Magnitude()) <= 1e-10


def test_Geom_BSplineSurface_Test_IncreaseUMultiplicity(surf):
    surf.InsertUKnot(0.5, 1, 0.0)
    assert surf.UMultiplicity(2) == 1
    before = surf.Value(0.5, 0.5)
    surf.IncreaseUMultiplicity(2, 2)
    assert surf.UMultiplicity(2) == 2
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-10)


def test_Geom_BSplineSurface_Test_SetUKnot(surf):
    surf.InsertUKnot(0.5, 1, 0.0)
    surf.SetUKnot(2, 0.6)
    assert surf.UKnot(2) == pytest.approx(0.6)


def test_Geom_BSplineSurface_Test_SetVKnot(surf):
    surf.InsertVKnot(0.5, 1, 0.0)
    surf.SetVKnot(2, 0.6)
    assert surf.VKnot(2) == pytest.approx(0.6)


def test_Geom_BSplineSurface_Test_RationalSurface_UIso():
    poles = _poles(3, 3, lambda i, j: (i, j, (i + j) * 0.1))
    weights = _weights(3, 3, lambda i, j: 1.0 + 0.5 * ((i - 1) + (j - 1)))
    s = Geom_BSplineSurface(poles, weights, _reals(0, 1), _reals(0, 1), _ints(3, 3), _ints(3, 3), 2, 2)
    iso = s.UIso(0.5)
    assert iso is not None
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert s.Value(0.5, v).IsEqual(iso.Value(v), 1e-10)


def test_Geom_BSplineSurface_Test_CopyIndependence_Knots(surf):
    c = Geom_BSplineSurface(surf)
    surf.InsertUKnot(0.5, 1, 0.0)
    assert c.NbUKnots() == 2
    assert surf.NbUKnots() == 3


def test_Geom_BSplineSurface_Test_WeightsArray_NonRational_ReturnsUnitWeights(surf):
    assert not surf.IsURational()
    assert not surf.IsVRational()
    w = surf.WeightsArray()
    assert w.ColLength() == surf.NbUPoles()
    assert w.RowLength() == surf.NbVPoles()
    # IsDeletable() and the reference-identity check are C++ memory semantics: nanocct copies
    # const& results by design (Design.md 6), so the copy always owns its data.
    for i in range(w.LowerRow(), w.UpperRow() + 1):
        for j in range(w.LowerCol(), w.UpperCol() + 1):
            assert w[i, j] == pytest.approx(1.0)


def test_Geom_BSplineSurface_Test_WeightsArray_Rational_ReturnsOwning():
    poles = _poles(3, 3, lambda i, j: (i, j, 0))
    weights = _weights(3, 3, lambda i, j: 2.0 if (i == 2 and j == 2) else 1.0)
    s = Geom_BSplineSurface(poles, weights, _reals(0, 1), _reals(0, 1), _ints(3, 3), _ints(3, 3), 2, 2)
    w = s.WeightsArray()
    assert w.ColLength() == 3
    assert w.RowLength() == 3
    assert w[2, 2] == pytest.approx(2.0)
    assert w[1, 1] == pytest.approx(1.0)


def test_Geom_BSplineSurface_Test_OCC30990_CacheConsistencyAtKnots():
    nu, nv = 7, 5
    poles = _poles(
        nu, nv, lambda i, j: (float(i - 1), float(j - 1), math.sin(i * 0.5) * math.cos(j * 0.7))
    )
    s = Geom_BSplineSurface(
        poles, _reals(0.0, 0.25, 0.5, 0.75, 1.0), _reals(0.0, 0.5, 1.0), _ints(4, 1, 1, 1, 4), _ints(4, 1, 4), 3, 3
    )
    assert s is not None
    adaptor = GeomAdaptor_Surface(s)

    def same(a, b):
        return a.X() == b.X() and a.Y() == b.Y() and a.Z() == b.Z()

    nb_err = 0
    for i in range(2, s.NbUKnots()):
        uk = s.UKnot(i)
        uprev = 0.5 * (uk + s.UKnot(i - 1))
        unext = 0.5 * (uk + s.UKnot(i + 1))
        for j in range(1, s.NbVKnots()):
            v = 0.5 * (s.VKnot(j) + s.VKnot(j + 1))
            adaptor.Value(uprev, v)
            p1 = adaptor.Value(uk, v)
            adaptor.Value(unext, v)
            p2 = adaptor.Value(uk, v)
            if not same(p1, p2):
                nb_err += 1
    for j in range(2, s.NbVKnots()):
        vk = s.VKnot(j)
        vprev = 0.5 * (vk + s.VKnot(j - 1))
        vnext = 0.5 * (vk + s.VKnot(j + 1))
        for i in range(1, s.NbUKnots()):
            u = 0.5 * (s.UKnot(i) + s.UKnot(i + 1))
            adaptor.Value(u, vprev)
            p1 = adaptor.Value(u, vk)
            adaptor.Value(u, vnext)
            p2 = adaptor.Value(u, vk)
            if not same(p1, p2):
                nb_err += 1
    assert nb_err == 0
