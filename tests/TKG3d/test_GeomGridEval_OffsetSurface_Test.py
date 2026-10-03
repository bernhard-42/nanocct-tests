# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_OffsetSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_CylindricalSurface, Geom_OffsetSurface, Geom_Plane
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomGridEval import GeomGridEval_OffsetSurface, GeomGridEval_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-9


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


def _plane_offset(dist):
    return Geom_OffsetSurface(Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), dist)


def _cyl_offset():
    cyl = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    return Geom_OffsetSurface(cyl, 2.0)


def _vnear(a, b):
    return (a - b).Magnitude() <= TOL


def test_GeomGridEval_OffsetSurfaceTest_PlaneOffset():
    offset = _plane_offset(10.0)
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 10.0, 5)
    grid = ev.EvaluateGrid(u, v)
    for i in range(1, 6):
        for j in range(1, 6):
            expected = offset.Value(u.Value(i), v.Value(j))
            assert grid.Value(i, j).Distance(expected) <= TOL
            assert abs(grid.Value(i, j).Z() - 10.0) <= TOL


def test_GeomGridEval_OffsetSurfaceTest_CylinderOffset():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 5)
    grid = ev.EvaluateGrid(u, v)
    for i in range(1, 10):
        for j in range(1, 6):
            p = grid.Value(i, j)
            assert p.Distance(offset.Value(u.Value(i), v.Value(j))) <= TOL
            assert abs(math.hypot(p.X(), p.Y()) - 7.0) <= TOL


def test_GeomGridEval_OffsetSurfaceTest_DerivativeD1():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 5)
    v = _uniform(0.0, 5.0, 3)
    grid = ev.EvaluateGridD1(u, v)
    for i in range(1, 6):
        for j in range(1, 4):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            offset.D1(u.Value(i), v.Value(j), p, d1u, d1v)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)


def test_GeomGridEval_OffsetSurfaceTest_NestedDispatch():
    offset = _plane_offset(5.0)
    ev = GeomGridEval_Surface(offset)
    u = _uniform(0.0, 1.0, 3)
    v = _uniform(0.0, 1.0, 3)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 3
    assert grid.ColLength() == 3
    assert abs(grid.Value(1, 1).Z() - 5.0) <= TOL


def test_GeomGridEval_OffsetSurfaceTest_DerivativeD2():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 5)
    v = _uniform(0.0, 5.0, 3)
    grid = ev.EvaluateGridD2(u, v)
    for i in range(1, 6):
        for j in range(1, 4):
            p = gp_Pnt()
            d1u, d1v, d2u, d2v, d2uv = (gp_Vec() for _ in range(5))
            offset.D2(u.Value(i), v.Value(j), p, d1u, d1v, d2u, d2v, d2uv)
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert _vnear(r.D2U, d2u)
            assert _vnear(r.D2V, d2v)
            assert _vnear(r.D2UV, d2uv)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeD3():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 5)
    v = _uniform(0.0, 5.0, 3)
    grid = ev.EvaluateGridD3(u, v)
    adaptor = GeomAdaptor_Surface(offset)
    for i in range(1, 6):
        for j in range(1, 4):
            p = gp_Pnt()
            vs = [gp_Vec() for _ in range(9)]
            adaptor.D3(u.Value(i), v.Value(j), p, *vs)
            d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv = vs
            r = grid.Value(i, j)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert _vnear(r.D2U, d2u)
            assert _vnear(r.D2V, d2v)
            assert _vnear(r.D2UV, d2uv)
            assert _vnear(r.D3U, d3u)
            assert _vnear(r.D3V, d3v)
            assert _vnear(r.D3UUV, d3uuv)
            assert _vnear(r.D3UVV, d3uvv)


def _check_dn(nu, nv):
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 5)
    v = _uniform(0.0, 5.0, 3)
    grid = ev.EvaluateGridDN(u, v, nu, nv)
    for i in range(1, 6):
        for j in range(1, 4):
            expected = offset.DN(u.Value(i), v.Value(j), nu, nv)
            assert _vnear(grid.Value(i, j), expected)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeDN_U1V0():
    _check_dn(1, 0)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeDN_U0V1():
    _check_dn(0, 1)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeDN_U1V1():
    _check_dn(1, 1)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeDN_U2V0():
    _check_dn(2, 0)


def test_GeomGridEval_OffsetSurfaceTest_DerivativeDN_PlaneOffset():
    offset = _plane_offset(10.0)
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 10.0, 5)
    v = _uniform(0.0, 10.0, 5)
    grid_u = ev.EvaluateGridDN(u, v, 1, 0)
    grid_v = ev.EvaluateGridDN(u, v, 0, 1)
    for i in range(1, 6):
        for j in range(1, 6):
            assert _vnear(grid_u.Value(i, j), offset.DN(u.Value(i), v.Value(j), 1, 0))
            assert _vnear(grid_v.Value(i, j), offset.DN(u.Value(i), v.Value(j), 0, 1))
    grid_2u = ev.EvaluateGridDN(u, v, 2, 0)
    for i in range(1, 6):
        for j in range(1, 6):
            assert grid_2u.Value(i, j).Magnitude() <= TOL


def test_GeomGridEval_OffsetSurfaceTest_IsolineU_CompareToGeomD0():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _single(math.pi / 4)
    v = _uniform(0.0, 5.0, 15)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 15
    assert grid.ColLength() == 1
    for j in range(1, 16):
        expected = gp_Pnt()
        offset.D0(u.Value(1), v.Value(j), expected)
        assert grid.Value(1, j).Distance(expected) <= TOL


def test_GeomGridEval_OffsetSurfaceTest_IsolineV_CompareToGeomD0():
    offset = _cyl_offset()
    ev = GeomGridEval_OffsetSurface(offset)
    u = _uniform(0.0, 2 * math.pi, 15)
    v = _single(2.5)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 1
    assert grid.ColLength() == 15
    for i in range(1, 16):
        expected = gp_Pnt()
        offset.D0(u.Value(i), v.Value(1), expected)
        assert grid.Value(i, 1).Distance(expected) <= TOL


def test_GeomGridEval_OffsetSurfaceTest_IsolinePlane_CompareToGeomD0():
    offset = _plane_offset(3.0)
    ev = GeomGridEval_OffsetSurface(offset)
    u = _single(5.0)
    v = _uniform(-10.0, 10.0, 20)
    grid = ev.EvaluateGrid(u, v)
    for j in range(1, 21):
        expected = gp_Pnt()
        offset.D0(u.Value(1), v.Value(j), expected)
        assert grid.Value(1, j).Distance(expected) <= TOL
