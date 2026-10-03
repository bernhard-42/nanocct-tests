# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGridEval_BezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_BezierCurve
from nanocct.Geom2dGridEval import Geom2dGridEval_BezierCurve
from nanocct.gp import gp_Ax22d, gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def uniform(first, last, n):
    a = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        a.SetValue(i, first + (i - 1) * step)
    return a


def check_d0(ev, curve, params, n):
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == n
    for i in range(1, n + 1):
        assert abs(grid.Value(i).Distance(curve.Value(params.Value(i)))) <= TOL


def check_dk(ev, curve, params, n, order):
    grid = (ev.EvaluateGridD1, ev.EvaluateGridD2, ev.EvaluateGridD3)[order - 1](params)
    for i in range(1, n + 1):
        p = gp_Pnt2d()
        vs = [gp_Vec2d() for _ in range(order)]
        (curve.D1, curve.D2, curve.D3)[order - 1](params.Value(i), p, *vs)
        g = grid.Value(i)
        assert abs(g.Point.Distance(p)) <= TOL
        for k, v in enumerate(vs, 1):
            assert abs((getattr(g, "D%d" % k) - v).Magnitude()) <= TOL


def bezier():
    p = NCollection_Array1[gp_Pnt2d](1, 4)
    for i, (x, y) in enumerate(((0, 0), (1, 2), (3, 2), (4, 0)), 1):
        p.SetValue(i, gp_Pnt2d(x, y))
    return Geom2d_BezierCurve(p)


def test_Geom2dGridEval_BezierCurveTest_BasicD0():
    b = bezier()
    ev = Geom2dGridEval_BezierCurve(b)
    assert ev.Geometry() is not None
    check_d0(ev, b, uniform(0.0, 1.0, 11), 11)


def test_Geom2dGridEval_BezierCurveTest_D1():
    b = bezier()
    check_dk(Geom2dGridEval_BezierCurve(b), b, uniform(0.0, 1.0, 11), 11, 1)


def test_Geom2dGridEval_BezierCurveTest_D2():
    b = bezier()
    check_dk(Geom2dGridEval_BezierCurve(b), b, uniform(0.0, 1.0, 11), 11, 2)


def test_Geom2dGridEval_BezierCurveTest_D3():
    b = bezier()
    check_dk(Geom2dGridEval_BezierCurve(b), b, uniform(0.0, 1.0, 11), 11, 3)


def test_Geom2dGridEval_BezierCurveTest_DN_BeyondDegree():
    grid = Geom2dGridEval_BezierCurve(bezier()).EvaluateGridDN(uniform(0.0, 1.0, 11), 4)
    for i in range(1, 12):
        assert abs(grid.Value(i).Magnitude()) <= TOL


def test_Geom2dGridEval_BezierCurveTest_RationalBezier():
    p = NCollection_Array1[gp_Pnt2d](1, 3)
    w = NCollection_Array1[float](1, 3)
    for i, (x, y) in enumerate(((1, 0), (1, 1), (0, 1)), 1):
        p.SetValue(i, gp_Pnt2d(x, y))
    for i, v in enumerate((1.0, 1.0 / math.sqrt(2.0), 1.0), 1):
        w.SetValue(i, v)
    b = Geom2d_BezierCurve(p, w)
    check_d0(Geom2dGridEval_BezierCurve(b), b, uniform(0.0, 1.0, 21), 21)
