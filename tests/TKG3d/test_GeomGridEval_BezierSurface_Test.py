# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_BezierSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_BezierSurface
from nanocct.GeomGridEval import GeomGridEval_BezierSurface
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2

TOL = 1e-10


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _single(value):
    arr = NCollection_Array1[float](1, 1)
    arr.SetValue(1, value)
    return arr


def _bilinear(corner_z):
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(2, 1, gp_Pnt(1, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
    poles.SetValue(2, 2, gp_Pnt(1, 1, corner_z))
    return poles


def _rational_bilinear():
    weights = NCollection_Array2[float](1, 2, 1, 2)
    weights.SetValue(1, 1, 1.0)
    weights.SetValue(2, 1, 1.0)
    weights.SetValue(1, 2, 1.0)
    weights.SetValue(2, 2, 2.0)
    return Geom_BezierSurface(_bilinear(1), weights)


def _sin_ij():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles.SetValue(i, j, gp_Pnt(i, j, math.sin(i + j)))
    return Geom_BezierSurface(poles)


def _sin_half(n):
    poles = NCollection_Array2[gp_Pnt](1, n, 1, n)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            poles.SetValue(i, j, gp_Pnt(i - 1, j - 1, math.sin((i - 1) * 0.5 + (j - 1) * 0.5)))
    return poles


def test_GeomGridEval_BezierSurfaceTest_BasicEvaluation():
    bez = Geom_BezierSurface(_bilinear(0))
    ev = GeomGridEval_BezierSurface(bez)
    assert ev.Geometry() is not None
    params = _uniform(0.0, 1.0, 3)
    grid = ev.EvaluateGrid(params, params)
    assert grid.RowLength() == 3
    assert grid.ColLength() == 3
    for i in range(1, 4):
        for j in range(1, 4):
            expected = bez.Value(params.Value(i), params.Value(j))
            assert grid.Value(i, j).Distance(expected) <= TOL


def test_GeomGridEval_BezierSurfaceTest_RationalEvaluation():
    bez = _rational_bilinear()
    ev = GeomGridEval_BezierSurface(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGrid(params, params)
    for i in range(1, 6):
        for j in range(1, 6):
            expected = bez.Value(params.Value(i), params.Value(j))
            assert grid.Value(i, j).Distance(expected) <= TOL


def test_GeomGridEval_BezierSurfaceTest_DerivativeD1():
    bez = Geom_BezierSurface(_bilinear(1))
    ev = GeomGridEval_BezierSurface(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD1(params, params)
    for i in range(1, 6):
        for j in range(1, 6):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            bez.D1(params.Value(i), params.Value(j), p, d1u, d1v)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL


def test_GeomGridEval_BezierSurfaceTest_DerivativeD2():
    bez = _sin_ij()
    ev = GeomGridEval_BezierSurface(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD2(params, params)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
            bez.D2(params.Value(i), params.Value(j), p, d1u, d1v, d2u, d2v, d2uv)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL
            assert (r.D2U - d2u).Magnitude() <= TOL
            assert (r.D2V - d2v).Magnitude() <= TOL
            assert (r.D2UV - d2uv).Magnitude() <= TOL


def test_GeomGridEval_BezierSurfaceTest_DerivativeD3():
    bez = Geom_BezierSurface(_sin_half(4))
    ev = GeomGridEval_BezierSurface(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD3(params, params)
    for i in range(1, 6):
        for j in range(1, 6):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv = (gp_Vec() for _ in range(9))
            bez.D3(params.Value(i), params.Value(j), p, d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert (r.D3U - d3u).Magnitude() <= TOL
            assert (r.D3V - d3v).Magnitude() <= TOL
            assert (r.D3UUV - d3uuv).Magnitude() <= TOL
            assert (r.D3UVV - d3uvv).Magnitude() <= TOL


def _check_dn(bez, nu, nv):
    ev = GeomGridEval_BezierSurface(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridDN(params, params, nu, nv)
    for i in range(1, 6):
        for j in range(1, 6):
            expected = bez.DN(params.Value(i), params.Value(j), nu, nv)
            assert (grid.Value(i, j) - expected).Magnitude() <= TOL


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_U1V0():
    _check_dn(_sin_ij(), 1, 0)


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_U0V1():
    _check_dn(_sin_ij(), 0, 1)


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_U2V0():
    _check_dn(_sin_ij(), 2, 0)


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_U1V1():
    _check_dn(_sin_ij(), 1, 1)


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_BeyondDegree():
    ev = GeomGridEval_BezierSurface(_sin_ij())
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridDN(params, params, 3, 0)
    for i in range(1, 6):
        for j in range(1, 6):
            assert grid.Value(i, j).Magnitude() <= TOL


def test_GeomGridEval_BezierSurfaceTest_DerivativeDN_RationalSurface():
    bez = _rational_bilinear()
    for nu, nv in ((0, 1), (1, 0), (1, 1)):
        _check_dn(bez, nu, nv)


def test_GeomGridEval_BezierSurfaceTest_IsolineU_CompareToGeomD0():
    bez = Geom_BezierSurface(_sin_half(3))
    ev = GeomGridEval_BezierSurface(bez)
    u = _single(0.5)
    v = _uniform(0.0, 1.0, 10)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 10
    assert grid.ColLength() == 1
    for j in range(1, 11):
        expected = gp_Pnt()
        bez.D0(u.Value(1), v.Value(j), expected)
        assert grid.Value(1, j).Distance(expected) <= TOL


def test_GeomGridEval_BezierSurfaceTest_IsolineV_CompareToGeomD0():
    bez = Geom_BezierSurface(_sin_half(3))
    ev = GeomGridEval_BezierSurface(bez)
    u = _uniform(0.0, 1.0, 10)
    v = _single(0.7)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 1
    assert grid.ColLength() == 10
    for i in range(1, 11):
        expected = gp_Pnt()
        bez.D0(u.Value(i), v.Value(1), expected)
        assert grid.Value(i, 1).Distance(expected) <= TOL


def test_GeomGridEval_BezierSurfaceTest_IsolineRational_CompareToGeomD0():
    poles = _sin_half(3)
    weights = NCollection_Array2[float](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            weights.SetValue(i, j, 1.0 + 0.5 * ((i - 1) + (j - 1)))
    bez = Geom_BezierSurface(poles, weights)
    ev = GeomGridEval_BezierSurface(bez)
    u = _single(0.3)
    v = _uniform(0.0, 1.0, 15)
    grid = ev.EvaluateGrid(u, v)
    for j in range(1, 16):
        expected = gp_Pnt()
        bez.D0(u.Value(1), v.Value(j), expected)
        assert grid.Value(1, j).Distance(expected) <= TOL
