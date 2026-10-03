# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dGridEval_Ellipse_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_Ellipse
from nanocct.Geom2dGridEval import Geom2dGridEval_Ellipse
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


def ellipse(cx=0, cy=0, a=3.0, b=2.0):
    return Geom2d_Ellipse(gp_Ax22d(gp_Pnt2d(cx, cy), gp_Dir2d(1, 0)), a, b)


def test_Geom2dGridEval_EllipseTest_BasicD0():
    e = ellipse()
    ev = Geom2dGridEval_Ellipse(e)
    assert ev.Geometry() is not None
    check_d0(ev, e, uniform(0.0, 2 * math.pi, 13), 13)


def test_Geom2dGridEval_EllipseTest_CardinalPoints():
    ev = Geom2dGridEval_Ellipse(ellipse())
    params = NCollection_Array1[float](1, 4)
    for i, u in enumerate((0.0, math.pi / 2, math.pi, 3 * math.pi / 2), 1):
        params.SetValue(i, u)
    grid = ev.EvaluateGrid(params)
    for i, (x, y) in enumerate(((3.0, 0.0), (0.0, 2.0), (-3.0, 0.0), (0.0, -2.0)), 1):
        assert abs(grid.Value(i).X() - x) <= TOL
        assert abs(grid.Value(i).Y() - y) <= TOL


def test_Geom2dGridEval_EllipseTest_D1():
    e = ellipse(1, 2, 5.0, 3.0)
    check_dk(Geom2dGridEval_Ellipse(e), e, uniform(0.0, 2 * math.pi, 13), 13, 1)


def test_Geom2dGridEval_EllipseTest_D2():
    e = ellipse()
    check_dk(Geom2dGridEval_Ellipse(e), e, uniform(0.0, 2 * math.pi, 9), 9, 2)


def test_Geom2dGridEval_EllipseTest_D3():
    e = ellipse()
    check_dk(Geom2dGridEval_Ellipse(e), e, uniform(0.0, 2 * math.pi, 9), 9, 3)
