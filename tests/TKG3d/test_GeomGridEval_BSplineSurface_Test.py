# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_BSplineSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_BSplineSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomGridEval import GeomGridEval_BSplineSurface
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


def _simple():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(2, 1, gp_Pnt(1, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
    poles.SetValue(2, 2, gp_Pnt(1, 1, 1))
    knots = _floats([0.0, 1.0])
    mults = _ints([2, 2])
    return Geom_BSplineSurface(poles, knots, knots, mults, mults, 1, 1)


def _rational():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    weights = NCollection_Array2[float](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            center = i == 2 and j == 2
            poles.SetValue(i, j, gp_Pnt(i - 1.0, j - 1.0, 1.0 if center else 0.0))
            weights.SetValue(i, j, 2.0 if center else 1.0)
    knots = _floats([0.0, 1.0])
    mults = _ints([3, 3])
    return Geom_BSplineSurface(poles, weights, knots, knots, mults, mults, 2, 2)


def _multi_span():
    poles = NCollection_Array2[gp_Pnt](1, 5, 1, 5)
    for i in range(1, 6):
        for j in range(1, 6):
            z = math.sin((i - 1) * math.pi / 4.0) * math.sin((j - 1) * math.pi / 4.0)
            poles.SetValue(i, j, gp_Pnt(i - 1.0, j - 1.0, z))
    knots = _floats([0.0, 0.5, 1.0])
    mults = _ints([3, 2, 3])
    return Geom_BSplineSurface(poles, knots, knots, mults, mults, 2, 2)


def _check_grid_vs_value(surf, u, v):
    ev = GeomGridEval_BSplineSurface(surf)
    grid = ev.EvaluateGrid(u, v)
    for iu in range(1, u.Size() + 1):
        for iv in range(1, v.Size() + 1):
            expected = surf.Value(u.Value(iu), v.Value(iv))
            assert grid.Value(iu, iv).Distance(expected) <= TOL


def _check_grid_vs_d0(surf, u, v):
    ev = GeomGridEval_BSplineSurface(surf)
    grid = ev.EvaluateGrid(u, v)
    for iu in range(1, grid.ColLength() + 1):
        for iv in range(1, grid.RowLength() + 1):
            expected = gp_Pnt()
            surf.D0(u.Value(iu), v.Value(iv), expected)
            assert grid.Value(iu, iv).Distance(expected) <= TOL


def _check_dn(surf, n, nu, nv):
    ev = GeomGridEval_BSplineSurface(surf)
    u = _uniform(0.0, 1.0, n)
    v = _uniform(0.0, 1.0, n)
    grid = ev.EvaluateGridDN(u, v, nu, nv)
    for iu in range(1, n + 1):
        for iv in range(1, n + 1):
            expected = surf.DN(u.Value(iu), v.Value(iv), nu, nv)
            assert (grid.Value(iu, iv) - expected).Magnitude() <= TOL


def test_GeomGridEval_BSplineSurfaceTest_BasicEvaluation():
    surf = _simple()
    assert GeomGridEval_BSplineSurface(surf).Geometry() is not None
    _check_grid_vs_value(surf, _uniform(0.0, 1.0, 5), _uniform(0.0, 1.0, 5))


def test_GeomGridEval_BSplineSurfaceTest_CornerPoints():
    ev = GeomGridEval_BSplineSurface(_simple())
    params = _floats([0.0, 1.0])
    grid = ev.EvaluateGrid(params, params)
    assert grid.Value(1, 1).Distance(gp_Pnt(0, 0, 0)) <= TOL
    assert grid.Value(2, 1).Distance(gp_Pnt(1, 0, 0)) <= TOL
    assert grid.Value(1, 2).Distance(gp_Pnt(0, 1, 0)) <= TOL
    assert grid.Value(2, 2).Distance(gp_Pnt(1, 1, 1)) <= TOL


def test_GeomGridEval_BSplineSurfaceTest_RationalSurface():
    _check_grid_vs_value(_rational(), _uniform(0.0, 1.0, 11), _uniform(0.0, 1.0, 11))


def test_GeomGridEval_BSplineSurfaceTest_MultiSpanSurface():
    _check_grid_vs_value(_multi_span(), _uniform(0.0, 1.0, 21), _uniform(0.0, 1.0, 21))


def test_GeomGridEval_BSplineSurfaceTest_HigherDegree():
    poles = NCollection_Array2[gp_Pnt](1, 4, 1, 4)
    for i in range(1, 5):
        for j in range(1, 5):
            poles.SetValue(i, j, gp_Pnt(i - 1.0, j - 1.0, math.cos((i + j - 2) * math.pi / 6.0)))
    knots = _floats([0.0, 1.0])
    mults = _ints([4, 4])
    surf = Geom_BSplineSurface(poles, knots, knots, mults, mults, 3, 3)
    _check_grid_vs_value(surf, _uniform(0.0, 1.0, 17), _uniform(0.0, 1.0, 17))


def test_GeomGridEval_BSplineSurfaceTest_IsolineU_CompareToGeomD0():
    _check_grid_vs_d0(_multi_span(), _single(0.5), _uniform(0.0, 1.0, 15))


def test_GeomGridEval_BSplineSurfaceTest_IsolineV_CompareToGeomD0():
    _check_grid_vs_d0(_multi_span(), _uniform(0.0, 1.0, 15), _single(0.7))


def test_GeomGridEval_BSplineSurfaceTest_IsolineMultiSpan_CompareToGeomD0():
    _check_grid_vs_d0(_multi_span(), _single(0.35), _uniform(0.0, 1.0, 20))


def test_GeomGridEval_BSplineSurfaceTest_IsolineRational_CompareToGeomD0():
    _check_grid_vs_d0(_rational(), _uniform(0.0, 1.0, 15), _single(0.3))


def test_GeomGridEval_BSplineSurfaceTest_DerivativeD1():
    surf = _simple()
    ev = GeomGridEval_BSplineSurface(surf)
    u = _uniform(0.0, 1.0, 5)
    v = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD1(u, v)
    for iu in range(1, 6):
        for iv in range(1, 6):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            surf.D1(u.Value(iu), v.Value(iv), p, d1u, d1v)
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert (r.D1U - d1u).Magnitude() <= TOL
            assert (r.D1V - d1v).Magnitude() <= TOL


def test_GeomGridEval_BSplineSurfaceTest_DerivativeD2():
    surf = _simple()
    ev = GeomGridEval_BSplineSurface(surf)
    u = _uniform(0.0, 1.0, 5)
    v = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD2(u, v)
    for iu in range(1, 6):
        for iv in range(1, 6):
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


def test_GeomGridEval_BSplineSurfaceTest_DerivativeD3():
    surf = _multi_span()
    ev = GeomGridEval_BSplineSurface(surf)
    u = _uniform(0.0, 1.0, 11)
    v = _uniform(0.0, 1.0, 11)
    grid = ev.EvaluateGridD3(u, v)
    adaptor = GeomAdaptor_Surface(surf)
    for iu in range(1, 12):
        for iv in range(1, 12):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv = (gp_Vec() for _ in range(9))
            adaptor.D3(u.Value(iu), v.Value(iv), p, d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv)
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


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_U1V0():
    _check_dn(_simple(), 5, 1, 0)


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_U0V1():
    _check_dn(_simple(), 5, 0, 1)


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_U1V1():
    _check_dn(_simple(), 5, 1, 1)


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_BeyondDegree():
    ev = GeomGridEval_BSplineSurface(_simple())
    u = _uniform(0.0, 1.0, 5)
    v = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridDN(u, v, 2, 0)
    for iu in range(1, 6):
        for iv in range(1, 6):
            assert grid.Value(iu, iv).Magnitude() <= TOL


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_MultiSpan():
    surf = _multi_span()
    for nu, nv in ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2)):
        _check_dn(surf, 11, nu, nv)


def test_GeomGridEval_BSplineSurfaceTest_DerivativeDN_RationalSurface():
    surf = _rational()
    for nu in range(3):
        for nv in range(3):
            if nu + nv == 0:
                continue
            _check_dn(surf, 7, nu, nv)
