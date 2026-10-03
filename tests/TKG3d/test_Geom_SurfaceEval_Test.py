# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_SurfaceEval_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import (
    Geom_BezierSurface,
    Geom_BSplineSurface,
    Geom_Circle,
    Geom_CylindricalSurface,
    Geom_Line,
    Geom_OffsetSurface,
    Geom_Plane,
    Geom_SphericalSurface,
    Geom_SurfaceOfLinearExtrusion,
    Geom_SurfaceOfRevolution,
)
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pln, gp_Pnt, gp_Sphere, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()
ORIGIN = gp_Pnt(0.0, 0.0, 0.0)


def xy_plane():
    return Geom_Plane(gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))


def check_d2_consistent(surf, u, v):
    ev = surf.EvalD2(u, v)
    p = gp_Pnt()
    d1u, d1v, d2u, d2v, d2uv = gp_Vec(), gp_Vec(), gp_Vec(), gp_Vec(), gp_Vec()
    surf.D2(u, v, p, d1u, d1v, d2u, d2v, d2uv)
    assert abs(ev.Point.Distance(p)) <= TOL
    assert abs((ev.D1U - d1u).Magnitude()) <= TOL
    assert abs((ev.D1V - d1v).Magnitude()) <= TOL
    assert abs((ev.D2U - d2u).Magnitude()) <= TOL
    assert abs((ev.D2V - d2v).Magnitude()) <= TOL
    assert abs((ev.D2UV - d2uv).Magnitude()) <= TOL


def test_Geom_SurfaceEvalTest_Plane_EvalD0_ReturnsValidPoint():
    res = xy_plane().EvalD0(1.0, 2.0)
    assert abs(res.X() - 1.0) <= TOL
    assert abs(res.Y() - 2.0) <= TOL
    assert abs(res.Z()) <= TOL


def test_Geom_SurfaceEvalTest_Plane_EvalD1_ConstantPartials():
    d1 = xy_plane().EvalD1(1.0, 2.0)
    assert abs(d1.D1U.Magnitude() - 1.0) <= TOL
    assert abs(d1.D1V.Magnitude() - 1.0) <= TOL
    assert abs(d1.D1U.Dot(d1.D1V)) <= TOL


def test_Geom_SurfaceEvalTest_Sphere_EvalD1_PartialDerivatives():
    r = 5.0
    s = Geom_SphericalSurface(gp_Sphere(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), r))
    d1 = s.EvalD1(math.pi / 4.0, math.pi / 6.0)
    assert abs(d1.Point.Distance(ORIGIN) - r) <= TOL
    assert d1.D1U.Magnitude() > TOL
    assert d1.D1V.Magnitude() > TOL


def test_Geom_SurfaceEvalTest_BSplineSurface_EvalD2_ConsistentWithOldAPI():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles[i, j] = gp_Pnt(float(i - 1), float(j - 1), 0.1 * float((i - 2) * (j - 2)))
    uk = NCollection_Array1[float](1, 2)
    uk[1], uk[2] = 0.0, 1.0
    vk = NCollection_Array1[float](1, 2)
    vk[1], vk[2] = 0.0, 1.0
    um = NCollection_Array1[int](1, 2)
    um[1], um[2] = 3, 3
    vm = NCollection_Array1[int](1, 2)
    vm[1], vm[2] = 3, 3
    surf = Geom_BSplineSurface(poles, uk, vk, um, vm, 2, 2)
    check_d2_consistent(surf, 0.5, 0.5)


def test_Geom_SurfaceEvalTest_OffsetSurface_EvalD0_ValidOnRegularSurface():
    off = Geom_OffsetSurface(xy_plane(), 3.0)
    res = off.EvalD0(1.0, 2.0)
    assert abs(res.X() - 1.0) <= TOL
    assert abs(res.Y() - 2.0) <= TOL
    assert abs(res.Z() - 3.0) <= TOL


def test_Geom_SurfaceEvalTest_CylindricalSurface_EvalD1_ValidResults():
    r = 4.0
    s = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), r)
    v = 3.0
    d1 = s.EvalD1(math.pi / 4.0, v)
    assert abs(math.hypot(d1.Point.X(), d1.Point.Y()) - r) <= TOL
    assert abs(d1.Point.Z() - v) <= TOL
    assert d1.D1U.Magnitude() > TOL
    assert abs(d1.D1V.X()) <= TOL
    assert abs(d1.D1V.Y()) <= TOL
    assert abs(d1.D1V.Z() - 1.0) <= TOL


def test_Geom_SurfaceEvalTest_BezierSurface_EvalD2_ConsistentWithOldAPI():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    poles[1, 1] = gp_Pnt(0.0, 0.0, 0.0)
    poles[1, 2] = gp_Pnt(0.0, 1.0, 0.0)
    poles[1, 3] = gp_Pnt(0.0, 2.0, 0.0)
    poles[2, 1] = gp_Pnt(1.0, 0.0, 0.5)
    poles[2, 2] = gp_Pnt(1.0, 1.0, 1.0)
    poles[2, 3] = gp_Pnt(1.0, 2.0, 0.5)
    poles[3, 1] = gp_Pnt(2.0, 0.0, 0.0)
    poles[3, 2] = gp_Pnt(2.0, 1.0, 0.0)
    poles[3, 3] = gp_Pnt(2.0, 2.0, 0.0)
    check_d2_consistent(Geom_BezierSurface(poles), 0.3, 0.7)


def test_Geom_SurfaceEvalTest_ExtrusionSurface_EvalD0_ValidResults():
    basis = Geom_Circle(gp_Circ(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 3.0))
    s = Geom_SurfaceOfLinearExtrusion(basis, gp_Dir(0.0, 0.0, 1.0))
    v = 5.0
    res = s.EvalD0(math.pi / 3.0, v)
    assert abs(math.hypot(res.X(), res.Y()) - 3.0) <= TOL
    assert abs(res.Z() - v) <= TOL


def test_Geom_SurfaceEvalTest_RevolutionSurface_EvalD1_ValidResults():
    gen = Geom_Line(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    s = Geom_SurfaceOfRevolution(gen, gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    v = 2.0
    d1 = s.EvalD1(math.pi / 4.0, v)
    assert abs(math.hypot(d1.Point.X(), d1.Point.Y()) - 1.0) <= TOL
    assert abs(d1.Point.Z() - v) <= TOL
    assert d1.D1U.Magnitude() > TOL
    assert abs(d1.D1V.X()) <= TOL
    assert abs(d1.D1V.Y()) <= TOL
    assert abs(d1.D1V.Z() - 1.0) <= TOL
