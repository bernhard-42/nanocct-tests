# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGridEval_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GeomAbs import (
    GeomAbs_BezierCurve,
    GeomAbs_BSplineCurve,
    GeomAbs_Circle,
    GeomAbs_Ellipse,
    GeomAbs_Hyperbola,
    GeomAbs_Line,
    GeomAbs_OffsetCurve,
    GeomAbs_Parabola,
)
from nanocct.Geom2d import (
    Geom2d_BezierCurve,
    Geom2d_BSplineCurve,
    Geom2d_Circle,
    Geom2d_Ellipse,
    Geom2d_Hyperbola,
    Geom2d_Line,
    Geom2d_OffsetCurve,
    Geom2d_Parabola,
)
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dGridEval import (
    Geom2dGridEval_BSplineCurve,
    Geom2dGridEval_Circle,
    Geom2dGridEval_Curve,
    Geom2dGridEval_Line,
)
from nanocct.gp import gp_Ax22d, gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def uniform(first, last, n):
    a = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        a.SetValue(i, first + (i - 1) * step)
    return a


def arr_pnt(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a.SetValue(i, gp_Pnt2d(x, y))
    return a


def arr(typ, *vals):
    a = NCollection_Array1[typ](1, len(vals))
    for i, v in enumerate(vals, 1):
        a.SetValue(i, v)
    return a


def simple_bspline():
    return Geom2d_BSplineCurve(arr_pnt((0, 0), (1, 2), (3, 2), (4, 0)), arr(float, 0.0, 1.0), arr(int, 4, 4), 3)


def circle(r=2.0):
    return Geom2d_Circle(gp_Ax22d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), r)


def check_d0(ev, curve, params):
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == params.Size()
    for i in range(1, params.Size() + 1):
        assert abs(grid.Value(i).Distance(curve.Value(params.Value(i)))) <= TOL


def check_dk(ev, curve, params, order):
    grid = (ev.EvaluateGridD1, ev.EvaluateGridD2, ev.EvaluateGridD3)[order - 1](params)
    for i in range(1, params.Size() + 1):
        p = gp_Pnt2d()
        vs = [gp_Vec2d() for _ in range(order)]
        (curve.D1, curve.D2, curve.D3)[order - 1](params.Value(i), p, *vs)
        g = grid.Value(i)
        assert abs(g.Point.Distance(p)) <= TOL
        for k, v in enumerate(vs, 1):
            assert abs((getattr(g, "D%d" % k) - v).Magnitude()) <= TOL


def test_Geom2dGridEval_LineTest_BasicEvaluation():
    ev = Geom2dGridEval_Line(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)))
    assert ev.Geometry() is not None
    params = uniform(0.0, 10.0, 11)
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == 11
    for i in range(1, 12):
        assert abs(grid.Value(i).X() - params.Value(i)) <= TOL
        assert abs(grid.Value(i).Y()) <= TOL


def test_Geom2dGridEval_LineTest_NonOriginLine():
    grid = Geom2dGridEval_Line(Geom2d_Line(gp_Pnt2d(1, 2), gp_Dir2d(1, 1))).EvaluateGrid(uniform(0.0, 5.0, 6))
    assert abs(grid.Value(1).Distance(gp_Pnt2d(1, 2))) <= TOL
    d = 5.0 / math.sqrt(2.0)
    assert abs(grid.Value(6).Distance(gp_Pnt2d(1 + d, 2 + d))) <= TOL


def test_Geom2dGridEval_LineTest_DerivativeD1():
    grid = Geom2dGridEval_Line(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 2))).EvaluateGridD1(uniform(0.0, 5.0, 6))
    assert grid.Size() == 6
    d = gp_Dir2d(1, 2)
    for i in range(1, 7):
        assert abs(grid.Value(i).D1.X() - d.X()) <= TOL
        assert abs(grid.Value(i).D1.Y() - d.Y()) <= TOL


def test_Geom2dGridEval_LineTest_DerivativeD2D3():
    ev = Geom2dGridEval_Line(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)))
    params = uniform(0.0, 5.0, 6)
    g2, g3 = ev.EvaluateGridD2(params), ev.EvaluateGridD3(params)
    for i in range(1, 7):
        assert abs(g2.Value(i).D2.Magnitude()) <= TOL
        assert abs(g3.Value(i).D2.Magnitude()) <= TOL
        assert abs(g3.Value(i).D3.Magnitude()) <= TOL


def test_Geom2dGridEval_CircleTest_BasicEvaluation():
    ev = Geom2dGridEval_Circle(circle())
    assert ev.Geometry() is not None
    params = arr(float, 0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi)
    grid = ev.EvaluateGrid(params)
    for i, (x, y) in enumerate(((2.0, 0.0), (0.0, 2.0), (-2.0, 0.0), (0.0, -2.0), (2.0, 0.0)), 1):
        assert abs(grid.Value(i).X() - x) <= TOL
        assert abs(grid.Value(i).Y() - y) <= TOL


def test_Geom2dGridEval_CircleTest_DerivativeD1():
    c = circle()
    check_dk(Geom2dGridEval_Circle(c), c, uniform(0.0, 2 * math.pi, 9), 1)


def test_Geom2dGridEval_CircleTest_DerivativeD2():
    c = circle()
    check_dk(Geom2dGridEval_Circle(c), c, uniform(0.0, 2 * math.pi, 9), 2)


def test_Geom2dGridEval_CircleTest_DerivativeD3():
    c = circle()
    check_dk(Geom2dGridEval_Circle(c), c, uniform(0.0, 2 * math.pi, 9), 3)


def test_Geom2dGridEval_BSplineCurveTest_BasicEvaluation():
    c = simple_bspline()
    ev = Geom2dGridEval_BSplineCurve(c)
    assert ev.Geometry() is not None
    check_d0(ev, c, uniform(0.0, 1.0, 11))


def test_Geom2dGridEval_BSplineCurveTest_EndpointsMatch():
    grid = Geom2dGridEval_BSplineCurve(simple_bspline()).EvaluateGrid(arr(float, 0.0, 1.0))
    assert abs(grid.Value(1).Distance(gp_Pnt2d(0, 0))) <= TOL
    assert abs(grid.Value(2).Distance(gp_Pnt2d(4, 0))) <= TOL


def test_Geom2dGridEval_BSplineCurveTest_DerivativeD1():
    c = simple_bspline()
    check_dk(Geom2dGridEval_BSplineCurve(c), c, uniform(0.0, 1.0, 11), 1)


def test_Geom2dGridEval_BSplineCurveTest_DerivativeD2():
    c = simple_bspline()
    check_dk(Geom2dGridEval_BSplineCurve(c), c, uniform(0.0, 1.0, 11), 2)


def test_Geom2dGridEval_BSplineCurveTest_DerivativeD3():
    c = simple_bspline()
    check_dk(Geom2dGridEval_BSplineCurve(c), c, uniform(0.0, 1.0, 11), 3)


def test_Geom2dGridEval_BSplineCurveTest_DerivativeDN_BeyondDegree():
    grid = Geom2dGridEval_BSplineCurve(simple_bspline()).EvaluateGridDN(uniform(0.0, 1.0, 11), 4)
    for i in range(1, 12):
        assert abs(grid.Value(i).Magnitude()) <= TOL


def test_Geom2dGridEval_BSplineCurveTest_MultiSpanBSpline():
    c = Geom2d_BSplineCurve(
        arr_pnt((0, 0), (1, 2), (2, 2), (3, 0), (4, -1), (5, 0)), arr(float, 0.0, 0.5, 1.0), arr(int, 4, 2, 4), 3
    )
    check_d0(Geom2dGridEval_BSplineCurve(c), c, uniform(0.0, 1.0, 31))


def test_Geom2dGridEval_CurveTest_LineDispatch():
    l = Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0))
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(l))
    assert ev.GetType() == GeomAbs_Line
    check_d0(ev, l, uniform(0.0, 10.0, 11))


def test_Geom2dGridEval_CurveTest_CircleDispatch():
    c = circle()
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(c))
    assert ev.GetType() == GeomAbs_Circle
    check_d0(ev, c, uniform(0.0, 2 * math.pi, 17))


def test_Geom2dGridEval_CurveTest_EllipseDispatch():
    e = Geom2d_Ellipse(gp_Ax22d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 3.0, 2.0)
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(e))
    assert ev.GetType() == GeomAbs_Ellipse
    check_d0(ev, e, uniform(0.0, 2 * math.pi, 13))


def test_Geom2dGridEval_CurveTest_HyperbolaDispatch():
    h = Geom2d_Hyperbola(gp_Ax22d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 3.0, 2.0)
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(h))
    assert ev.GetType() == GeomAbs_Hyperbola
    check_d0(ev, h, uniform(-2.0, 2.0, 11))


def test_Geom2dGridEval_CurveTest_ParabolaDispatch():
    p = Geom2d_Parabola(gp_Ax22d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 1.0)
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(p))
    assert ev.GetType() == GeomAbs_Parabola
    check_d0(ev, p, uniform(-2.0, 2.0, 11))


def test_Geom2dGridEval_CurveTest_BSplineDispatch():
    c = simple_bspline()
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(c))
    assert ev.GetType() == GeomAbs_BSplineCurve
    check_d0(ev, c, uniform(0.0, 1.0, 21))


def test_Geom2dGridEval_CurveTest_BezierCurveDispatch():
    b = Geom2d_BezierCurve(arr_pnt((0, 0), (1, 2), (3, 2), (4, 0)))
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(b))
    assert ev.GetType() == GeomAbs_BezierCurve
    check_d0(ev, b, uniform(0.0, 1.0, 11))


def test_Geom2dGridEval_CurveTest_OffsetCurveDispatch():
    off = Geom2d_OffsetCurve(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 1.0)
    ev = Geom2dGridEval_Curve(off)
    assert ev.GetType() == GeomAbs_OffsetCurve
    check_d0(ev, off, uniform(0.0, 5.0, 6))


def test_Geom2dGridEval_CurveTest_DirectHandleInit():
    ev = Geom2dGridEval_Curve(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)))
    assert ev.GetType() == GeomAbs_Line
    grid = ev.EvaluateGrid(uniform(0.0, 10.0, 11))
    assert grid.Size() == 11
    assert abs(grid.Value(1).X()) <= TOL


def test_Geom2dGridEval_CurveTest_EmptyParams():
    ev = Geom2dGridEval_Curve(Geom2dAdaptor_Curve(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(1, 0))))
    assert ev.EvaluateGrid(NCollection_Array1[float]()).IsEmpty() is True


def test_Geom2dGridEval_CurveTest_UnifiedDerivativeD1():
    c = circle()
    check_dk(Geom2dGridEval_Curve(Geom2dAdaptor_Curve(c)), c, uniform(0.0, 2 * math.pi, 9), 1)


def test_Geom2dGridEval_CurveTest_UnifiedDerivativeD2():
    c = simple_bspline()
    check_dk(Geom2dGridEval_Curve(Geom2dAdaptor_Curve(c)), c, uniform(0.0, 1.0, 11), 2)


def test_Geom2dGridEval_CurveTest_UnifiedDerivativeD3():
    c = simple_bspline()
    check_dk(Geom2dGridEval_Curve(Geom2dAdaptor_Curve(c)), c, uniform(0.0, 1.0, 11), 3)


def test_Geom2dGridEval_CurveTest_OffsetCurveDerivativeD3():
    off = Geom2d_OffsetCurve(circle(), 0.5)
    ev = Geom2dGridEval_Curve(off)
    assert ev.GetType() == GeomAbs_OffsetCurve
    check_dk(ev, off, uniform(0.0, 2 * math.pi, 9), 3)
