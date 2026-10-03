# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGridEval_Hyperbola_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_Hyperbola
from nanocct.Geom2dGridEval import Geom2dGridEval_Hyperbola
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


def hyperbola(cx=0, cy=0):
    return Geom2d_Hyperbola(gp_Ax22d(gp_Pnt2d(cx, cy), gp_Dir2d(1, 0)), 3.0, 2.0)


def test_Geom2dGridEval_HyperbolaTest_BasicD0():
    h = hyperbola()
    ev = Geom2dGridEval_Hyperbola(h)
    assert ev.Geometry() is not None
    check_d0(ev, h, uniform(-2.0, 2.0, 11), 11)


def test_Geom2dGridEval_HyperbolaTest_AtOrigin():
    params = NCollection_Array1[float](1, 1)
    params.SetValue(1, 0.0)
    g = Geom2dGridEval_Hyperbola(hyperbola()).EvaluateGrid(params).Value(1)
    assert abs(g.X() - 3.0) <= TOL
    assert abs(g.Y()) <= TOL


def test_Geom2dGridEval_HyperbolaTest_D1():
    h = hyperbola(1, 2)
    check_dk(Geom2dGridEval_Hyperbola(h), h, uniform(-2.0, 2.0, 11), 11, 1)


def test_Geom2dGridEval_HyperbolaTest_D2():
    h = hyperbola()
    check_dk(Geom2dGridEval_Hyperbola(h), h, uniform(-2.0, 2.0, 11), 11, 2)


def test_Geom2dGridEval_HyperbolaTest_D3():
    h = hyperbola()
    check_dk(Geom2dGridEval_Hyperbola(h), h, uniform(-2.0, 2.0, 11), 11, 3)
