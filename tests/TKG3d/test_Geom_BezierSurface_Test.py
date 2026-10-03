# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_BezierSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_BezierSurface
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec


def _row(*pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        a[i] = gp_Pnt(*p)
    return a


def _w1(*ws):
    a = NCollection_Array1[float](1, len(ws))
    for i, w in enumerate(ws, 1):
        a[i] = w
    return a


def _poles2x2(p22=(1, 1, 0)):
    a = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    a[1, 1] = gp_Pnt(0, 0, 0)
    a[1, 2] = gp_Pnt(1, 0, 0)
    a[2, 1] = gp_Pnt(0, 1, 0)
    a[2, 2] = gp_Pnt(*p22)
    return a


def _w2x2(w11, w12, w21, w22):
    a = NCollection_Array2[float](1, 2, 1, 2)
    a[1, 1] = w11
    a[1, 2] = w12
    a[2, 1] = w21
    a[2, 2] = w22
    return a


def _rational2x2(w11=1.0, w12=2.0, w21=2.0, w22=1.0, p22=(1, 1, 0)):
    return Geom_BezierSurface(_poles2x2(p22), _w2x2(w11, w12, w21, w22))


def _frange(start, stop, step):
    x = start
    while x <= stop:
        yield x
        x += step


@pytest.fixture
def surf():
    a = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            a[i, j] = gp_Pnt(i, j, (i + j) * 0.1)
    return Geom_BezierSurface(a)


def test_Geom_BezierSurface_Test_CopyConstructorBasicProperties(surf):
    cp = Geom_BezierSurface(surf)
    assert surf.UDegree() == cp.UDegree()
    assert surf.VDegree() == cp.VDegree()
    assert surf.NbUPoles() == cp.NbUPoles()
    assert surf.NbVPoles() == cp.NbVPoles()
    assert surf.IsURational() == cp.IsURational()
    assert surf.IsVRational() == cp.IsVRational()


def test_Geom_BezierSurface_Test_CopyConstructorPoles(surf):
    cp = Geom_BezierSurface(surf)
    for i in range(1, surf.NbUPoles() + 1):
        for j in range(1, surf.NbVPoles() + 1):
            assert surf.Pole(i, j).IsEqual(cp.Pole(i, j), 1e-10)


def test_Geom_BezierSurface_Test_CopyMethodUsesOptimizedConstructor(surf):
    cp = surf.Copy()
    assert isinstance(cp, Geom_BezierSurface)
    assert surf.UDegree() == cp.UDegree()
    assert surf.VDegree() == cp.VDegree()
    for u in (0.0, 0.5, 1.0):
        for v in (0.0, 0.5, 1.0):
            assert surf.Value(u, v).IsEqual(cp.Value(u, v), 1e-10)


def test_Geom_BezierSurface_Test_RationalSurfaceCopyConstructor():
    rs = _rational2x2()
    cp = Geom_BezierSurface(rs)
    assert cp.IsURational() or cp.IsVRational()
    for i in range(1, rs.NbUPoles() + 1):
        for j in range(1, rs.NbVPoles() + 1):
            assert rs.Weight(i, j) == pytest.approx(cp.Weight(i, j))


def test_Geom_BezierSurface_Test_CopyIndependence(surf):
    cp = Geom_BezierSurface(surf)
    new_pole = gp_Pnt(10, 10, 10)
    surf.SetPole(2, 2, new_pole)
    assert not cp.Pole(2, 2).IsEqual(new_pole, 1e-10)


def test_Geom_BezierSurface_Test_Evaluation_D0(surf):
    p = gp_Pnt()
    surf.D0(0.0, 0.0, p)
    assert p.IsEqual(gp_Pnt(1, 1, 0.2), 1e-10)
    surf.D0(1.0, 1.0, p)
    assert p.IsEqual(gp_Pnt(3, 3, 0.6), 1e-10)


def test_Geom_BezierSurface_Test_Evaluation_D1(surf):
    p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
    surf.D1(0.5, 0.5, p, du, dv)
    assert du.Magnitude() > 0.0
    assert dv.Magnitude() > 0.0


def test_Geom_BezierSurface_Test_Evaluation_D2(surf):
    p = gp_Pnt()
    du, dv, duu, dvv, duv = (gp_Vec() for _ in range(5))
    surf.D2(0.5, 0.5, p, du, dv, duu, dvv, duv)
    assert du.Magnitude() > 0.0


def test_Geom_BezierSurface_Test_Evaluation_DN(surf):
    assert surf.DN(0.5, 0.5, 1, 0).Magnitude() > 0.0
    assert surf.DN(0.5, 0.5, 0, 1).Magnitude() > 0.0


def test_Geom_BezierSurface_Test_Properties(surf):
    assert surf.UDegree() == 2
    assert surf.VDegree() == 2
    assert not surf.IsUPeriodic()
    assert not surf.IsVPeriodic()
    assert not surf.IsURational()
    assert not surf.IsVRational()
    assert surf.NbUPoles() == 3
    assert surf.NbVPoles() == 3
    assert surf.IsCNu(100)
    assert surf.IsCNv(100)


def test_Geom_BezierSurface_Test_Bounds(surf):
    u1, u2, v1, v2 = surf.Bounds()
    assert u1 == pytest.approx(0.0)
    assert u2 == pytest.approx(1.0)
    assert v1 == pytest.approx(0.0)
    assert v2 == pytest.approx(1.0)


def test_Geom_BezierSurface_Test_SetPole(surf):
    new_pole = gp_Pnt(5, 5, 5)
    surf.SetPole(2, 2, new_pole)
    assert surf.Pole(2, 2).IsEqual(new_pole, 1e-10)


def test_Geom_BezierSurface_Test_SetWeight():
    s = _rational2x2(1.0, 1.0, 1.0, 1.0)
    before = s.Value(0.5, 0.5)
    s.SetWeight(2, 2, 10.0)
    assert s.Weight(2, 2) == pytest.approx(10.0)
    assert s.IsURational() or s.IsVRational()
    assert not before.IsEqual(s.Value(0.5, 0.5), 1e-6)


def test_Geom_BezierSurface_Test_Increase(surf):
    before = surf.Value(0.5, 0.5)
    surf.Increase(4, 3)
    assert surf.UDegree() == 4
    assert surf.VDegree() == 3
    assert surf.NbUPoles() == 5
    assert surf.NbVPoles() == 4
    assert before.IsEqual(surf.Value(0.5, 0.5), 1e-10)


def test_Geom_BezierSurface_Test_Segment(surf):
    before = surf.Value(0.5, 0.5)
    surf.Segment(0.25, 0.75, 0.25, 0.75)
    assert surf.Value(0.5, 0.5).IsEqual(before, 1e-6)


def test_Geom_BezierSurface_Test_ExchangeUV(surf):
    before = surf.Value(0.3, 0.7)
    udeg, vdeg = surf.UDegree(), surf.VDegree()
    surf.ExchangeUV()
    assert surf.UDegree() == vdeg
    assert surf.VDegree() == udeg
    assert before.IsEqual(surf.Value(0.7, 0.3), 1e-10)


def test_Geom_BezierSurface_Test_UReverse(surf):
    before = surf.Value(0.3, 0.5)
    surf.UReverse()
    assert before.IsEqual(surf.Value(0.7, 0.5), 1e-10)


def test_Geom_BezierSurface_Test_VReverse(surf):
    before = surf.Value(0.5, 0.3)
    surf.VReverse()
    assert before.IsEqual(surf.Value(0.5, 0.7), 1e-10)


def test_Geom_BezierSurface_Test_UIso(surf):
    iso = surf.UIso(0.5)
    assert iso is not None
    for v in _frange(0.0, 1.0, 0.25):
        assert surf.Value(0.5, v).IsEqual(iso.Value(v), 1e-10)


def test_Geom_BezierSurface_Test_VIso(surf):
    iso = surf.VIso(0.5)
    assert iso is not None
    for u in _frange(0.0, 1.0, 0.25):
        assert surf.Value(u, 0.5).IsEqual(iso.Value(u), 1e-10)


def test_Geom_BezierSurface_Test_Resolution(surf):
    utol, vtol = surf.Resolution(1.0)
    assert utol > 0.0
    assert vtol > 0.0


def test_Geom_BezierSurface_Test_Transform(surf):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(10, 20, 30))
    before = surf.Value(0.5, 0.5)
    surf.Transform(t)
    after = surf.Value(0.5, 0.5)
    assert abs(after.X() - (before.X() + 10.0)) <= 1e-10
    assert abs(after.Y() - (before.Y() + 20.0)) <= 1e-10
    assert abs(after.Z() - (before.Z() + 30.0)) <= 1e-10


def test_Geom_BezierSurface_Test_InsertPoleRowAfter(surf):
    nb = surf.NbUPoles()
    surf.InsertPoleRowAfter(1, _row((1.5, 1, 0), (1.5, 2, 0), (1.5, 3, 0)))
    assert surf.NbUPoles() == nb + 1
    assert surf.UDegree() == 3


def test_Geom_BezierSurface_Test_InsertPoleColAfter(surf):
    nb = surf.NbVPoles()
    surf.InsertPoleColAfter(1, _row((1, 1.5, 0), (2, 1.5, 0), (3, 1.5, 0)))
    assert surf.NbVPoles() == nb + 1
    assert surf.VDegree() == 3


def test_Geom_BezierSurface_Test_RemovePoleRow(surf):
    surf.InsertPoleRowAfter(1, _row((1.5, 1, 0), (1.5, 2, 0), (1.5, 3, 0)))
    assert surf.NbUPoles() == 4
    surf.RemovePoleRow(2)
    assert surf.NbUPoles() == 3


def test_Geom_BezierSurface_Test_RemovePoleCol(surf):
    surf.InsertPoleColAfter(1, _row((1, 1.5, 0), (2, 1.5, 0), (3, 1.5, 0)))
    assert surf.NbVPoles() == 4
    surf.RemovePoleCol(2)
    assert surf.NbVPoles() == 3


def test_Geom_BezierSurface_Test_SetPoleRow(surf):
    surf.SetPoleRow(2, _row((10, 1, 0), (10, 2, 0), (10, 3, 0)))
    for j in range(1, 4):
        assert abs(surf.Pole(2, j).X() - 10.0) <= 1e-10


def test_Geom_BezierSurface_Test_SetPoleCol(surf):
    surf.SetPoleCol(2, _row((1, 10, 0), (2, 10, 0), (3, 10, 0)))
    for i in range(1, 4):
        assert abs(surf.Pole(i, 2).Y() - 10.0) <= 1e-10


def test_Geom_BezierSurface_Test_WeightsAccess_NonRational(surf):
    assert surf.Weights() is None


def test_Geom_BezierSurface_Test_PolesAccess(surf):
    poles = surf.Poles()
    assert poles.ColLength() == 3
    assert poles.RowLength() == 3
    assert poles[1, 1].IsEqual(gp_Pnt(1, 1, 0.2), 1e-10)


def test_Geom_BezierSurface_Test_MaxDegree():
    assert Geom_BezierSurface.MaxDegree_s() >= 25


def test_Geom_BezierSurface_Test_RationalSurface_UIso():
    s = _rational2x2()
    iso = s.UIso(0.5)
    assert iso is not None
    for v in _frange(0.0, 1.0, 0.25):
        assert s.Value(0.5, v).IsEqual(iso.Value(v), 1e-10)


def test_Geom_BezierSurface_Test_Evaluation_D3(surf):
    p = gp_Pnt()
    vs = [gp_Vec() for _ in range(9)]
    surf.D3(0.5, 0.5, p, *vs)
    d3u, d3v = vs[5], vs[6]
    assert abs(d3u.Magnitude()) <= 1e-10
    assert abs(d3v.Magnitude()) <= 1e-10


def test_Geom_BezierSurface_Test_InsertPoleRowBefore(surf):
    nb = surf.NbUPoles()
    surf.InsertPoleRowBefore(2, _row((0.5, 1, 0), (0.5, 2, 0), (0.5, 3, 0)))
    assert surf.NbUPoles() == nb + 1
    assert surf.Pole(2, 1).IsEqual(gp_Pnt(0.5, 1, 0), 1e-10)


def test_Geom_BezierSurface_Test_InsertPoleColBefore(surf):
    nb = surf.NbVPoles()
    surf.InsertPoleColBefore(2, _row((1, 0.5, 0), (2, 0.5, 0), (3, 0.5, 0)))
    assert surf.NbVPoles() == nb + 1
    assert surf.Pole(1, 2).IsEqual(gp_Pnt(1, 0.5, 0), 1e-10)


def test_Geom_BezierSurface_Test_RationalSegment():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    weights = NCollection_Array2[float](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles[i, j] = gp_Pnt(i, j, (i + j) * 0.1)
            weights[i, j] = 1.0 + 0.3 * ((i - 1) + (j - 1))
    s = Geom_BezierSurface(poles, weights)
    assert s.IsURational() or s.IsVRational()
    mid = s.Value(0.5, 0.5)
    s.Segment(0.25, 0.75, 0.25, 0.75)
    assert mid.IsEqual(s.Value(0.5, 0.5), 1e-5)


def test_Geom_BezierSurface_Test_RationalIncrease():
    s = _rational2x2(p22=(1, 1, 1))
    before = s.Value(0.5, 0.5)
    s.Increase(3, 3)
    assert s.UDegree() == 3
    assert s.VDegree() == 3
    assert before.IsEqual(s.Value(0.5, 0.5), 1e-10)


def test_Geom_BezierSurface_Test_SetWeightRow():
    s = _rational2x2(1.0, 2.0, 3.0, 4.0)
    s.SetWeightRow(1, _w1(5.0, 6.0))
    assert s.Weight(1, 1) == pytest.approx(5.0)
    assert s.Weight(1, 2) == pytest.approx(6.0)


def test_Geom_BezierSurface_Test_SetWeightCol():
    s = _rational2x2(1.0, 2.0, 3.0, 4.0)
    s.SetWeightCol(1, _w1(7.0, 8.0))
    assert s.Weight(1, 1) == pytest.approx(7.0)
    assert s.Weight(2, 1) == pytest.approx(8.0)


def test_Geom_BezierSurface_Test_InsertPoleRowAfterWithWeights():
    s = _rational2x2()
    s.InsertPoleRowAfter(1, _row((0, 0.5, 0), (1, 0.5, 0)), _w1(3.0, 4.0))
    assert s.NbUPoles() == 3
    assert s.Weight(2, 1) == pytest.approx(3.0)
    assert s.Weight(2, 2) == pytest.approx(4.0)


def test_Geom_BezierSurface_Test_VIso_Rational():
    s = _rational2x2()
    iso = s.VIso(0.5)
    assert iso is not None
    for u in _frange(0.0, 1.0, 0.25):
        assert s.Value(u, 0.5).IsEqual(iso.Value(u), 1e-10)


def test_Geom_BezierSurface_Test_SetPoleWithWeight():
    s = _rational2x2(1.0, 1.0, 1.0, 2.0)
    new_pole = gp_Pnt(0.5, 0.5, 1.0)
    s.SetPole(1, 1, new_pole, 5.0)
    assert s.Pole(1, 1).IsEqual(new_pole, 1e-10)
    assert s.Weight(1, 1) == pytest.approx(5.0)


def test_Geom_BezierSurface_Test_SetPoleColWithWeights():
    s = _rational2x2()
    s.SetPoleCol(2, _row((5, 0, 0), (5, 1, 0)), _w1(3.0, 4.0))
    assert s.Pole(1, 2).IsEqual(gp_Pnt(5, 0, 0), 1e-10)
    assert s.Weight(1, 2) == pytest.approx(3.0)
    assert s.Weight(2, 2) == pytest.approx(4.0)


def test_Geom_BezierSurface_Test_WeightsArray_NonRational_ReturnsUnitWeights(surf):
    # IsDeletable() and the address identity of the returned reference are C++ reference semantics:
    # the binding returns a copy, so only the values are checked.
    assert not surf.IsURational()
    assert not surf.IsVRational()
    w = surf.WeightsArray()
    assert w.ColLength() == surf.NbUPoles()
    assert w.RowLength() == surf.NbVPoles()
    for i in range(w.LowerRow(), w.UpperRow() + 1):
        for j in range(w.LowerCol(), w.UpperCol() + 1):
            assert w[i, j] == pytest.approx(1.0)


def test_Geom_BezierSurface_Test_WeightsArray_Rational_ReturnsOwning():
    s = _rational2x2(1.0, 2.0, 1.0, 1.0)
    w = s.WeightsArray()
    assert w.Size() == 4
    assert w.IsDeletable()
    assert w[1, 2] == pytest.approx(2.0)
    assert w[1, 1] == pytest.approx(1.0)
