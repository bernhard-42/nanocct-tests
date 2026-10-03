# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_SurfaceOfRevolution_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import nanocct.GeomAbs as GeomAbs
from nanocct.Geom import Geom_Circle, Geom_Line, Geom_SurfaceOfRevolution
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomGridEval import GeomGridEval_Surface, GeomGridEval_SurfaceOfRevolution
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-9


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _z_axis():
    return gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _line_rev():
    line = Geom_Line(gp_Pnt(5.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    return Geom_SurfaceOfRevolution(line, _z_axis())


def _vnear(a, b):
    return (a - b).Magnitude() <= TOL


def _check_points(grid, surf, u, v):
    for i in range(1, u.Size() + 1):
        for j in range(1, v.Size() + 1):
            assert grid.Value(i, j).Distance(surf.Value(u.Value(i), v.Value(j))) <= TOL


def test_GeomGridEval_SurfaceOfRevolutionTest_BasicEvaluation():
    rev = _line_rev()
    ev = GeomGridEval_SurfaceOfRevolution(rev)
    u = _uniform(0.0, math.pi, 9)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGrid(u, v)
    _check_points(grid, rev, u, v)
    for i in range(1, 10):
        for j in range(1, 6):
            p = grid.Value(i, j)
            assert abs(math.hypot(p.X(), p.Y()) - 5.0) <= TOL


def test_GeomGridEval_SurfaceOfRevolutionTest_CircleMeridian():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(10.0, 0.0, 0.0), gp_Dir(0, 1, 0), gp_Dir(1, 0, 0)), 3.0)
    rev = Geom_SurfaceOfRevolution(circle, _z_axis())
    ev = GeomGridEval_SurfaceOfRevolution(rev)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    _check_points(ev.EvaluateGrid(u, v), rev, u, v)


def test_GeomGridEval_SurfaceOfRevolutionTest_DerivativeD1():
    rev = _line_rev()
    ev = GeomGridEval_SurfaceOfRevolution(rev)
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD1(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            rev.D1(u.Value(i), v.Value(j), p, d1u, d1v)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)


def test_GeomGridEval_SurfaceOfRevolutionTest_DerivativeD2():
    rev = _line_rev()
    ev = GeomGridEval_SurfaceOfRevolution(rev)
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD2(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
            rev.D2(u.Value(i), v.Value(j), p, d1u, d1v, d2u, d2v, d2uv)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert _vnear(r.D2U, d2u)
            assert _vnear(r.D2V, d2v)
            assert _vnear(r.D2UV, d2uv)


def test_GeomGridEval_SurfaceOfRevolutionTest_DerivativeD3():
    rev = _line_rev()
    ev = GeomGridEval_SurfaceOfRevolution(rev)
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD3(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            vs = [gp_Vec() for _ in range(9)]
            rev.D3(u.Value(i), v.Value(j), p, *vs)
            _d1u, _d1v, _d2u, _d2v, _d2uv, d3u, d3v, d3uuv, d3uvv = vs
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D3U, d3u)
            assert _vnear(r.D3V, d3v)
            assert _vnear(r.D3UUV, d3uuv)
            assert _vnear(r.D3UVV, d3uvv)


def test_GeomGridEval_SurfaceOfRevolutionTest_UnifiedDispatch():
    rev = _line_rev()
    ev = GeomGridEval_Surface(rev)
    assert ev.GetType() == GeomAbs.GeomAbs_SurfaceOfRevolution
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    _check_points(ev.EvaluateGrid(u, v), rev, u, v)


def test_GeomGridEval_SurfaceOfRevolutionTest_AdaptorDispatch():
    rev = _line_rev()
    adaptor = GeomAdaptor_Surface(rev)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_SurfaceOfRevolution
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    _check_points(ev.EvaluateGrid(u, v), rev, u, v)
