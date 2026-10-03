# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_SurfaceOfExtrusion_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import nanocct.GeomAbs as GeomAbs
from nanocct.Geom import Geom_Circle, Geom_Line, Geom_SurfaceOfLinearExtrusion
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomGridEval import GeomGridEval_Surface, GeomGridEval_SurfaceOfExtrusion
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-9


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _line_ext():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    return Geom_SurfaceOfLinearExtrusion(line, gp_Dir(0, 0, 1))


def _circle_ext(radius=5.0, direction=None):
    if direction is None:
        direction = gp_Dir(0, 0, 1)
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), radius)
    return Geom_SurfaceOfLinearExtrusion(circle, direction)


def _vnear(a, b):
    return (a - b).Magnitude() <= TOL


def _check_points(grid, surf, u, v):
    for i in range(1, u.Size() + 1):
        for j in range(1, v.Size() + 1):
            assert grid.Value(i, j).Distance(surf.Value(u.Value(i), v.Value(j))) <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_BasicEvaluation():
    ext = _line_ext()
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGrid(u, v)
    _check_points(grid, ext, u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p = grid.Value(i, j)
            assert abs(p.X() - u.Value(i)) <= TOL
            assert abs(p.Y()) <= TOL
            assert abs(p.Z() - v.Value(j)) <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_CircleBasisCurve():
    ext = _circle_ext()
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 10.0, 5)
    grid = ev.EvaluateGrid(u, v)
    _check_points(grid, ext, u, v)
    for i in range(1, 10):
        for j in range(1, 6):
            p = grid.Value(i, j)
            assert abs(math.hypot(p.X(), p.Y()) - 5.0) <= TOL
            assert abs(p.Z() - v.Value(j)) <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_DerivativeD1():
    ext = _line_ext()
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD1(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            ext.D1(u.Value(i), v.Value(j), p, d1u, d1v)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert abs(r.D1V.X()) <= TOL
            assert abs(r.D1V.Y()) <= TOL
            assert abs(r.D1V.Z() - 1.0) <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_DerivativeD2():
    ext = _circle_ext()
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD2(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
            ext.D2(u.Value(i), v.Value(j), p, d1u, d1v, d2u, d2v, d2uv)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert _vnear(r.D2U, d2u)
            assert _vnear(r.D2V, d2v)
            assert _vnear(r.D2UV, d2uv)
            assert r.D2V.Magnitude() <= TOL
            assert r.D2UV.Magnitude() <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_DerivativeD3():
    ext = _circle_ext()
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, math.pi, 5)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGridD3(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            vs = [gp_Vec() for _ in range(9)]
            ext.D3(u.Value(i), v.Value(j), p, *vs)
            _d1u, _d1v, _d2u, _d2v, _d2uv, d3u, d3v, d3uuv, d3uvv = vs
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D3U, d3u)
            assert _vnear(r.D3V, d3v)
            assert _vnear(r.D3UUV, d3uuv)
            assert _vnear(r.D3UVV, d3uvv)
            assert r.D3V.Magnitude() <= TOL
            assert r.D3UUV.Magnitude() <= TOL
            assert r.D3UVV.Magnitude() <= TOL


def test_GeomGridEval_SurfaceOfExtrusionTest_UnifiedDispatch():
    ext = _line_ext()
    ev = GeomGridEval_Surface(ext)
    assert ev.GetType() == GeomAbs.GeomAbs_SurfaceOfExtrusion
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 5.0, 5)
    _check_points(ev.EvaluateGrid(u, v), ext, u, v)


def test_GeomGridEval_SurfaceOfExtrusionTest_AdaptorDispatch():
    ext = _line_ext()
    adaptor = GeomAdaptor_Surface(ext)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_SurfaceOfExtrusion
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 5.0, 5)
    _check_points(ev.EvaluateGrid(u, v), ext, u, v)


def test_GeomGridEval_SurfaceOfExtrusionTest_NonAxisAlignedDirection():
    ext = _circle_ext(3.0, gp_Dir(1, 1, 1))
    ev = GeomGridEval_SurfaceOfExtrusion(ext)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-5.0, 5.0, 5)
    _check_points(ev.EvaluateGrid(u, v), ext, u, v)
