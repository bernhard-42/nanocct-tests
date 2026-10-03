# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import (
    Geom_BezierCurve,
    Geom_BSplineCurve,
    Geom_Circle,
    Geom_Ellipse,
    Geom_Hyperbola,
    Geom_Line,
    Geom_OffsetCurve,
    Geom_Parabola,
)
from nanocct.GeomAbs import GeomAbs_CurveType
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomGridEval import (
    GeomGridEval_BSplineCurve,
    GeomGridEval_Circle,
    GeomGridEval_Curve,
    GeomGridEval_Line,
    GeomGridEval_OtherCurve,
)
from nanocct.gp import gp, gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10
CT = GeomAbs_CurveType


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _floats(values):
    arr = NCollection_Array1[float](1, len(values))
    for i, v in enumerate(values, start=1):
        arr.SetValue(i, v)
    return arr


def _ints(values):
    arr = NCollection_Array1[int](1, len(values))
    for i, v in enumerate(values, start=1):
        arr.SetValue(i, v)
    return arr


def _pnts(points):
    arr = NCollection_Array1[gp_Pnt](1, len(points))
    for i, p in enumerate(points, start=1):
        arr.SetValue(i, gp_Pnt(*p))
    return arr


def _simple_bspline():
    poles = _pnts([(0, 0, 0), (1, 2, 0), (3, 2, 0), (4, 0, 0)])
    return Geom_BSplineCurve(poles, _floats([0.0, 1.0]), _ints([4, 4]), 3)


def _rational_bspline():
    poles = _pnts([(1, 0, 0), (1, 1, 0), (0, 1, 0), (-1, 1, 0)])
    s = 1.0 / math.sqrt(2.0)
    weights = _floats([1.0, s, 1.0, s])
    return Geom_BSplineCurve(poles, weights, _floats([0.0, 1.0]), _ints([4, 4]), 3)


def _multi_span_bspline():
    poles = _pnts([(0, 0, 0), (1, 2, 0), (2, 2, 0), (3, 0, 0), (4, -1, 0), (5, 0, 0)])
    return Geom_BSplineCurve(poles, _floats([0.0, 0.5, 1.0]), _ints([4, 2, 4]), 3)


def _circle(radius=2.0):
    return Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), radius)


def _check_points(grid, geom, params):
    for i in range(1, params.Size() + 1):
        assert grid.Value(i).Distance(geom.Value(params.Value(i))) <= TOL


def _check_d1(grid, curve, params):
    for i in range(1, params.Size() + 1):
        p, d1 = gp_Pnt(), gp_Vec()
        curve.D1(params.Value(i), p, d1)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL


def _check_d2(grid, curve, params):
    for i in range(1, params.Size() + 1):
        p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
        curve.D2(params.Value(i), p, d1, d2)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL
        assert (r.D2 - d2).Magnitude() <= TOL


def _check_d3(grid, curve, params):
    for i in range(1, params.Size() + 1):
        p, d1, d2, d3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        curve.D3(params.Value(i), p, d1, d2, d3)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL
        assert (r.D2 - d2).Magnitude() <= TOL
        assert (r.D3 - d3).Magnitude() <= TOL


def _check_dn(ev, curve, params, order):
    grid = ev.EvaluateGridDN(params, order)
    for i in range(1, params.Size() + 1):
        assert (grid.Value(i) - curve.DN(params.Value(i), order)).Magnitude() <= TOL


# GeomGridEval_Line


def test_GeomGridEval_LineTest_BasicEvaluation():
    ev = GeomGridEval_Line(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    assert ev.Geometry() is not None
    params = _uniform(0.0, 10.0, 11)
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == 11
    for i in range(1, 12):
        t = params.Value(i)
        assert abs(grid.Value(i).X() - t) <= TOL
        assert abs(grid.Value(i).Y()) <= TOL
        assert abs(grid.Value(i).Z()) <= TOL


def test_GeomGridEval_LineTest_NonOriginLine():
    ev = GeomGridEval_Line(Geom_Line(gp_Pnt(1, 2, 3), gp_Dir(1, 1, 1)))
    grid = ev.EvaluateGrid(_uniform(0.0, 5.0, 6))
    assert grid.Value(1).Distance(gp_Pnt(1, 2, 3)) <= TOL
    d = 5.0 / math.sqrt(3.0)
    assert grid.Value(6).Distance(gp_Pnt(1 + d, 2 + d, 3 + d)) <= TOL


# GeomGridEval_Circle


def test_GeomGridEval_CircleTest_BasicEvaluation():
    ev = GeomGridEval_Circle(_circle())
    assert ev.Geometry() is not None
    params = _floats([0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi])
    grid = ev.EvaluateGrid(params)
    expected = [(2.0, 0.0), (0.0, 2.0), (-2.0, 0.0), (0.0, -2.0), (2.0, 0.0)]
    for i, (x, y) in enumerate(expected, start=1):
        assert abs(grid.Value(i).X() - x) <= TOL
        assert abs(grid.Value(i).Y() - y) <= TOL


def test_GeomGridEval_CircleTest_NonStandardCircle():
    ev = GeomGridEval_Circle(Geom_Circle(gp_Ax2(gp_Pnt(1, 0, 0), gp_Dir(1, 0, 0)), 3.0))
    grid = ev.EvaluateGrid(_uniform(0.0, 2 * math.pi, 9))
    center = gp_Pnt(1, 0, 0)
    for i in range(1, grid.Length() + 1):
        assert abs(grid.Value(i).Distance(center) - 3.0) <= TOL
        assert abs(grid.Value(i).X() - 1.0) <= TOL


# GeomGridEval_BSplineCurve


def test_GeomGridEval_BSplineCurveTest_BasicEvaluation():
    curve = _simple_bspline()
    ev = GeomGridEval_BSplineCurve(curve)
    assert ev.Geometry() is not None
    params = _uniform(0.0, 1.0, 11)
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == 11
    _check_points(grid, curve, params)


def test_GeomGridEval_BSplineCurveTest_EndpointsMatch():
    ev = GeomGridEval_BSplineCurve(_simple_bspline())
    grid = ev.EvaluateGrid(_floats([0.0, 1.0]))
    assert grid.Value(1).Distance(gp_Pnt(0, 0, 0)) <= TOL
    assert grid.Value(2).Distance(gp_Pnt(4, 0, 0)) <= TOL


# GeomGridEval_OtherCurve


def test_GeomGridEval_OtherCurveTest_EllipseFallback():
    ellipse = Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0, 2.0)
    adaptor = GeomAdaptor_Curve(ellipse)
    ev = GeomGridEval_OtherCurve(adaptor)
    params = _uniform(0.0, 2 * math.pi, 9)
    _check_points(ev.EvaluateGrid(params), ellipse, params)


# GeomGridEval_Curve (unified dispatcher)


def _dispatch(geom, expected_type, params):
    adaptor = GeomAdaptor_Curve(geom)
    ev = GeomGridEval_Curve(adaptor)
    assert ev.GetType() == expected_type
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == params.Size()
    _check_points(grid, geom, params)


def test_GeomGridEval_CurveTest_LineDispatch():
    _dispatch(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), CT.GeomAbs_Line, _uniform(0.0, 10.0, 11))


def test_GeomGridEval_CurveTest_CircleDispatch():
    _dispatch(_circle(), CT.GeomAbs_Circle, _uniform(0.0, 2 * math.pi, 17))


def test_GeomGridEval_CurveTest_BSplineDispatch():
    _dispatch(_simple_bspline(), CT.GeomAbs_BSplineCurve, _uniform(0.0, 1.0, 21))


def test_GeomGridEval_CurveTest_EllipseDispatch():
    ellipse = Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0, 2.0)
    _dispatch(ellipse, CT.GeomAbs_Ellipse, _uniform(0.0, 2 * math.pi, 13))


def test_GeomGridEval_CurveTest_HyperbolaDispatch():
    hypr = Geom_Hyperbola(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0, 2.0)
    _dispatch(hypr, CT.GeomAbs_Hyperbola, _uniform(-2.0, 2.0, 11))


def test_GeomGridEval_CurveTest_ParabolaDispatch():
    parab = Geom_Parabola(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    _dispatch(parab, CT.GeomAbs_Parabola, _uniform(-2.0, 2.0, 11))


def test_GeomGridEval_CurveTest_BezierCurveDispatch():
    bez = Geom_BezierCurve(_pnts([(0, 0, 0), (1, 2, 0), (3, 2, 0), (4, 0, 0)]))
    _dispatch(bez, CT.GeomAbs_BezierCurve, _uniform(0.0, 1.0, 11))


def test_GeomGridEval_CurveTest_OffsetCurveFallbackDispatch():
    line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    offset = Geom_OffsetCurve(line, 1.0, gp.DZ_s())
    _dispatch(offset, CT.GeomAbs_OffsetCurve, _uniform(0.0, 5.0, 6))


def test_GeomGridEval_CurveTest_DirectHandleInit():
    ev = GeomGridEval_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    assert ev.GetType() == CT.GeomAbs_Line
    grid = ev.EvaluateGrid(_uniform(0.0, 10.0, 11))
    assert grid.Size() == 11
    assert abs(grid.Value(1).X()) <= TOL


def test_GeomGridEval_CurveTest_EmptyParams():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    ev = GeomGridEval_Curve(adaptor)
    grid = ev.EvaluateGrid(NCollection_Array1[float]())
    assert grid.IsEmpty()


# Additional B-spline tests


def test_GeomGridEval_BSplineCurveTest_RationalBSpline():
    curve = _rational_bspline()
    params = _uniform(0.0, 1.0, 21)
    grid = GeomGridEval_BSplineCurve(curve).EvaluateGrid(params)
    assert grid.Size() == 21
    _check_points(grid, curve, params)


def test_GeomGridEval_BSplineCurveTest_MultiSpanBSpline():
    curve = _multi_span_bspline()
    params = _uniform(0.0, 1.0, 31)
    _check_points(GeomGridEval_BSplineCurve(curve).EvaluateGrid(params), curve, params)


def test_GeomGridEval_BSplineCurveTest_HighDegree():
    poles = _pnts([(0, 0, 0), (1, 3, 0), (2, 1, 0), (3, 4, 0), (4, 2, 0), (5, 0, 0)])
    curve = Geom_BSplineCurve(poles, _floats([0.0, 1.0]), _ints([6, 6]), 5)
    params = _uniform(0.0, 1.0, 51)
    _check_points(GeomGridEval_BSplineCurve(curve).EvaluateGrid(params), curve, params)


# Derivatives


def test_GeomGridEval_LineTest_DerivativeD1():
    ev = GeomGridEval_Line(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 2, 3)))
    grid = ev.EvaluateGridD1(_uniform(0.0, 5.0, 6))
    assert grid.Size() == 6
    direction = gp_Dir(1, 2, 3)
    for i in range(1, 7):
        d1 = grid.Value(i).D1
        assert abs(d1.X() - direction.X()) <= TOL
        assert abs(d1.Y() - direction.Y()) <= TOL
        assert abs(d1.Z() - direction.Z()) <= TOL


def test_GeomGridEval_LineTest_DerivativeD2D3():
    ev = GeomGridEval_Line(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    params = _uniform(0.0, 5.0, 6)
    grid_d2 = ev.EvaluateGridD2(params)
    grid_d3 = ev.EvaluateGridD3(params)
    for i in range(1, 7):
        assert grid_d2.Value(i).D2.Magnitude() <= TOL
        assert grid_d3.Value(i).D2.Magnitude() <= TOL
        assert grid_d3.Value(i).D3.Magnitude() <= TOL


def test_GeomGridEval_CircleTest_DerivativeD1():
    circle = _circle()
    params = _floats([0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi])
    _check_d1(GeomGridEval_Circle(circle).EvaluateGridD1(params), circle, params)


def test_GeomGridEval_CircleTest_DerivativeD2():
    circle = _circle()
    params = _uniform(0.0, 2 * math.pi, 9)
    _check_d2(GeomGridEval_Circle(circle).EvaluateGridD2(params), circle, params)


def test_GeomGridEval_BSplineCurveTest_DerivativeD1():
    curve = _simple_bspline()
    params = _uniform(0.0, 1.0, 11)
    _check_d1(GeomGridEval_BSplineCurve(curve).EvaluateGridD1(params), curve, params)


def test_GeomGridEval_BSplineCurveTest_DerivativeD2():
    curve = _simple_bspline()
    params = _uniform(0.0, 1.0, 11)
    _check_d2(GeomGridEval_BSplineCurve(curve).EvaluateGridD2(params), curve, params)


def test_GeomGridEval_BSplineCurveTest_DerivativeD3():
    curve = _simple_bspline()
    params = _uniform(0.0, 1.0, 11)
    _check_d3(GeomGridEval_BSplineCurve(curve).EvaluateGridD3(params), curve, params)


def test_GeomGridEval_CurveTest_UnifiedDerivativeD1():
    circle = _circle()
    adaptor = GeomAdaptor_Curve(circle)
    params = _uniform(0.0, 2 * math.pi, 9)
    _check_d1(GeomGridEval_Curve(adaptor).EvaluateGridD1(params), circle, params)


def test_GeomGridEval_CurveTest_UnifiedDerivativeD2():
    curve = _simple_bspline()
    adaptor = GeomAdaptor_Curve(curve)
    params = _uniform(0.0, 1.0, 11)
    _check_d2(GeomGridEval_Curve(adaptor).EvaluateGridD2(params), curve, params)


def test_GeomGridEval_CircleTest_DerivativeD3():
    circle = _circle()
    params = _uniform(0.0, 2 * math.pi, 9)
    _check_d3(GeomGridEval_Circle(circle).EvaluateGridD3(params), circle, params)


def test_GeomGridEval_OffsetCurveTest_DerivativeD3():
    offset = Geom_OffsetCurve(_circle(), 0.5, gp.DZ_s())
    adaptor = GeomAdaptor_Curve(offset)
    ev = GeomGridEval_OtherCurve(adaptor)
    params = _uniform(0.0, 2 * math.pi, 9)
    _check_d3(ev.EvaluateGridD3(params), adaptor, params)


def test_GeomGridEval_CurveTest_OffsetCurveDerivativeD3():
    line = Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    offset = Geom_OffsetCurve(line, 1.0, gp.DZ_s())
    adaptor = GeomAdaptor_Curve(offset)
    ev = GeomGridEval_Curve(adaptor)
    assert ev.GetType() == CT.GeomAbs_OffsetCurve
    params = _uniform(0.0, 5.0, 6)
    _check_d3(ev.EvaluateGridD3(params), adaptor, params)


def test_GeomGridEval_CurveTest_UnifiedDerivativeD3():
    curve = _simple_bspline()
    adaptor = GeomAdaptor_Curve(curve)
    params = _uniform(0.0, 1.0, 11)
    _check_d3(GeomGridEval_Curve(adaptor).EvaluateGridD3(params), curve, params)


# B-spline DN


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_Order1():
    curve = _simple_bspline()
    _check_dn(GeomGridEval_BSplineCurve(curve), curve, _uniform(0.0, 1.0, 11), 1)


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_Order2():
    curve = _simple_bspline()
    _check_dn(GeomGridEval_BSplineCurve(curve), curve, _uniform(0.0, 1.0, 11), 2)


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_Order3():
    curve = _simple_bspline()
    _check_dn(GeomGridEval_BSplineCurve(curve), curve, _uniform(0.0, 1.0, 11), 3)


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_BeyondDegree():
    grid = GeomGridEval_BSplineCurve(_simple_bspline()).EvaluateGridDN(_uniform(0.0, 1.0, 11), 4)
    for i in range(1, 12):
        assert grid.Value(i).Magnitude() <= TOL


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_RationalCurve():
    curve = _rational_bspline()
    ev = GeomGridEval_BSplineCurve(curve)
    params = _uniform(0.0, 1.0, 21)
    for order in (1, 2, 3):
        _check_dn(ev, curve, params, order)


def test_GeomGridEval_BSplineCurveTest_DerivativeDN_MultiSpan():
    curve = _multi_span_bspline()
    ev = GeomGridEval_BSplineCurve(curve)
    params = _uniform(0.0, 1.0, 31)
    for order in (1, 2, 3):
        _check_dn(ev, curve, params, order)
