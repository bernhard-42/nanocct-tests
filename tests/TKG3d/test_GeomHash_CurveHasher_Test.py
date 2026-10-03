# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomHash_CurveHasher_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import (
    Geom_BezierCurve,
    Geom_BSplineCurve,
    Geom_Circle,
    Geom_Ellipse,
    Geom_Hyperbola,
    Geom_Line,
    Geom_OffsetCurve,
    Geom_Parabola,
    Geom_TrimmedCurve,
)
from nanocct.GeomHash import GeomHash_CurveHasher
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1


def _pnts(*coords):
    arr = NCollection_Array1[gp_Pnt](1, len(coords))
    for i, c in enumerate(coords, start=1):
        arr[i] = gp_Pnt(*c)
    return arr


def _reals(*vals):
    arr = NCollection_Array1[float](1, len(vals))
    for i, v in enumerate(vals, start=1):
        arr[i] = float(v)
    return arr


def _ints(*vals):
    arr = NCollection_Array1[int](1, len(vals))
    for i, v in enumerate(vals, start=1):
        arr[i] = v
    return arr


def _zaxis():
    return gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))


def _line(p=(0.0, 0.0, 0.0), d=(1.0, 0.0, 0.0)):
    return Geom_Line(gp_Pnt(*p), gp_Dir(*d))


def _assert_same(h, a, b):
    assert h(a) == h(b)
    assert h(a, b)


def _assert_diff(h, a, b):
    assert h(a) != h(b)
    assert not h(a, b)


_CUBIC_POLES = ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 1.0, 0.0), (3.0, 0.0, 0.0))


def test_GeomHash_CurveHasherTest_Line_CopiedLines_SameHash():
    h = GeomHash_CurveHasher()
    l1 = Geom_Line(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(1.0, 0.0, 0.0))
    _assert_same(h, l1, l1.Copy())


def test_GeomHash_CurveHasherTest_Line_DifferentLines_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, _line(), _line(p=(1.0, 0.0, 0.0)))


def test_GeomHash_CurveHasherTest_Circle_CopiedCircles_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_Circle(_zaxis(), 5.0)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Circle_DifferentRadius_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, Geom_Circle(_zaxis(), 5.0), Geom_Circle(_zaxis(), 10.0))


def test_GeomHash_CurveHasherTest_Ellipse_CopiedEllipses_SameHash():
    h = GeomHash_CurveHasher()
    e1 = Geom_Ellipse(_zaxis(), 10.0, 5.0)
    _assert_same(h, e1, e1.Copy())


def test_GeomHash_CurveHasherTest_Ellipse_DifferentRadii_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, Geom_Ellipse(_zaxis(), 10.0, 5.0), Geom_Ellipse(_zaxis(), 10.0, 7.0))


def test_GeomHash_CurveHasherTest_Hyperbola_CopiedHyperbolas_SameHash():
    h = GeomHash_CurveHasher()
    h1 = Geom_Hyperbola(_zaxis(), 5.0, 3.0)
    _assert_same(h, h1, h1.Copy())


def test_GeomHash_CurveHasherTest_Hyperbola_DifferentRadii_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, Geom_Hyperbola(_zaxis(), 5.0, 3.0), Geom_Hyperbola(_zaxis(), 5.0, 4.0))


def test_GeomHash_CurveHasherTest_Parabola_CopiedParabolas_SameHash():
    h = GeomHash_CurveHasher()
    p1 = Geom_Parabola(_zaxis(), 2.0)
    _assert_same(h, p1, p1.Copy())


def test_GeomHash_CurveHasherTest_Parabola_DifferentFocal_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, Geom_Parabola(_zaxis(), 2.0), Geom_Parabola(_zaxis(), 3.0))


def test_GeomHash_CurveHasherTest_BezierCurve_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_BezierCurve(_pnts((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (3.0, 2.0, 0.0), (4.0, 0.0, 0.0)))
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_BezierCurve_DifferentPoles_DifferentComparison():
    h = GeomHash_CurveHasher()
    c1 = Geom_BezierCurve(_pnts((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (2.0, 0.0, 0.0)))
    c2 = Geom_BezierCurve(_pnts((0.0, 0.0, 0.0), (1.0, 3.0, 0.0), (2.0, 0.0, 0.0)))
    assert not h(c1, c2)


def test_GeomHash_CurveHasherTest_BSplineCurve_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(0.0, 1.0), _ints(4, 4), 3)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_TrimmedCurve_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    t1 = Geom_TrimmedCurve(_line(), 0.0, 10.0)
    _assert_same(h, t1, t1.Copy())


def test_GeomHash_CurveHasherTest_TrimmedCurve_DifferentBounds_DifferentHash():
    h = GeomHash_CurveHasher()
    line = _line()
    _assert_diff(h, Geom_TrimmedCurve(line, 0.0, 10.0), Geom_TrimmedCurve(line, 0.0, 20.0))


def test_GeomHash_CurveHasherTest_OffsetCurve_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    o1 = Geom_OffsetCurve(_line(), 5.0, gp_Dir(0.0, 0.0, 1.0))
    _assert_same(h, o1, o1.Copy())


def test_GeomHash_CurveHasherTest_OffsetCurve_DifferentOffset_DifferentHash():
    h = GeomHash_CurveHasher()
    line = _line()
    ref = gp_Dir(0.0, 0.0, 1.0)
    _assert_diff(h, Geom_OffsetCurve(line, 5.0, ref), Geom_OffsetCurve(line, 10.0, ref))


def test_GeomHash_CurveHasherTest_DifferentTypes_DifferentComparison():
    h = GeomHash_CurveHasher()
    assert not h(_line(), Geom_Circle(_zaxis(), 5.0))


def test_GeomHash_CurveHasherTest_NullCurves_HandledCorrectly():
    h = GeomHash_CurveHasher()
    line = _line()
    assert h(None) == 0
    assert h(None, None)
    assert not h(line, None)


def test_GeomHash_CurveHasherTest_SameObject_Equal():
    h = GeomHash_CurveHasher()
    line = _line()
    assert h(line, line)


def test_GeomHash_CurveHasherTest_BSplineCurve_Weighted_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(1.0, 2.0, 2.0, 1.0), _reals(0.0, 1.0), _ints(4, 4), 3)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_BSplineCurve_DifferentWeights_DifferentComparison():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(1.0, 2.0, 2.0, 1.0), _reals(0.0, 1.0), _ints(4, 4), 3)
    c2 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(1.0, 3.0, 2.0, 1.0), _reals(0.0, 1.0), _ints(4, 4), 3)
    assert not h(c1, c2)


def test_GeomHash_CurveHasherTest_BezierCurve_Weighted_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_BezierCurve(_pnts((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (2.0, 0.0, 0.0)), _reals(1.0, 2.0, 1.0))
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Circle_DifferentAxisOrientation_DifferentHash():
    h = GeomHash_CurveHasher()
    a2 = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
    _assert_diff(h, Geom_Circle(_zaxis(), 5.0), Geom_Circle(a2, 5.0))


def test_GeomHash_CurveHasherTest_Line_DifferentDirection_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, _line(), _line(d=(0.0, 1.0, 0.0)))


def test_GeomHash_CurveHasherTest_BSplineCurve_DifferentKnots_DifferentComparison():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(0.0, 1.0), _ints(4, 4), 3)
    c2 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(0.0, 2.0), _ints(4, 4), 3)
    assert not h(c1, c2)


def test_GeomHash_CurveHasherTest_BSplineCurve_QuadraticBezierEquivalent_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(
        _pnts((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (2.0, 0.0, 0.0)), _reals(0.0, 1.0), _ints(3, 3), 2
    )
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Line_Reversed_DifferentComparison():
    h = GeomHash_CurveHasher()
    l1 = _line()
    assert not h(l1, l1.Reversed())


def test_GeomHash_CurveHasherTest_BezierCurve_Reversed_DifferentComparison():
    h = GeomHash_CurveHasher()
    c1 = Geom_BezierCurve(_pnts((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (2.0, 0.0, 0.0)))
    assert not h(c1, c1.Reversed())


def test_GeomHash_CurveHasherTest_Circle_Translated_DifferentHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_Circle(_zaxis(), 5.0)
    c2 = c1.Copy()
    c2.Translate(gp_Vec(1.0, 0.0, 0.0))
    _assert_diff(h, c1, c2)


def test_GeomHash_CurveHasherTest_Circle_Scaled_DifferentHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_Circle(_zaxis(), 5.0)
    c2 = c1.Copy()
    c2.Scale(gp_Pnt(0.0, 0.0, 0.0), 2.0)
    _assert_diff(h, c1, c2)


def test_GeomHash_CurveHasherTest_BSplineCurve_HigherDegree_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    poles = _pnts(
        (0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 0.5, 0.0), (3.0, 1.5, 0.0), (4.0, 0.0, 0.0), (5.0, 1.0, 0.0)
    )
    c1 = Geom_BSplineCurve(poles, _reals(0.0, 1.0), _ints(6, 6), 5)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_BSplineCurve_DifferentDegree_DifferentComparison():
    h = GeomHash_CurveHasher()
    c1 = Geom_BSplineCurve(_pnts(*_CUBIC_POLES), _reals(0.0, 1.0), _ints(4, 4), 3)
    c2 = Geom_BSplineCurve(
        _pnts((0.0, 0.0, 0.0), (1.5, 1.0, 0.0), (3.0, 0.0, 0.0)), _reals(0.0, 1.0), _ints(3, 3), 2
    )
    assert not h(c1, c2)


def test_GeomHash_CurveHasherTest_BSplineCurve_LinearMultipleSpans_CopiedCurves_SameHash():
    h = GeomHash_CurveHasher()
    poles = _pnts((0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 0.0, 0.0), (3.0, 1.0, 0.0))
    c1 = Geom_BSplineCurve(poles, _reals(0.0, 1.0, 2.0, 3.0), _ints(2, 1, 1, 2), 1)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Ellipse_vs_Hyperbola_DifferentComparison():
    h = GeomHash_CurveHasher()
    assert not h(Geom_Ellipse(_zaxis(), 5.0, 3.0), Geom_Hyperbola(_zaxis(), 5.0, 3.0))


def test_GeomHash_CurveHasherTest_Circle_vs_Ellipse_DifferentComparison():
    h = GeomHash_CurveHasher()
    assert not h(Geom_Circle(_zaxis(), 5.0), Geom_Ellipse(_zaxis(), 5.0, 5.0))


def test_GeomHash_CurveHasherTest_TrimmedCurve_vs_BaseCurve_DifferentComparison():
    h = GeomHash_CurveHasher()
    line = _line()
    assert not h(line, Geom_TrimmedCurve(line, 0.0, 10.0))


def test_GeomHash_CurveHasherTest_Circle_VerySmallRadius_CopiedCircles_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_Circle(_zaxis(), 1e-10)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Circle_VeryLargeRadius_CopiedCircles_SameHash():
    h = GeomHash_CurveHasher()
    c1 = Geom_Circle(_zaxis(), 1e10)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_CurveHasherTest_Line_AtOrigin_vs_FarFromOrigin_DifferentHash():
    h = GeomHash_CurveHasher()
    _assert_diff(h, _line(), _line(p=(1e10, 1e10, 1e10)))
