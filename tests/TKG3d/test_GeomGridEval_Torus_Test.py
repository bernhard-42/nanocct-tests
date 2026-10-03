# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_Torus_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_ToroidalSurface
from nanocct.GeomGridEval import GeomGridEval_Torus
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _surface():
    return Geom_ToroidalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0, 2.0)


def test_GeomGridEval_TorusTest_GridBasicEvaluation():
    surf = _surface()
    ev = GeomGridEval_Torus(surf)
    assert ev.Geometry() is not None
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 9
    assert grid.ColLength() == 9
    for iu in range(1, 10):
        for iv in range(1, 9 + 1):
            expected = surf.Value(u.Value(iu), v.Value(iv))
            assert grid.Value(iu, iv).Distance(expected) <= TOL


def test_GeomGridEval_TorusTest_GridDerivativeD1():
    surf = _surface()
    ev = GeomGridEval_Torus(surf)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD1(u, v)
    for iu in range(1, 10):
        for iv in range(1, 9 + 1):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            surf.D1(u.Value(iu), v.Value(iv), p, d1u, d1v)
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL


def test_GeomGridEval_TorusTest_GridDerivativeD2():
    surf = _surface()
    ev = GeomGridEval_Torus(surf)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD2(u, v)
    for iu in range(1, 10):
        for iv in range(1, 9 + 1):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
            surf.D2(u.Value(iu), v.Value(iv), p, d1u, d1v, d2u, d2v, d2uv)
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL
            assert (r.D2U - d2u).Magnitude() <= TOL
            assert (r.D2V - d2v).Magnitude() <= TOL
            assert (r.D2UV - d2uv).Magnitude() <= TOL


def test_GeomGridEval_TorusTest_GridDerivativeD3():
    surf = _surface()
    ev = GeomGridEval_Torus(surf)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD3(u, v)
    for iu in range(1, 10):
        for iv in range(1, 9 + 1):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv = (gp_Vec() for _ in range(9))
            surf.D3(u.Value(iu), v.Value(iv), p, d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv)
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL
            assert (r.D2U - d2u).Magnitude() <= TOL
            assert (r.D2V - d2v).Magnitude() <= TOL
            assert (r.D2UV - d2uv).Magnitude() <= TOL
            assert (r.D3U - d3u).Magnitude() <= TOL
            assert (r.D3V - d3v).Magnitude() <= TOL
            assert (r.D3UUV - d3uuv).Magnitude() <= TOL
            assert (r.D3UVV - d3uvv).Magnitude() <= TOL


def test_GeomGridEval_TorusTest_GridDerivativeDN():
    surf = _surface()
    ev = GeomGridEval_Torus(surf)
    u = _uniform(0.0, 2 * math.pi, 5)
    v = _uniform(0.0, 2 * math.pi, 4)
    d4u = ev.EvaluateGridDN(u, v, 4, 0)
    for iu in range(1, 6):
        for iv in range(1, 5):
            expected = surf.DN(u.Value(iu), v.Value(iv), 4, 0)
            assert (d4u.Value(iu, iv) - expected).Magnitude() <= TOL
