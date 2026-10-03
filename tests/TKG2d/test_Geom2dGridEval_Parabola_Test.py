# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGridEval_Parabola_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_Parabola
from nanocct.Geom2dGridEval import Geom2dGridEval_Parabola
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


def parabola(cx=0, cy=0, f=1.0):
    return Geom2d_Parabola(gp_Ax22d(gp_Pnt2d(cx, cy), gp_Dir2d(1, 0)), f)


def test_Geom2dGridEval_ParabolaTest_BasicD0():
    p = parabola()
    ev = Geom2dGridEval_Parabola(p)
    assert ev.Geometry() is not None
    check_d0(ev, p, uniform(-3.0, 3.0, 13), 13)


def test_Geom2dGridEval_ParabolaTest_AtOrigin():
    params = NCollection_Array1[float](1, 1)
    params.SetValue(1, 0.0)
    g = Geom2dGridEval_Parabola(parabola()).EvaluateGrid(params).Value(1)
    assert abs(g.X()) <= TOL
    assert abs(g.Y()) <= TOL


def test_Geom2dGridEval_ParabolaTest_D1():
    p = parabola(1, 2, 2.0)
    check_dk(Geom2dGridEval_Parabola(p), p, uniform(-3.0, 3.0, 13), 13, 1)


def test_Geom2dGridEval_ParabolaTest_D2():
    p = parabola()
    check_dk(Geom2dGridEval_Parabola(p), p, uniform(-3.0, 3.0, 13), 13, 2)


def test_Geom2dGridEval_ParabolaTest_D3():
    p = parabola()
    check_dk(Geom2dGridEval_Parabola(p), p, uniform(-3.0, 3.0, 13), 13, 3)


def test_Geom2dGridEval_ParabolaTest_DN_HighOrder():
    grid = Geom2dGridEval_Parabola(parabola()).EvaluateGridDN(uniform(-3.0, 3.0, 7), 3)
    for i in range(1, 8):
        assert abs(grid.Value(i).Magnitude()) <= TOL
