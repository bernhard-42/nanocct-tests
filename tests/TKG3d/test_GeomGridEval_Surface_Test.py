# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_Surface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import nanocct.GeomAbs as GeomAbs
from nanocct.Geom import (
    Geom_BezierSurface,
    Geom_BSplineSurface,
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_Line,
    Geom_Plane,
    Geom_SphericalSurface,
    Geom_SurfaceOfRevolution,
    Geom_ToroidalSurface,
)
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomGridEval import (
    GeomGridEval_Cone,
    GeomGridEval_Cylinder,
    GeomGridEval_OtherSurface,
    GeomGridEval_Plane,
    GeomGridEval_Sphere,
    GeomGridEval_Surface,
    GeomGridEval_Torus,
)
from nanocct.gp import gp, gp_Ax3, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2

TOL = 1e-10


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _simple_bspline():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(2, 1, gp_Pnt(1, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
    poles.SetValue(2, 2, gp_Pnt(1, 1, 1))
    uk = NCollection_Array1[float](1, 2)
    vk = NCollection_Array1[float](1, 2)
    um = NCollection_Array1[int](1, 2)
    vm = NCollection_Array1[int](1, 2)
    uk.SetValue(1, 0.0)
    uk.SetValue(2, 1.0)
    vk.SetValue(1, 0.0)
    vk.SetValue(2, 1.0)
    for m in (um, vm):
        m.SetValue(1, 2)
        m.SetValue(2, 2)
    return Geom_BSplineSurface(poles, uk, vk, um, vm, 1, 1)


def _ax3():
    return gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _d2(surf, u, v):
    p = gp_Pnt()
    vs = [gp_Vec() for _ in range(5)]
    surf.D2(u, v, p, *vs)
    return p, vs


def _d3(surf, u, v):
    p = gp_Pnt()
    vs = [gp_Vec() for _ in range(9)]
    surf.D3(u, v, p, *vs)
    return p, vs


def _vnear(a, b):
    return (a - b).Magnitude() <= TOL


def _check_points(grid, surf, u, v):
    for iu in range(1, u.Size() + 1):
        for iv in range(1, v.Size() + 1):
            expected = surf.Value(u.Value(iu), v.Value(iv))
            assert grid.Value(iu, iv).Distance(expected) <= TOL


def _check_d3_only(grid, ref, u, v):
    for iu in range(1, u.Size() + 1):
        for iv in range(1, v.Size() + 1):
            p, (_d1u, _d1v, _d2u, _d2v, _d2uv, d3u, d3v, d3uuv, d3uvv) = _d3(ref, u.Value(iu), v.Value(iv))
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D3U, d3u)
            assert _vnear(r.D3V, d3v)
            assert _vnear(r.D3UUV, d3uuv)
            assert _vnear(r.D3UVV, d3uvv)


# ---------------------------------------------------------------- Plane


def test_GeomGridEval_PlaneTest_BasicEvaluation():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Plane(plane)
    assert ev.Geometry() is not None
    u = _uniform(0.0, 5.0, 6)
    v = _uniform(0.0, 3.0, 4)
    grid = ev.EvaluateGrid(u, v)
    assert grid.RowLength() == 4
    assert grid.ColLength() == 6
    for iu in range(1, 7):
        for iv in range(1, 5):
            p = grid.Value(iu, iv)
            assert abs(p.Z()) <= TOL
            assert abs(p.X() - u.Value(iu)) <= TOL
            assert abs(p.Y() - v.Value(iv)) <= TOL


def test_GeomGridEval_PlaneTest_NonOriginPlane():
    plane = Geom_Plane(gp_Pnt(1, 2, 3), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Plane(plane)
    u = _uniform(-1.0, 1.0, 3)
    v = _uniform(-1.0, 1.0, 3)
    grid = ev.EvaluateGrid(u, v)
    for iu in range(1, 4):
        for iv in range(1, 4):
            assert abs(grid.Value(iu, iv).Z() - 3.0) <= TOL
    assert abs(grid.Value(2, 2).X() - 1.0) <= TOL
    assert abs(grid.Value(2, 2).Y() - 2.0) <= TOL


# ---------------------------------------------------------------- Sphere


def test_GeomGridEval_SphereTest_BasicEvaluation():
    sphere = Geom_SphericalSurface(_ax3(), 1.0)
    ev = GeomGridEval_Sphere(sphere)
    assert ev.Geometry() is not None
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-math.pi / 2, math.pi / 2, 5)
    grid = ev.EvaluateGrid(u, v)
    origin = gp_Pnt(0, 0, 0)
    for iu in range(1, 10):
        for iv in range(1, 6):
            assert abs(grid.Value(iu, iv).Distance(origin) - 1.0) <= TOL
    for iu in range(1, 10):
        north = grid.Value(iu, 5)
        assert abs(north.X()) <= TOL
        assert abs(north.Y()) <= TOL
        assert abs(north.Z() - 1.0) <= TOL
        south = grid.Value(iu, 1)
        assert abs(south.X()) <= TOL
        assert abs(south.Y()) <= TOL
        assert abs(south.Z() + 1.0) <= TOL


def test_GeomGridEval_SphereTest_NonUnitSphere():
    sphere = Geom_SphericalSurface(gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(0, 0, 1)), 3.0)
    ev = GeomGridEval_Sphere(sphere)
    u = _uniform(0.0, 2 * math.pi, 17)
    v = _uniform(-math.pi / 2, math.pi / 2, 9)
    grid = ev.EvaluateGrid(u, v)
    center = gp_Pnt(1, 2, 3)
    for iu in range(1, 18):
        for iv in range(1, 10):
            assert abs(grid.Value(iu, iv).Distance(center) - 3.0) <= TOL


# ---------------------------------------------------------------- OtherSurface


def test_GeomGridEval_OtherSurfaceTest_CylinderFallback():
    cyl = Geom_CylindricalSurface(_ax3(), 2.0)
    adaptor = GeomAdaptor_Surface(cyl)
    ev = GeomGridEval_OtherSurface(adaptor)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_points(ev.EvaluateGrid(u, v), cyl, u, v)


# ---------------------------------------------------------------- Surface (dispatcher)


def test_GeomGridEval_SurfaceTest_PlaneDispatch():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    adaptor = GeomAdaptor_Surface(plane)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_Plane
    u = _uniform(-5.0, 5.0, 11)
    v = _uniform(-3.0, 3.0, 7)
    _check_points(ev.EvaluateGrid(u, v), plane, u, v)


def test_GeomGridEval_SurfaceTest_SphereDispatch():
    sphere = Geom_SphericalSurface(_ax3(), 2.0)
    adaptor = GeomAdaptor_Surface(sphere)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_Sphere
    u = _uniform(0.0, 2 * math.pi, 13)
    v = _uniform(-math.pi / 2, math.pi / 2, 7)
    _check_points(ev.EvaluateGrid(u, v), sphere, u, v)


def test_GeomGridEval_SurfaceTest_BSplineDispatch():
    surf = _simple_bspline()
    adaptor = GeomAdaptor_Surface(surf)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_BSplineSurface
    u = _uniform(0.0, 1.0, 11)
    v = _uniform(0.0, 1.0, 11)
    _check_points(ev.EvaluateGrid(u, v), surf, u, v)


def test_GeomGridEval_SurfaceTest_BezierSurfaceDispatch():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(2, 1, gp_Pnt(1, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(0, 1, 0))
    poles.SetValue(2, 2, gp_Pnt(1, 1, 0))
    bezier = Geom_BezierSurface(poles)
    adaptor = GeomAdaptor_Surface(bezier)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_BezierSurface
    params = _uniform(0.0, 1.0, 5)
    _check_points(ev.EvaluateGrid(params, params), bezier, params, params)


def test_GeomGridEval_SurfaceTest_CylinderDispatch():
    cyl = Geom_CylindricalSurface(_ax3(), 2.0)
    adaptor = GeomAdaptor_Surface(cyl)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_Cylinder
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_points(ev.EvaluateGrid(u, v), cyl, u, v)


def test_GeomGridEval_SurfaceTest_TorusDispatch():
    torus = Geom_ToroidalSurface(_ax3(), 4.0, 1.0)
    adaptor = GeomAdaptor_Surface(torus)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_Torus
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    _check_points(ev.EvaluateGrid(u, v), torus, u, v)


def test_GeomGridEval_SurfaceTest_ConeDispatch():
    cone = Geom_ConicalSurface(_ax3(), math.pi / 4, 1.0)
    adaptor = GeomAdaptor_Surface(cone)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_Cone
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_points(ev.EvaluateGrid(u, v), cone, u, v)


def test_GeomGridEval_SurfaceTest_SurfaceOfRevolutionFallbackDispatch():
    line = Geom_Line(gp_Pnt(1, 0, 0), gp_Dir(0, 0, 1))
    rev = Geom_SurfaceOfRevolution(line, gp.OZ_s())
    adaptor = GeomAdaptor_Surface(rev)
    ev = GeomGridEval_Surface(adaptor)
    assert ev.GetType() == GeomAbs.GeomAbs_SurfaceOfRevolution
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_points(ev.EvaluateGrid(u, v), rev, u, v)


def test_GeomGridEval_SurfaceTest_DirectHandleInit():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Surface(plane)
    assert ev.GetType() == GeomAbs.GeomAbs_Plane
    u = _uniform(0.0, 1.0, 5)
    v = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGrid(u, v)
    assert not grid.IsEmpty()
    assert abs(grid.Value(1, 1).Z()) <= TOL


def test_GeomGridEval_SurfaceTest_EmptyParams():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    adaptor = GeomAdaptor_Surface(plane)
    ev = GeomGridEval_Surface(adaptor)
    empty = NCollection_Array1[float]()
    grid = ev.EvaluateGrid(empty, empty)
    assert grid.IsEmpty()


# ---------------------------------------------------------------- D1 / D2


def test_GeomGridEval_PlaneTest_DerivativeD1():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Plane(plane)
    u = _uniform(0.0, 5.0, 6)
    v = _uniform(0.0, 3.0, 4)
    grid = ev.EvaluateGridD1(u, v)
    p, d1u_ref, d1v_ref = gp_Pnt(), gp_Vec(), gp_Vec()
    plane.D1(0.0, 0.0, p, d1u_ref, d1v_ref)
    for iu in range(1, 7):
        for iv in range(1, 5):
            r = grid.Value(iu, iv)
            assert _vnear(r.D1U, d1u_ref)
            assert _vnear(r.D1V, d1v_ref)


def test_GeomGridEval_PlaneTest_DerivativeD2():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Plane(plane)
    u = _uniform(0.0, 5.0, 6)
    v = _uniform(0.0, 3.0, 4)
    grid = ev.EvaluateGridD2(u, v)
    for iu in range(1, 7):
        for iv in range(1, 5):
            r = grid.Value(iu, iv)
            assert r.D2U.Magnitude() <= TOL
            assert r.D2V.Magnitude() <= TOL
            assert r.D2UV.Magnitude() <= TOL


def _check_d1(grid, surf, u, v):
    for iu in range(1, u.Size() + 1):
        for iv in range(1, v.Size() + 1):
            p, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
            surf.D1(u.Value(iu), v.Value(iv), p, d1u, d1v)
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)


def _check_d2(grid, surf, u, v):
    for iu in range(1, u.Size() + 1):
        for iv in range(1, v.Size() + 1):
            p, (d1u, d1v, d2u, d2v, d2uv) = _d2(surf, u.Value(iu), v.Value(iv))
            r = grid.Value(iu, iv)
            assert r.Point.Distance(p) <= TOL
            assert _vnear(r.D1U, d1u)
            assert _vnear(r.D1V, d1v)
            assert _vnear(r.D2U, d2u)
            assert _vnear(r.D2V, d2v)
            assert _vnear(r.D2UV, d2uv)


def test_GeomGridEval_SphereTest_DerivativeD1():
    sphere = Geom_SphericalSurface(_ax3(), 2.0)
    ev = GeomGridEval_Sphere(sphere)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-math.pi / 2, math.pi / 2, 5)
    _check_d1(ev.EvaluateGridD1(u, v), sphere, u, v)


def test_GeomGridEval_SphereTest_DerivativeD2():
    sphere = Geom_SphericalSurface(_ax3(), 2.0)
    ev = GeomGridEval_Sphere(sphere)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-math.pi / 2, math.pi / 2, 5)
    _check_d2(ev.EvaluateGridD2(u, v), sphere, u, v)


def test_GeomGridEval_SurfaceTest_UnifiedDerivativeD1():
    sphere = Geom_SphericalSurface(_ax3(), 2.0)
    adaptor = GeomAdaptor_Surface(sphere)
    ev = GeomGridEval_Surface(adaptor)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-math.pi / 2, math.pi / 2, 5)
    _check_d1(ev.EvaluateGridD1(u, v), sphere, u, v)


def test_GeomGridEval_SurfaceTest_UnifiedDerivativeD2():
    surf = _simple_bspline()
    adaptor = GeomAdaptor_Surface(surf)
    ev = GeomGridEval_Surface(adaptor)
    u = _uniform(0.0, 1.0, 5)
    v = _uniform(0.0, 1.0, 5)
    _check_d2(ev.EvaluateGridD2(u, v), surf, u, v)


# ---------------------------------------------------------------- D3


def test_GeomGridEval_PlaneTest_DerivativeD3():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    ev = GeomGridEval_Plane(plane)
    u = _uniform(0.0, 5.0, 6)
    v = _uniform(0.0, 3.0, 4)
    grid = ev.EvaluateGridD3(u, v)
    for iu in range(1, 7):
        for iv in range(1, 5):
            r = grid.Value(iu, iv)
            for vec in (r.D2U, r.D2V, r.D2UV, r.D3U, r.D3V, r.D3UUV, r.D3UVV):
                assert vec.Magnitude() <= TOL


def test_GeomGridEval_SphereTest_DerivativeD3():
    sphere = Geom_SphericalSurface(_ax3(), 2.0)
    ev = GeomGridEval_Sphere(sphere)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(-math.pi / 2 + 0.1, math.pi / 2 - 0.1, 5)
    grid = ev.EvaluateGridD3(u, v)
    adaptor = GeomAdaptor_Surface(sphere)
    for iu in range(1, 10):
        for iv in range(1, 6):
            p, (d1u, d1v, d2u, d2v, d2uv, d3u, d3v, d3uuv, d3uvv) = _d3(adaptor, u.Value(iu), v.Value(iv))
            r = grid.Value(iu, iv)
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


def test_GeomGridEval_CylinderTest_DerivativeD3():
    cyl = Geom_CylindricalSurface(_ax3(), 2.0)
    ev = GeomGridEval_Cylinder(cyl)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_d3_only(ev.EvaluateGridD3(u, v), GeomAdaptor_Surface(cyl), u, v)


def test_GeomGridEval_ConeTest_DerivativeD3():
    cone = Geom_ConicalSurface(_ax3(), math.pi / 4, 1.0)
    ev = GeomGridEval_Cone(cone)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 5.0, 6)
    _check_d3_only(ev.EvaluateGridD3(u, v), GeomAdaptor_Surface(cone), u, v)


def test_GeomGridEval_TorusTest_DerivativeD3():
    torus = Geom_ToroidalSurface(_ax3(), 4.0, 1.0)
    ev = GeomGridEval_Torus(torus)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    _check_d3_only(ev.EvaluateGridD3(u, v), GeomAdaptor_Surface(torus), u, v)


def test_GeomGridEval_SurfaceTest_UnifiedDerivativeD3():
    torus = Geom_ToroidalSurface(_ax3(), 4.0, 1.0)
    adaptor = GeomAdaptor_Surface(torus)
    ev = GeomGridEval_Surface(adaptor)
    u = _uniform(0.0, 2 * math.pi, 9)
    v = _uniform(0.0, 2 * math.pi, 9)
    _check_d3_only(ev.EvaluateGridD3(u, v), torus, u, v)
