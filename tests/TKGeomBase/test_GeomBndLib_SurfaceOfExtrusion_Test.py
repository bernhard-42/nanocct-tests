# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_SurfaceOfExtrusion_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_AddSurface
from nanocct.Geom import Geom_BSplineCurve, Geom_Circle, Geom_Ellipse, Geom_Line, Geom_SurfaceOfLinearExtrusion
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomBndLib import GeomBndLib_Surface
from nanocct.gp import gp, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi
KEYS = ("Xmin", "Xmax", "Ymin", "Ymax", "Zmin", "Zmax")


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


def _compare(extr, rng, nu, nv, optimal=False):
    ad = GeomAdaptor_Surface(extr)
    nb, ob = Bnd_Box(), Bnd_Box()
    if optimal:
        GeomBndLib_Surface(extr).AddOptimal(*rng, CONF, nb)
        BndLib_AddSurface.AddOptimal_s(ad, *rng, CONF, ob)
    else:
        GeomBndLib_Surface(extr).Add(*rng, CONF, nb)
        BndLib_AddSurface.Add_s(ad, *rng, CONF, ob)
    _no_larger(nb, ob)
    _contains(nb, extr, *rng, nu, nv)


def _circle_z():
    return Geom_SurfaceOfLinearExtrusion(Geom_Circle(gp.XOY_s(), 5.0), gp.DZ_s())


def _ellipse_z():
    return Geom_SurfaceOfLinearExtrusion(Geom_Ellipse(gp.XOY_s(), 8.0, 3.0), gp.DZ_s())


def _bspline():
    poles = NCollection_Array1[gp_Pnt](1, 4)
    for i, p in enumerate([(0, 0, 0), (3, 5, 0), (7, -2, 0), (10, 3, 0)], 1):
        poles.SetValue(i, gp_Pnt(*p))
    knots = NCollection_Array1[float](1, 3)
    mults = NCollection_Array1[int](1, 3)
    for i, (k, m) in enumerate([(0.0, 3), (0.5, 1), (1.0, 3)], 1):
        knots.SetValue(i, k)
        mults.SetValue(i, m)
    return Geom_BSplineCurve(poles, knots, mults, 2)


def test_GeomBndLib_ExtrusionTest_CircleAlongZ_Full_CompareWithBndLib():
    _compare(_circle_z(), (0.0, 2.0 * PI, 0.0, 10.0), 36, 10)


def test_GeomBndLib_ExtrusionTest_CircleAlongZ_Arc_CompareWithBndLib():
    _compare(_circle_z(), (0.0, PI, 0.0, 5.0), 18, 5)


def test_GeomBndLib_ExtrusionTest_InfiniteU_OpenInExtrusionBasisDirection():
    extr = Geom_SurfaceOfLinearExtrusion(Geom_Line(gp_Pnt(5, 0, 0), gp.DZ_s()), gp.DX_s())
    b = Bnd_Box()
    GeomBndLib_Surface(extr).Add(-Precision.Infinite_s(), Precision.Infinite_s(), 0.0, 10.0, CONF, b)
    assert not b.IsVoid()
    assert not b.IsWhole()
    assert not b.IsOpenXmin()
    assert not b.IsOpenXmax()
    assert not b.IsOpenYmin()
    assert not b.IsOpenYmax()
    assert b.IsOpenZmin()
    assert b.IsOpenZmax()
    lim, tol = _lim(b), 2.0 * CONF
    assert abs(lim["Xmin"] - 5.0) <= tol
    assert abs(lim["Xmax"] - 15.0) <= tol
    assert abs(lim["Ymin"]) <= tol
    assert abs(lim["Ymax"]) <= tol


def test_GeomBndLib_ExtrusionTest_CircleAlongDiagonal_CompareWithBndLib():
    extr = Geom_SurfaceOfLinearExtrusion(Geom_Circle(gp.XOY_s(), 5.0), gp_Dir(1, 0, 1))
    _compare(extr, (0.0, 2.0 * PI, 0.0, 10.0), 36, 10)


def test_GeomBndLib_ExtrusionTest_EllipseAlongZ_CompareWithBndLib():
    _compare(_ellipse_z(), (0.0, 2.0 * PI, 0.0, 5.0), 36, 5)


def test_GeomBndLib_ExtrusionTest_EllipseAlongZ_Arc_CompareWithBndLib():
    _compare(_ellipse_z(), (0.0, PI, -2.0, 5.0), 18, 7)


def test_GeomBndLib_ExtrusionTest_LineAlongZ_CompareWithBndLib():
    extr = Geom_SurfaceOfLinearExtrusion(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), gp.DZ_s())
    _compare(extr, (0.0, 10.0, 0.0, 5.0), 10, 5)


def test_GeomBndLib_ExtrusionTest_LineAlongDiagonal_CompareWithBndLib():
    extr = Geom_SurfaceOfLinearExtrusion(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), gp_Dir(1, 0, 1))
    _compare(extr, (0.0, 5.0, 0.0, 10.0), 5, 10)


def test_GeomBndLib_ExtrusionTest_BSplineAlongZ_CompareWithBndLib():
    _compare(Geom_SurfaceOfLinearExtrusion(_bspline(), gp.DZ_s()), (0.0, 1.0, 0.0, 5.0), 10, 5, optimal=True)


def test_GeomBndLib_ExtrusionTest_BSplineAlongDiagonal_CompareWithBndLib():
    extr = Geom_SurfaceOfLinearExtrusion(_bspline(), gp_Dir(1, 1, 1))
    b = Bnd_Box()
    GeomBndLib_Surface(extr).AddOptimal(0.0, 1.0, -3.0, 7.0, CONF, b)
    s3 = math.sqrt(3.0)
    vmin, vmax, tol = -3.0 / s3, 7.0 / s3, 1e-3
    lim = _lim(b)
    exp = {"Xmin": vmin, "Xmax": 10.0 + vmax, "Ymin": vmin, "Ymax": 3.0 + vmax, "Zmin": vmin, "Zmax": vmax}
    for k, v in exp.items():
        assert abs(lim[k] - v) <= tol, k
    _contains(b, extr, 0.0, 1.0, -3.0, 7.0, 10, 10)


def test_GeomBndLib_ExtrusionTest_CircleNegativeV_CompareWithBndLib():
    _compare(_circle_z(), (0.0, 2.0 * PI, -5.0, 5.0), 36, 10)
