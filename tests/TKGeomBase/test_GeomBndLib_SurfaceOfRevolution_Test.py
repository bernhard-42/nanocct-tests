# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_SurfaceOfRevolution_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_AddSurface
from nanocct.Geom import (Geom_BSplineCurve, Geom_Circle, Geom_Ellipse, Geom_Line, Geom_Parabola,
                          Geom_SurfaceOfRevolution)
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.GeomBndLib import GeomBndLib_Surface
from nanocct.gp import gp, gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi
KEYS = ("Xmin", "Xmax", "Ymin", "Ymax", "Zmin", "Zmax")


def _lim(box):
    lim = box.Get()
    return {k: getattr(lim, k) for k in KEYS}


def _no_larger(new, old, tol):
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


def _compare(rev, rng, nu, nv):
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Surface(rev).Add(*rng, CONF, nb)
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(rev), *rng, CONF, ob)
    _no_larger(nb, ob, 0.5)
    _contains(nb, rev, *rng, nu, nv)


def _z_axis():
    return gp_Ax1(gp.Origin_s(), gp.DZ_s())


def _line_rev(x=5.0):
    return Geom_SurfaceOfRevolution(Geom_Line(gp_Pnt(x, 0, 0), gp.DZ_s()), _z_axis())


def _circle_rev():
    return Geom_SurfaceOfRevolution(Geom_Circle(gp_Ax2(gp_Pnt(5, 0, 0), gp.DY_s(), gp.DX_s()), 2.0), _z_axis())


def _bspline_rev():
    poles = NCollection_Array1[gp_Pnt](1, 4)
    for i, p in enumerate([(3, 0, 0), (5, 0, 3), (4, 0, 7), (6, 0, 10)], 1):
        poles.SetValue(i, gp_Pnt(*p))
    knots = NCollection_Array1[float](1, 3)
    mults = NCollection_Array1[int](1, 3)
    for i, (k, m) in enumerate([(0.0, 3), (0.5, 1), (1.0, 3)], 1):
        knots.SetValue(i, k)
        mults.SetValue(i, m)
    return Geom_SurfaceOfRevolution(Geom_BSplineCurve(poles, knots, mults, 2), _z_axis())


def test_GeomBndLib_RevolutionTest_LineAroundZ_Full_CompareWithBndLib():
    _compare(_line_rev(), (0.0, 2.0 * PI, 0.0, 10.0), 36, 10)


def test_GeomBndLib_RevolutionTest_LineAroundZ_HalfTurn_CompareWithBndLib():
    _compare(_line_rev(), (0.0, PI, 0.0, 5.0), 18, 5)


def test_GeomBndLib_RevolutionTest_InfiniteV_OpenInAxisDirection():
    b = Bnd_Box()
    GeomBndLib_Surface(_line_rev()).Add(0.0, 2.0 * PI, -Precision.Infinite_s(), Precision.Infinite_s(), CONF, b)
    assert not b.IsVoid()
    assert not b.IsWhole()
    assert not b.IsOpenXmin()
    assert not b.IsOpenXmax()
    assert not b.IsOpenYmin()
    assert not b.IsOpenYmax()
    assert b.IsOpenZmin()
    assert b.IsOpenZmax()
    lim, tol = _lim(b), 2.0 * CONF
    for k, v in {"Xmin": -5.0, "Xmax": 5.0, "Ymin": -5.0, "Ymax": 5.0}.items():
        assert abs(lim[k] - v) <= tol, k


def test_GeomBndLib_RevolutionTest_LineAroundZ_QuarterTurn_CompareWithBndLib():
    _compare(_line_rev(), (0.0, PI / 2.0, 0.0, 5.0), 9, 5)


def test_GeomBndLib_RevolutionTest_LineAroundX_Full_CompareWithBndLib():
    rev = Geom_SurfaceOfRevolution(Geom_Line(gp_Pnt(0, 3, 0), gp.DX_s()), gp_Ax1(gp.Origin_s(), gp.DX_s()))
    _compare(rev, (0.0, 2.0 * PI, 0.0, 8.0), 36, 10)


def test_GeomBndLib_RevolutionTest_LineAroundTiltedAxis_CompareWithBndLib():
    rev = Geom_SurfaceOfRevolution(Geom_Line(gp_Pnt(4, 0, 0), gp.DZ_s()), gp_Ax1(gp.Origin_s(), gp_Dir(1, 1, 0)))
    _compare(rev, (0.0, 2.0 * PI, 0.0, 5.0), 36, 10)


def test_GeomBndLib_RevolutionTest_CircleAroundZ_Full_CompareWithBndLib():
    _compare(_circle_rev(), (0.0, 2.0 * PI, 0.0, 2.0 * PI), 36, 36)


def test_GeomBndLib_RevolutionTest_CircleAroundZ_HalfTurn_CompareWithBndLib():
    _compare(_circle_rev(), (0.0, PI, 0.0, 2.0 * PI), 18, 36)


def test_GeomBndLib_RevolutionTest_ParabolaAroundZ_CompareWithBndLib():
    rev = Geom_SurfaceOfRevolution(Geom_Parabola(gp.XOY_s(), 2.0), _z_axis())
    _compare(rev, (0.0, 2.0 * PI, -3.0, 3.0), 36, 10)


def test_GeomBndLib_RevolutionTest_EllipseAroundZ_CompareWithBndLib():
    el = Geom_Ellipse(gp_Ax2(gp_Pnt(5, 0, 0), gp.DY_s(), gp.DX_s()), 3.0, 1.5)
    _compare(Geom_SurfaceOfRevolution(el, _z_axis()), (0.0, 2.0 * PI, 0.0, 2.0 * PI), 36, 36)


def test_GeomBndLib_RevolutionTest_BSplineAroundZ_CompareWithBndLib():
    _compare(_bspline_rev(), (0.0, 2.0 * PI, 0.0, 1.0), 36, 10)


def test_GeomBndLib_RevolutionTest_BSplineAroundZ_HalfTurn_CompareWithBndLib():
    _compare(_bspline_rev(), (0.0, PI, 0.0, 1.0), 18, 10)


def test_GeomBndLib_RevolutionTest_LineSmallRadius_CompareWithBndLib():
    _compare(_line_rev(0.5), (0.0, 2.0 * PI, -5.0, 5.0), 36, 10)


def test_GeomBndLib_RevolutionTest_LineLargeRadius_CompareWithBndLib():
    _compare(_line_rev(100.0), (0.0, 2.0 * PI, 0.0, 10.0), 36, 10)


def test_GeomBndLib_RevolutionTest_LineAroundZ_PartialV_CompareWithBndLib():
    _compare(_line_rev(), (0.0, 2.0 * PI, 3.0, 7.0), 36, 10)
