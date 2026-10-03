# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_Surface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_AddSurface
from nanocct.Geom import (Geom_BezierSurface, Geom_BSplineSurface, Geom_ConicalSurface, Geom_CylindricalSurface,
                          Geom_Plane, Geom_RectangularTrimmedSurface, Geom_SphericalSurface, Geom_ToroidalSurface)
from nanocct.GeomAbs import (GeomAbs_BezierSurface, GeomAbs_Cone, GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere,
                             GeomAbs_Torus)
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomBndLib import GeomBndLib_Surface
from nanocct.gp import gp, gp_Ax3, gp_Cone, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi
KEYS = ("Xmin", "Xmax", "Ymin", "Ymax", "Zmin", "Zmax")


def _lim(box):
    lim = box.Get()
    return {k: getattr(lim, k) for k in KEYS}


def _compare(new, old, tol):
    n, o = _lim(new), _lim(old)
    for k in KEYS:
        assert abs(n[k] - o[k]) <= tol, k


def _inside(inner, outer, tol=CONF):
    i, o = _lim(inner), _lim(outer)
    for k in KEYS:
        if k.endswith("min"):
            assert i[k] >= o[k] - tol, k
        else:
            assert i[k] <= o[k] + tol, k


def _near(box, **exp):
    lim = _lim(box)
    for k, v in exp.items():
        assert abs(lim[k] - v) <= CONF, k


def _old(surf_or_adaptor, *args):
    ad = surf_or_adaptor if isinstance(surf_or_adaptor, GeomAdaptor_Surface) else GeomAdaptor_Surface(surf_or_adaptor)
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(ad, *args, b)
    return b


def _new(src, *args):
    b = Bnd_Box()
    GeomBndLib_Surface(src).Add(*args, b)
    return b


def test_GeomBndLib_SurfaceTest_Plane_FinitePatch():
    s = GeomBndLib_Surface(Geom_Plane(gp.XOY_s()))
    assert s.GetType() == GeomAbs_Plane
    b = Bnd_Box()
    s.Add(-5.0, 5.0, -3.0, 3.0, 0.0, b)
    _near(b, Xmin=-5, Ymin=-3, Zmin=0, Xmax=5, Ymax=3, Zmax=0)


def test_GeomBndLib_SurfaceTest_Plane_CompareWithBndLib():
    p = Geom_Plane(gp.XOY_s())
    _compare(_new(p, -5.0, 5.0, -3.0, 3.0, CONF), _old(p, -5.0, 5.0, -3.0, 3.0, CONF), CONF)


def test_GeomBndLib_SurfaceTest_Cylinder_Patch():
    s = GeomBndLib_Surface(Geom_CylindricalSurface(gp.XOY_s(), 3.0))
    assert s.GetType() == GeomAbs_Cylinder
    b = Bnd_Box()
    s.Add(0.0, 2.0 * PI, 0.0, 10.0, CONF, b)
    _near(b, Xmin=-3, Ymin=-3, Zmin=0, Xmax=3, Ymax=3, Zmax=10)


def test_GeomBndLib_SurfaceTest_Cylinder_CompareWithBndLib():
    c = Geom_CylindricalSurface(gp.XOY_s(), 4.0)
    _compare(_new(c, 0.0, 2.0 * PI, -5.0, 5.0, CONF), _old(c, 0.0, 2.0 * PI, -5.0, 5.0, CONF), CONF)


def test_GeomBndLib_SurfaceTest_Cone_Patch():
    s = GeomBndLib_Surface(Geom_ConicalSurface(gp_Cone(gp_Ax3(gp.XOY_s()), PI / 4.0, 2.0)))
    assert s.GetType() == GeomAbs_Cone
    b = Bnd_Box()
    s.Add(0.0, 2.0 * PI, 0.0, 5.0, CONF, b)
    lim = _lim(b)
    r = 2.0 + 5.0 * math.sin(PI / 4.0)
    assert lim["Xmax"] >= r - CONF
    assert lim["Ymax"] >= r - CONF
    assert lim["Xmin"] <= -r + CONF
    assert lim["Ymin"] <= -r + CONF


def test_GeomBndLib_SurfaceTest_Cone_CompareWithBndLib():
    c = Geom_ConicalSurface(gp_Cone(gp_Ax3(gp.XOY_s()), PI / 6.0, 3.0))
    _compare(_new(c, 0.0, 2.0 * PI, 0.0, 5.0, CONF), _old(c, 0.0, 2.0 * PI, 0.0, 5.0, CONF), CONF)


def test_GeomBndLib_SurfaceTest_Sphere_Full():
    s = GeomBndLib_Surface(Geom_SphericalSurface(gp.XOY_s(), 5.0))
    assert s.GetType() == GeomAbs_Sphere
    b = Bnd_Box()
    s.Add(0.0, b)
    _near(b, Xmin=-5, Ymin=-5, Zmin=-5, Xmax=5, Ymax=5, Zmax=5)


def test_GeomBndLib_SurfaceTest_Sphere_Patch():
    b = _new(Geom_SphericalSurface(gp.XOY_s(), 5.0), 0.0, PI / 2.0, 0.0, PI / 2.0, CONF)
    lim = _lim(b)
    for k in ("Xmin", "Ymin", "Zmin"):
        assert lim[k] >= -CONF
    for k in ("Xmax", "Ymax", "Zmax"):
        assert lim[k] <= 5.0 + CONF


def test_GeomBndLib_SurfaceTest_Sphere_CompareWithBndLib():
    s = Geom_SphericalSurface(gp.XOY_s(), 7.0)
    _compare(_new(s, CONF), _old(s, CONF), CONF)


def test_GeomBndLib_SurfaceTest_Sphere_Patch_CompareWithBndLib():
    s = Geom_SphericalSurface(gp.XOY_s(), 7.0)
    args = (0.0, PI, -PI / 4.0, PI / 4.0, CONF)
    _compare(_new(s, *args), _old(s, *args), CONF)


def test_GeomBndLib_SurfaceTest_Torus_Full():
    s = GeomBndLib_Surface(Geom_ToroidalSurface(gp.XOY_s(), 10.0, 3.0))
    assert s.GetType() == GeomAbs_Torus
    b = Bnd_Box()
    s.Add(0.0, b)
    _near(b, Xmin=-13, Ymin=-13, Zmin=-3, Xmax=13, Ymax=13, Zmax=3)


def test_GeomBndLib_SurfaceTest_Torus_CompareWithBndLib():
    t = Geom_ToroidalSurface(gp.XOY_s(), 10.0, 3.0)
    _inside(_new(t, CONF), _old(t, CONF))


def test_GeomBndLib_SurfaceTest_Torus_Patch_CompareWithBndLib():
    t = Geom_ToroidalSurface(gp.XOY_s(), 10.0, 3.0)
    args = (0.0, PI, 0.0, PI, CONF)
    _inside(_new(t, *args), _old(t, *args))


def _bezier():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(10, 0, 0))
    poles.SetValue(2, 1, gp_Pnt(0, 10, 0))
    poles.SetValue(2, 2, gp_Pnt(10, 10, 5))
    return Geom_BezierSurface(poles)


def test_GeomBndLib_SurfaceTest_BezierSurface_Simple():
    s = GeomBndLib_Surface(_bezier())
    assert s.GetType() == GeomAbs_BezierSurface
    b = Bnd_Box()
    s.Add(CONF, b)
    lim = _lim(b)
    assert lim["Xmin"] <= CONF and lim["Xmax"] >= 10.0 - CONF
    assert lim["Ymin"] <= CONF and lim["Ymax"] >= 10.0 - CONF
    assert lim["Zmin"] <= CONF and lim["Zmax"] >= 5.0 - CONF


def test_GeomBndLib_SurfaceTest_BezierSurface_CompareWithBndLib():
    s = _bezier()
    _compare(_new(s, CONF), _old(s, CONF), CONF)


def test_GeomBndLib_SurfaceTest_BSplineSurface_CompareWithBndLib():
    pts = [[(0, 0, 0), (5, 0, 2), (10, 0, 0)], [(0, 5, 1), (5, 5, 5), (10, 5, 1)], [(0, 10, 0), (5, 10, 2), (10, 10, 0)]]
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i, row in enumerate(pts, 1):
        for j, p in enumerate(row, 1):
            poles.SetValue(i, j, gp_Pnt(*p))
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 3)
    mults.SetValue(2, 3)
    s = Geom_BSplineSurface(poles, knots, knots, mults, mults, 2, 2)
    _compare(_new(s, CONF), _old(s, CONF), CONF)


def test_GeomBndLib_SurfaceTest_AdaptorConstructor_Sphere():
    sph = Geom_SphericalSurface(gp.XOY_s(), 5.0)
    bh = _new(sph, CONF)
    ad = GeomAdaptor_Surface(sph)  # must outlive sa: GeomBndLib_Surface keeps a raw pointer to it
    sa = GeomBndLib_Surface(ad)
    assert sa.GetType() == GeomAbs_Sphere
    ba = Bnd_Box()
    sa.Add(CONF, ba)
    _compare(bh, ba, CONF)


def test_GeomBndLib_SurfaceTest_AddOptimal_Sphere():
    s = GeomBndLib_Surface(Geom_SphericalSurface(gp.XOY_s(), 5.0))
    b, bo = Bnd_Box(), Bnd_Box()
    s.Add(CONF, b)
    s.AddOptimal(CONF, bo)
    _inside(bo, b)


def test_GeomBndLib_SurfaceTest_AddOptimal_CompareWithBndLib():
    sph = Geom_SphericalSurface(gp.XOY_s(), 7.0)
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Surface(sph).AddOptimal(CONF, nb)
    BndLib_AddSurface.AddOptimal_s(GeomAdaptor_Surface(sph), CONF, ob)
    _compare(nb, ob, CONF)


def test_GeomBndLib_SurfaceTest_AddOptimal_Torus_TiltedBetterThanFast():
    torus = Geom_ToroidalSurface(gp_Ax3(gp.Origin_s(), gp_Dir(1, 0, 1)), 8.0, 3.0)
    fast, opt = Bnd_Box(), Bnd_Box()
    GeomBndLib_Surface(torus).Add(CONF, fast)
    GeomBndLib_Surface(torus).AddOptimal(CONF, opt)
    _inside(opt, fast)
    xz, y, tol = 8.0 / math.sqrt(2.0) + 3.0, 11.0, 10.0 * CONF
    o = _lim(opt)
    assert abs(o["Xmax"] - xz) <= tol
    assert abs(-o["Xmin"] - xz) <= tol
    assert abs(o["Ymax"] - y) <= tol
    assert abs(-o["Ymin"] - y) <= tol
    assert abs(o["Zmax"] - xz) <= tol
    assert abs(-o["Zmin"] - xz) <= tol


def test_GeomBndLib_SurfaceTest_AdaptorConstructor_TrimmedRangeUsedForFullAdd():
    ad = GeomAdaptor_Surface(Geom_SphericalSurface(gp.XOY_s(), 7.0), 0.0, PI, -PI / 4.0, PI / 4.0)
    _compare(_new(ad, CONF), _old(ad, CONF), CONF)


def test_GeomBndLib_SurfaceTest_TrimmedSurfaceHandle_Fallback_CompareWithBndLib():
    trim = Geom_RectangularTrimmedSurface(Geom_SphericalSurface(gp.XOY_s(), 7.0), 0.0, PI, -PI / 4.0, PI / 4.0)
    nb = _new(trim, CONF)
    assert not nb.IsVoid()
    _compare(nb, _old(trim, CONF), CONF)


def test_GeomBndLib_SurfaceTest_RectangularTrimmedSurface_UsesBasisSpecialization():
    trim = Geom_RectangularTrimmedSurface(Geom_SphericalSurface(gp.XOY_s(), 7.0), 0.0, PI, -PI / 4.0, PI / 4.0)
    s = GeomBndLib_Surface(trim)
    assert s.GetType() == GeomAbs_Sphere
    nb = Bnd_Box()
    s.Add(CONF, nb)
    _compare(nb, _old(trim, CONF), CONF)


def test_GeomBndLib_SurfaceTest_Torus_NegativeVMin_NoUnderBounding():
    torus = Geom_ToroidalSurface(gp.XOY_s(), 10.0, 3.0)
    u1, u2, v1, v2 = 0.0, 2.0 * PI, -PI / 8.0, PI / 8.0
    lim = _lim(_new(torus, u1, u2, v1, v2, CONF))
    for i in range(73):
        u = u1 + (u2 - u1) * i / 72.0
        for j in range(17):
            v = v1 + (v2 - v1) * j / 16.0
            p = torus.Value(u, v)
            assert lim["Xmin"] - CONF <= p.X() <= lim["Xmax"] + CONF
            assert lim["Ymin"] - CONF <= p.Y() <= lim["Ymax"] + CONF
            assert lim["Zmin"] - CONF <= p.Z() <= lim["Zmax"] + CONF
