# Translated from OCCT src/ModelingData/TKG2d/GTests/Adaptor2d_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Adaptor2d import Adaptor2d_Line2d, Adaptor2d_OffsetCurve
from nanocct.GeomAbs import GeomAbs_CN, GeomAbs_Line
from nanocct.gp import gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def base():
    return Adaptor2d_Line2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0), 0.0, 10.0)


def test_Adaptor2d_OffsetCurveTest_DefaultConstructor():
    deq(Adaptor2d_OffsetCurve().Offset(), 0.0)


def test_Adaptor2d_OffsetCurveTest_ConstructWithCurve_OffsetIsZero(base):
    o = Adaptor2d_OffsetCurve(base)
    deq(o.Offset(), 0.0)
    deq(o.FirstParameter(), 0.0)
    deq(o.LastParameter(), 0.0)


def test_Adaptor2d_OffsetCurveTest_ConstructWithOffset(base):
    o = Adaptor2d_OffsetCurve(base, 3.0)
    deq(o.Offset(), 3.0)
    deq(o.FirstParameter(), 0.0)
    deq(o.LastParameter(), 10.0)


def test_Adaptor2d_OffsetCurveTest_ConstructWithOffsetAndBounds(base):
    o = Adaptor2d_OffsetCurve(base, 2.0, 1.0, 8.0)
    deq(o.Offset(), 2.0)
    deq(o.FirstParameter(), 1.0)
    deq(o.LastParameter(), 8.0)


def test_Adaptor2d_OffsetCurveTest_Value_PositiveOffset(base):
    p = Adaptor2d_OffsetCurve(base, 3.0).Value(5.0)
    assert abs(p.X() - 5.0) <= TOL
    assert abs(p.Y() + 3.0) <= TOL


def test_Adaptor2d_OffsetCurveTest_Value_NegativeOffset(base):
    p = Adaptor2d_OffsetCurve(base, -2.0).Value(5.0)
    assert abs(p.X() - 5.0) <= TOL
    assert abs(p.Y() - 2.0) <= TOL


def test_Adaptor2d_OffsetCurveTest_Value_ZeroOffset_MatchesBaseCurve(base):
    o = Adaptor2d_OffsetCurve(base, 0.0)
    for u in (0.0, 2.0, 4.0, 6.0, 8.0, 10.0):
        assert o.Value(u).IsEqual(base.Value(u), TOL)


def test_Adaptor2d_OffsetCurveTest_D1_OffsetLine(base):
    o = Adaptor2d_OffsetCurve(base, 3.0)
    p, v = gp_Pnt2d(), gp_Vec2d()
    o.D1(5.0, p, v)
    assert abs(v.X() - 1.0) <= TOL
    assert abs(v.Y()) <= TOL


def test_Adaptor2d_OffsetCurveTest_Continuity(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).Continuity() == GeomAbs_CN


def test_Adaptor2d_OffsetCurveTest_NbIntervals(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).NbIntervals(GeomAbs_CN) == 1


def test_Adaptor2d_OffsetCurveTest_GetType_Line(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).GetType() == GeomAbs_Line


def test_Adaptor2d_OffsetCurveTest_IsNotClosed(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).IsClosed() is False


def test_Adaptor2d_OffsetCurveTest_IsNotPeriodic(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).IsPeriodic() is False


def test_Adaptor2d_OffsetCurveTest_LoadCurve_ResetsOffset(base):
    o = Adaptor2d_OffsetCurve(base, 5.0)
    deq(o.Offset(), 5.0)
    o.Load(Adaptor2d_Line2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(0.0, 1.0), 0.0, 5.0))
    deq(o.Offset(), 0.0)


def test_Adaptor2d_OffsetCurveTest_LoadOffset(base):
    o = Adaptor2d_OffsetCurve(base)
    deq(o.Offset(), 0.0)
    o.Load(7.5)
    deq(o.Offset(), 7.5)


def test_Adaptor2d_OffsetCurveTest_LoadOffsetWithBounds(base):
    o = Adaptor2d_OffsetCurve(base)
    o.Load(4.0, 2.0, 6.0)
    deq(o.Offset(), 4.0)
    deq(o.FirstParameter(), 2.0)
    deq(o.LastParameter(), 6.0)


def test_Adaptor2d_OffsetCurveTest_Curve_ReturnsBaseCurve(base):
    c = Adaptor2d_OffsetCurve(base, 3.0).Curve()
    assert c is not None
    assert c.GetType() == GeomAbs_Line


def test_Adaptor2d_OffsetCurveTest_Trim(base):
    t = Adaptor2d_OffsetCurve(base, 3.0).Trim(2.0, 7.0, TOL)
    deq(t.FirstParameter(), 2.0)
    deq(t.LastParameter(), 7.0)


def test_Adaptor2d_OffsetCurveTest_ShallowCopy(base):
    o = Adaptor2d_OffsetCurve(base, 3.0, 1.0, 9.0)
    c = o.ShallowCopy()
    deq(c.FirstParameter(), 1.0)
    deq(c.LastParameter(), 9.0)
    assert o.Value(5.0).IsEqual(c.Value(5.0), TOL)


def test_Adaptor2d_OffsetCurveTest_Resolution(base):
    assert Adaptor2d_OffsetCurve(base, 3.0).Resolution(0.001) > 0.0
