# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dHash_CurveHasher_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom2d import (
    Geom2d_BezierCurve,
    Geom2d_BSplineCurve,
    Geom2d_Circle,
    Geom2d_Ellipse,
    Geom2d_Hyperbola,
    Geom2d_Line,
    Geom2d_OffsetCurve,
    Geom2d_Parabola,
    Geom2d_TrimmedCurve,
)
from nanocct.Geom2dHash import Geom2dHash_CurveHasher
from nanocct.gp import gp_Ax22d, gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1


@pytest.fixture
def h():
    return Geom2dHash_CurveHasher()


def arr_pnt(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a[i] = gp_Pnt2d(x, y)
    return a


def arr(typ, *vals):
    a = NCollection_Array1[typ](1, len(vals))
    for i, v in enumerate(vals, 1):
        a[i] = v
    return a


def ax(ox=0.0, oy=0.0, xd=(1.0, 0.0), yd=(0.0, 1.0)):
    return gp_Ax22d(gp_Pnt2d(ox, oy), gp_Dir2d(*xd), gp_Dir2d(*yd))


def line(x=0.0, y=0.0, dx=1.0, dy=0.0):
    return Geom2d_Line(gp_Pnt2d(x, y), gp_Dir2d(dx, dy))


def same(h, c1, c2):
    assert h(c1) == h(c2)
    assert h(c1, c2) is True


def differ(h, c1, c2):
    assert h(c1) != h(c2)
    assert h(c1, c2) is False


def copied(h, c):
    cp = c.Copy()
    assert type(cp) is type(c)
    same(h, c, cp)


QUAD = ((0.0, 0.0), (1.0, 1.0), (2.0, 1.0), (3.0, 0.0))


def test_Geom2dHash_CurveHasherTest_Line_CopiedLines_SameHash(h):
    copied(h, Geom2d_Line(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0)))


def test_Geom2dHash_CurveHasherTest_Line_DifferentLines_DifferentHash(h):
    differ(h, line(), line(1.0, 0.0))


def test_Geom2dHash_CurveHasherTest_Circle_CopiedCircles_SameHash(h):
    copied(h, Geom2d_Circle(ax(), 5.0))


def test_Geom2dHash_CurveHasherTest_Circle_DifferentRadius_DifferentHash(h):
    differ(h, Geom2d_Circle(ax(), 5.0), Geom2d_Circle(ax(), 10.0))


def test_Geom2dHash_CurveHasherTest_Ellipse_CopiedEllipses_SameHash(h):
    copied(h, Geom2d_Ellipse(ax(), 10.0, 5.0))


def test_Geom2dHash_CurveHasherTest_Ellipse_DifferentRadii_DifferentHash(h):
    differ(h, Geom2d_Ellipse(ax(), 10.0, 5.0), Geom2d_Ellipse(ax(), 10.0, 7.0))


def test_Geom2dHash_CurveHasherTest_Hyperbola_CopiedHyperbolas_SameHash(h):
    copied(h, Geom2d_Hyperbola(ax(), 5.0, 3.0))


def test_Geom2dHash_CurveHasherTest_Hyperbola_DifferentRadii_DifferentHash(h):
    differ(h, Geom2d_Hyperbola(ax(), 5.0, 3.0), Geom2d_Hyperbola(ax(), 5.0, 4.0))


def test_Geom2dHash_CurveHasherTest_Parabola_CopiedParabolas_SameHash(h):
    copied(h, Geom2d_Parabola(ax(), 2.0))


def test_Geom2dHash_CurveHasherTest_Parabola_DifferentFocal_DifferentHash(h):
    differ(h, Geom2d_Parabola(ax(), 2.0), Geom2d_Parabola(ax(), 3.0))


def test_Geom2dHash_CurveHasherTest_BezierCurve_CopiedCurves_SameHash(h):
    copied(h, Geom2d_BezierCurve(arr_pnt((0.0, 0.0), (1.0, 2.0), (3.0, 2.0), (4.0, 0.0))))


def test_Geom2dHash_CurveHasherTest_BezierCurve_DifferentPoles_DifferentComparison(h):
    c1 = Geom2d_BezierCurve(arr_pnt((0.0, 0.0), (1.0, 2.0), (2.0, 0.0)))
    c2 = Geom2d_BezierCurve(arr_pnt((0.0, 0.0), (1.0, 3.0), (2.0, 0.0)))
    assert h(c1, c2) is False


def test_Geom2dHash_CurveHasherTest_BSplineCurve_CopiedCurves_SameHash(h):
    copied(h, Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 0.0, 1.0), arr(int, 4, 4), 3))


def test_Geom2dHash_CurveHasherTest_TrimmedCurve_CopiedCurves_SameHash(h):
    copied(h, Geom2d_TrimmedCurve(line(), 0.0, 10.0))


def test_Geom2dHash_CurveHasherTest_TrimmedCurve_DifferentBounds_DifferentHash(h):
    l = line()
    differ(h, Geom2d_TrimmedCurve(l, 0.0, 10.0), Geom2d_TrimmedCurve(l, 0.0, 20.0))


def test_Geom2dHash_CurveHasherTest_OffsetCurve_CopiedCurves_SameHash(h):
    copied(h, Geom2d_OffsetCurve(line(), 5.0))


def test_Geom2dHash_CurveHasherTest_OffsetCurve_DifferentOffset_DifferentHash(h):
    l = line()
    differ(h, Geom2d_OffsetCurve(l, 5.0), Geom2d_OffsetCurve(l, 10.0))


def test_Geom2dHash_CurveHasherTest_DifferentTypes_DifferentComparison(h):
    assert h(line(), Geom2d_Circle(ax(), 5.0)) is False


def test_Geom2dHash_CurveHasherTest_NullCurves_HandledCorrectly(h):
    assert h(None) == 0
    assert h(None, None) is True
    assert h(line(), None) is False


def test_Geom2dHash_CurveHasherTest_SameObject_Equal(h):
    l = line()
    assert h(l, l) is True


def test_Geom2dHash_CurveHasherTest_BSplineCurve_Weighted_CopiedCurves_SameHash(h):
    copied(
        h,
        Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 1.0, 2.0, 2.0, 1.0), arr(float, 0.0, 1.0), arr(int, 4, 4), 3),
    )


def test_Geom2dHash_CurveHasherTest_BSplineCurve_DifferentWeights_DifferentComparison(h):
    k, m = arr(float, 0.0, 1.0), arr(int, 4, 4)
    c1 = Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 1.0, 2.0, 2.0, 1.0), k, m, 3)
    c2 = Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 1.0, 3.0, 2.0, 1.0), k, m, 3)
    assert h(c1, c2) is False


def test_Geom2dHash_CurveHasherTest_BezierCurve_Weighted_CopiedCurves_SameHash(h):
    copied(h, Geom2d_BezierCurve(arr_pnt((0.0, 0.0), (1.0, 2.0), (2.0, 0.0)), arr(float, 1.0, 2.0, 1.0)))


def test_Geom2dHash_CurveHasherTest_Circle_DifferentAxisOrientation_DifferentHash(h):
    differ(h, Geom2d_Circle(ax(), 5.0), Geom2d_Circle(ax(xd=(0.0, 1.0), yd=(-1.0, 0.0)), 5.0))


def test_Geom2dHash_CurveHasherTest_Line_DifferentDirection_DifferentHash(h):
    differ(h, line(), line(dx=0.0, dy=1.0))


def test_Geom2dHash_CurveHasherTest_BSplineCurve_DifferentKnots_DifferentComparison(h):
    m = arr(int, 4, 4)
    c1 = Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 0.0, 1.0), m, 3)
    c2 = Geom2d_BSplineCurve(arr_pnt(*QUAD), arr(float, 0.0, 2.0), m, 3)
    assert h(c1, c2) is False


def test_Geom2dHash_CurveHasherTest_BSplineCurve_QuadraticBezierEquivalent_CopiedCurves_SameHash(h):
    copied(
        h, Geom2d_BSplineCurve(arr_pnt((0.0, 0.0), (1.0, 2.0), (2.0, 0.0)), arr(float, 0.0, 1.0), arr(int, 3, 3), 2)
    )


def test_Geom2dHash_CurveHasherTest_Line_Reversed_DifferentComparison(h):
    l = line()
    assert h(l, l.Reversed()) is False


def test_Geom2dHash_CurveHasherTest_BezierCurve_Reversed_DifferentComparison(h):
    c = Geom2d_BezierCurve(arr_pnt((0.0, 0.0), (1.0, 2.0), (2.0, 0.0)))
    assert h(c, c.Reversed()) is False


def test_Geom2dHash_CurveHasherTest_Circle_Translated_DifferentHash(h):
    c1 = Geom2d_Circle(ax(), 5.0)
    c2 = c1.Copy()
    c2.Translate(gp_Vec2d(1.0, 0.0))
    differ(h, c1, c2)


def test_Geom2dHash_CurveHasherTest_Circle_Scaled_DifferentHash(h):
    c1 = Geom2d_Circle(ax(), 5.0)
    c2 = c1.Copy()
    c2.Scale(gp_Pnt2d(0.0, 0.0), 2.0)
    differ(h, c1, c2)


def test_Geom2dHash_CurveHasherTest_BSplineCurve_HigherDegree_CopiedCurves_SameHash(h):
    p = arr_pnt((0.0, 0.0), (1.0, 1.0), (2.0, 0.5), (3.0, 1.5), (4.0, 0.0), (5.0, 1.0))
    copied(h, Geom2d_BSplineCurve(p, arr(float, 0.0, 1.0), arr(int, 6, 6), 5))


def test_Geom2dHash_CurveHasherTest_BSplineCurve_LinearMultipleSpans_CopiedCurves_SameHash(h):
    p = arr_pnt((0.0, 0.0), (1.0, 1.0), (2.0, 0.0), (3.0, 1.0))
    copied(h, Geom2d_BSplineCurve(p, arr(float, 0.0, 1.0, 2.0, 3.0), arr(int, 2, 1, 1, 2), 1))


def test_Geom2dHash_CurveHasherTest_Ellipse_vs_Hyperbola_DifferentComparison(h):
    assert h(Geom2d_Ellipse(ax(), 5.0, 3.0), Geom2d_Hyperbola(ax(), 5.0, 3.0)) is False


def test_Geom2dHash_CurveHasherTest_Circle_vs_Ellipse_DifferentComparison(h):
    assert h(Geom2d_Circle(ax(), 5.0), Geom2d_Ellipse(ax(), 5.0, 5.0)) is False


def test_Geom2dHash_CurveHasherTest_TrimmedCurve_vs_BaseCurve_DifferentComparison(h):
    l = line()
    assert h(l, Geom2d_TrimmedCurve(l, 0.0, 10.0)) is False


def test_Geom2dHash_CurveHasherTest_Circle_VerySmallRadius_CopiedCircles_SameHash(h):
    copied(h, Geom2d_Circle(ax(), 1e-10))


def test_Geom2dHash_CurveHasherTest_Circle_VeryLargeRadius_CopiedCircles_SameHash(h):
    copied(h, Geom2d_Circle(ax(), 1e10))


def test_Geom2dHash_CurveHasherTest_Line_AtOrigin_vs_FarFromOrigin_DifferentHash(h):
    differ(h, line(), line(1e10, 1e10))
