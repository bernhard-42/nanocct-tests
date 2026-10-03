# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomAdaptor_TransformedSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import (
    Geom_BSplineSurface,
    Geom_Line,
    Geom_OffsetSurface,
    Geom_Plane,
    Geom_SphericalSurface,
    Geom_SurfaceOfLinearExtrusion,
    Geom_SurfaceOfRevolution,
)
from nanocct.GeomAbs import GeomAbs_Line, GeomAbs_Plane, GeomAbs_Sphere
from nanocct.GeomAdaptor import GeomAdaptor_Surface, GeomAdaptor_TransformedSurface
from nanocct.GeomGridEval import GeomGridEval_Surface
from nanocct.gp import gp, gp_Ax1, gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2

THE_TOLERANCE = 1.0e-10


def near(a, b, tol):
    return abs(a - b) <= tol


def translation(dx, dy, dz):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(dx, dy, dz))
    return t


def rotation_y(angle):
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)), angle)
    return t


def xoy_plane():
    return Geom_Plane(gp_Pln(gp_Ax3(gp.XOY_s())))


def bspline_surface():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, 1, gp_Pnt(1.0, 0.0, 0.0))
    poles.SetValue(1, 2, gp_Pnt(0.0, 1.0, 0.0))
    poles.SetValue(2, 2, gp_Pnt(1.0, 1.0, 1.0))
    uk = NCollection_Array1[float](1, 2)
    vk = NCollection_Array1[float](1, 2)
    um = NCollection_Array1[int](1, 2)
    vm = NCollection_Array1[int](1, 2)
    uk[1], uk[2] = 0.0, 1.0
    vk[1], vk[2] = 0.0, 1.0
    um[1], um[2] = 2, 2
    vm[1], vm[2] = 2, 2
    return Geom_BSplineSurface(poles, uk, vk, um, vm, 1, 1)


def test_GeomAdaptor_TransformedSurfaceTest_IdentityTransformUsesOriginalSurface():
    pl = xoy_plane()
    a = GeomAdaptor_TransformedSurface(pl, gp_Trsf())
    assert a.GeomSurfaceOriginal() is pl
    assert a.GeomSurfaceTransformed() is pl


def test_GeomAdaptor_TransformedSurfaceTest_PlaneCachesTransformedSurface():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), translation(0.0, 0.0, 5.0))
    first = a.GeomSurfaceTransformed()
    second = a.GeomSurfaceTransformed()
    assert first is second
    assert near(a.Plane().Location().Z(), 5.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_BSplineCachePreservedByShallowCopy():
    a = GeomAdaptor_TransformedSurface(bspline_surface(), translation(4.0, 0.0, 0.0))
    surf = a.GeomSurfaceTransformed()
    bs = a.BSpline()
    cp = a.ShallowCopy()
    assert isinstance(cp, GeomAdaptor_TransformedSurface)
    assert cp.GeomSurfaceTransformed() is surf
    assert cp.BSpline() is bs


def test_GeomAdaptor_TransformedSurfaceTest_ShallowCopyFromUnbuiltStateBuildsCacheLazily():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), translation(0.0, 0.0, 4.0))
    cp = a.ShallowCopy()
    assert isinstance(cp, GeomAdaptor_TransformedSurface)
    first = cp.GeomSurfaceTransformed()
    second = cp.GeomSurfaceTransformed()
    assert first is second
    assert near(cp.Plane().Location().Z(), 4.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_SetTrsfRebuildsCache():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), translation(0.0, 0.0, 1.0))
    first = a.GeomSurfaceTransformed()
    a.SetTrsf(translation(0.0, 0.0, 3.0))
    second = a.GeomSurfaceTransformed()
    assert first is not second
    assert near(a.Plane().Location().Z(), 3.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_LoadRebuildsCache():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), translation(0.0, 0.0, 2.0))
    first = a.GeomSurfaceTransformed()
    sph = Geom_SphericalSurface(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 3.0)
    a.Load(sph, gp_Trsf())
    second = a.GeomSurfaceTransformed()
    assert first is not second
    assert a.GetType() == GeomAbs_Sphere
    assert near(a.Sphere().Radius(), 3.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_ExtrusionCachesDirectionAndBasisCurve():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    ext = Geom_SurfaceOfLinearExtrusion(line, gp_Dir(0.0, 0.0, 1.0))
    a = GeomAdaptor_TransformedSurface(ext, rotation_y(math.pi / 2.0))
    d = a.Direction()
    assert near(d.X(), 1.0, THE_TOLERANCE)
    assert near(d.Y(), 0.0, THE_TOLERANCE)
    assert near(d.Z(), 0.0, THE_TOLERANCE)
    c = a.BasisCurve()
    assert c is not None
    assert c.GetType() == GeomAbs_Line


def test_GeomAdaptor_TransformedSurfaceTest_RevolutionCachesAxisAndBasisCurve():
    line = Geom_Line(gp_Pnt(2.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    rev = Geom_SurfaceOfRevolution(line, gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    a = GeomAdaptor_TransformedSurface(rev, rotation_y(math.pi / 2.0))
    ax = a.AxeOfRevolution()
    assert near(ax.Direction().X(), 1.0, THE_TOLERANCE)
    assert near(ax.Direction().Y(), 0.0, THE_TOLERANCE)
    assert near(ax.Direction().Z(), 0.0, THE_TOLERANCE)
    c = a.BasisCurve()
    assert c is not None
    assert c.GetType() == GeomAbs_Line


def test_GeomAdaptor_TransformedSurfaceTest_OffsetCachesBasisSurfaceAndOffsetValue():
    off = Geom_OffsetSurface(xoy_plane(), 2.5)
    a = GeomAdaptor_TransformedSurface(off, translation(0.0, 0.0, 3.0))
    basis = a.BasisSurface()
    assert basis is not None
    assert basis.GetType() == GeomAbs_Plane
    assert near(a.OffsetValue(), 2.5, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_UTrimPreservesRestrictedBounds():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), 2.0, 8.0, 3.0, 9.0, translation(0.0, 0.0, 5.0), 0.1, 0.2)
    t = a.UTrim(4.0, 6.0, 0.05)
    assert isinstance(t, GeomAdaptor_Surface)
    assert near(t.FirstUParameter(), 4.0, THE_TOLERANCE)
    assert near(t.LastUParameter(), 6.0, THE_TOLERANCE)
    assert near(t.FirstVParameter(), 3.0, THE_TOLERANCE)
    assert near(t.LastVParameter(), 9.0, THE_TOLERANCE)
    assert near(t.ToleranceU(), 0.05, THE_TOLERANCE)
    assert near(t.ToleranceV(), 0.2, THE_TOLERANCE)
    assert near(t.EvalD0(4.0, 3.0).Z(), 5.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_VTrimPreservesRestrictedBounds():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), 2.0, 8.0, 3.0, 9.0, translation(0.0, 0.0, 7.0), 0.1, 0.2)
    t = a.VTrim(4.0, 6.0, 0.15)
    assert isinstance(t, GeomAdaptor_Surface)
    assert near(t.FirstUParameter(), 2.0, THE_TOLERANCE)
    assert near(t.LastUParameter(), 8.0, THE_TOLERANCE)
    assert near(t.FirstVParameter(), 4.0, THE_TOLERANCE)
    assert near(t.LastVParameter(), 6.0, THE_TOLERANCE)
    assert near(t.ToleranceU(), 0.1, THE_TOLERANCE)
    assert near(t.ToleranceV(), 0.15, THE_TOLERANCE)
    assert near(t.EvalD0(2.0, 4.0).Z(), 7.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedSurfaceTest_GridEvalUsesTransformedGeometryOnlyOnce():
    a = GeomAdaptor_TransformedSurface(xoy_plane(), translation(0.0, 0.0, 5.0))
    ev = GeomGridEval_Surface(a)
    up = NCollection_Array1[float](1, 2)
    vp = NCollection_Array1[float](1, 2)
    up[1], up[2] = 0.0, 1.0
    vp[1], vp[2] = 0.0, 1.0
    grid = ev.EvaluateGrid(up, vp)
    assert near(grid.Value(1, 1).Z(), 5.0, THE_TOLERANCE)
    assert near(grid.Value(2, 2).Z(), 5.0, THE_TOLERANCE)
