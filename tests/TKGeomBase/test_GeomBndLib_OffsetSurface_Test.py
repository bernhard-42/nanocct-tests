# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_OffsetSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_AddSurface
from nanocct.Geom import (Geom_CylindricalSurface, Geom_OffsetSurface, Geom_Plane, Geom_SphericalSurface,
                          Geom_ToroidalSurface)
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomBndLib import GeomBndLib_Surface
from nanocct.gp import gp
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi
KEYS = ("Xmin", "Xmax", "Ymin", "Ymax", "Zmin", "Zmax")
SPHERE_RANGE = (0.0, 2.0 * PI, -PI / 2.0, PI / 2.0)


def _lim(box):
    lim = box.Get()
    return {k: getattr(lim, k) for k in KEYS}


def _no_larger(new, old, tol=CONF):
    n, o = _lim(new), _lim(old)
    for k in KEYS:
        if k.endswith("min"):
            assert n[k] >= o[k] - tol, k
        else:
            assert n[k] <= o[k] + tol, k


def _contains(box, surf, u0, u1, v0, v1, nu, nv):
    lim = _lim(box)
    for i in range(nu + 1):
        u = u0 + i * (u1 - u0) / nu
        for j in range(nv + 1):
            v = v0 + j * (v1 - v0) / nv
            p = surf.Value(u, v)
            assert lim["Xmin"] - CONF <= p.X() <= lim["Xmax"] + CONF
            assert lim["Ymin"] - CONF <= p.Y() <= lim["Ymax"] + CONF
            assert lim["Zmin"] - CONF <= p.Z() <= lim["Zmax"] + CONF


def _compare(off, rng, check_rng, nu, nv):
    """rng=() means the full-surface overloads."""
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Surface(off).Add(*rng, CONF, nb)
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(off), *rng, CONF, ob)
    _no_larger(nb, ob)
    _contains(nb, off, *check_rng, nu, nv)


def _optimal_vs_fast(off, rng, check_rng, nu, nv):
    fast, opt = Bnd_Box(), Bnd_Box()
    GeomBndLib_Surface(off).Add(*rng, CONF, fast)
    GeomBndLib_Surface(off).AddOptimal(*rng, CONF, opt)
    _no_larger(opt, fast)
    _contains(opt, off, *check_rng, nu, nv)


def _sphere(r, d):
    return Geom_OffsetSurface(Geom_SphericalSurface(gp.XOY_s(), r), d)


def _cyl(r, d):
    return Geom_OffsetSurface(Geom_CylindricalSurface(gp.XOY_s(), r), d)


def _plane(d):
    return Geom_OffsetSurface(Geom_Plane(gp.XOY_s()), d)


def _torus():
    return Geom_OffsetSurface(Geom_ToroidalSurface(gp.XOY_s(), 10.0, 3.0), 1.0)


def test_GeomBndLib_OffsetSurfaceTest_Sphere_PositiveOffset_Full_CompareWithBndLib():
    _compare(_sphere(5.0, 2.0), (), SPHERE_RANGE, 36, 18)


def test_GeomBndLib_OffsetSurfaceTest_Sphere_PositiveOffset_Patch_CompareWithBndLib():
    rng = (0.0, PI, -PI / 4.0, PI / 4.0)
    _compare(_sphere(5.0, 2.0), rng, rng, 18, 9)


def test_GeomBndLib_OffsetSurfaceTest_Sphere_NegativeOffset_Full_CompareWithBndLib():
    _compare(_sphere(10.0, -3.0), (), SPHERE_RANGE, 36, 18)


def test_GeomBndLib_OffsetSurfaceTest_Cylinder_Full_CompareWithBndLib():
    rng = (0.0, 2.0 * PI, -5.0, 5.0)
    _compare(_cyl(4.0, 1.5), rng, rng, 36, 10)


def test_GeomBndLib_OffsetSurfaceTest_Cylinder_Patch_CompareWithBndLib():
    rng = (0.0, PI, 0.0, 5.0)
    _compare(_cyl(4.0, 1.5), rng, rng, 18, 5)


def test_GeomBndLib_OffsetSurfaceTest_Cylinder_NegativeOffset_CompareWithBndLib():
    rng = (0.0, 2.0 * PI, 0.0, 10.0)
    _compare(_cyl(8.0, -2.0), rng, rng, 36, 10)


def test_GeomBndLib_OffsetSurfaceTest_Plane_PositiveOffset_CompareWithBndLib():
    rng = (-5.0, 5.0, -5.0, 5.0)
    _compare(_plane(3.0), rng, rng, 10, 10)


def test_GeomBndLib_OffsetSurfaceTest_Plane_PositiveOffset_Patch_IsNotArtificiallyThickenedInZ():
    b = Bnd_Box()
    GeomBndLib_Surface(_plane(3.0)).Add(-4.0, 6.0, -2.0, 7.0, CONF, b)
    lim = _lim(b)
    assert abs(lim["Zmin"] - (3.0 - CONF)) <= 1e-12
    assert abs(lim["Zmax"] - (3.0 + CONF)) <= 1e-12


def test_GeomBndLib_OffsetSurfaceTest_Plane_NegativeOffset_CompareWithBndLib():
    rng = (-10.0, 10.0, -10.0, 10.0)
    _compare(_plane(-5.0), rng, rng, 10, 10)


def test_GeomBndLib_OffsetSurfaceTest_Torus_PositiveOffset_CompareWithBndLib():
    rng = (0.0, 2.0 * PI, 0.0, 2.0 * PI)
    _compare(_torus(), rng, rng, 36, 36)


def test_GeomBndLib_OffsetSurfaceTest_Torus_Patch_CompareWithBndLib():
    rng = (0.0, PI, 0.0, PI)
    _compare(_torus(), rng, rng, 18, 18)


def test_GeomBndLib_OffsetSurfaceTest_Plane_BoxOptimal_TighterThanBox():
    rng = (-5.0, 5.0, -5.0, 5.0)
    _optimal_vs_fast(_plane(3.0), rng, rng, 10, 10)


def test_GeomBndLib_OffsetSurfaceTest_Torus_BoxOptimal_ContainsSurface():
    rng = (0.0, 2.0 * PI, 0.0, 2.0 * PI)
    _optimal_vs_fast(_torus(), rng, rng, 36, 36)


def test_GeomBndLib_OffsetSurfaceTest_Sphere_BoxOptimal_ContainsSurface():
    _optimal_vs_fast(_sphere(5.0, 2.0), (), SPHERE_RANGE, 36, 18)


def test_GeomBndLib_OffsetSurfaceTest_Sphere_LargeOffset_CompareWithBndLib():
    _compare(_sphere(2.0, 20.0), (), SPHERE_RANGE, 36, 18)
