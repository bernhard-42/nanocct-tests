# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: SamplingHelpers3d_MatchesLegacyPolicy (calls GeomBndLib_SamplingHelpers::ComputeNbSamples from the
# private header GeomBndLib_SamplingHelpers.pxx, which no installed header declares).
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_Add3dCurve
from nanocct.Geom import (Geom_BezierCurve, Geom_BSplineCurve, Geom_Circle, Geom_Ellipse, Geom_Hyperbola, Geom_Line,
                          Geom_Parabola, Geom_TrimmedCurve)
from nanocct.GeomAbs import (GeomAbs_BezierCurve, GeomAbs_BSplineCurve, GeomAbs_Circle, GeomAbs_Ellipse,
                             GeomAbs_Hyperbola, GeomAbs_Line, GeomAbs_Parabola)
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomBndLib import GeomBndLib_Curve
from nanocct.gp import gp, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
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


def _conservative_envelope(new, old, tol):
    n, o = _lim(new), _lim(old)
    for k in KEYS:
        if k.endswith("min"):
            assert n[k] <= o[k] + tol, k
        else:
            assert n[k] >= o[k] - tol, k


def _near(box, **exp):
    lim = _lim(box)
    for k, v in exp.items():
        assert abs(lim[k] - v) <= CONF, k


def _new(curve, *args):
    b = Bnd_Box()
    GeomBndLib_Curve(curve).Add(*args, b)
    return b


def _old(adaptor, *args):
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(adaptor, *args, b)
    return b


def _array_pnt(pts):
    arr = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        arr.SetValue(i, gp_Pnt(*p))
    return arr


def _array(cls, values):
    arr = NCollection_Array1[cls](1, len(values))
    for i, v in enumerate(values, 1):
        arr.SetValue(i, v)
    return arr


# Line

def test_GeomBndLib_CurveTest_Line_FiniteSegment():
    c = GeomBndLib_Curve(Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 1.0, 0.0)))
    assert c.GetType() == GeomAbs_Line
    b = Bnd_Box()
    c.Add(0.0, 10.0, 0.0, b)
    ln = 10.0 / math.sqrt(2.0)
    _near(b, Xmin=0.0, Ymin=0.0, Zmin=0.0, Xmax=ln, Ymax=ln, Zmax=0.0)


def test_GeomBndLib_CurveTest_Line_CompareWithBndLib():
    line = Geom_Line(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0))
    _compare(_new(line, 0.0, 5.0, CONF), _old(GeomAdaptor_Curve(line), 0.0, 5.0, CONF), CONF)


# Circle

def test_GeomBndLib_CurveTest_Circle_Full():
    r = 5.0
    c = GeomBndLib_Curve(Geom_Circle(gp.XOY_s(), r))
    assert c.GetType() == GeomAbs_Circle
    b = Bnd_Box()
    c.Add(0.0, b)
    _near(b, Xmin=-r, Ymin=-r, Xmax=r, Ymax=r, Zmin=0.0, Zmax=0.0)


def test_GeomBndLib_CurveTest_Circle_Arc():
    r = 10.0
    c = GeomBndLib_Curve(Geom_Circle(gp.XOY_s(), r))
    b = Bnd_Box()
    c.Add(0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0.0, Ymin=0.0, Xmax=r, Ymax=r, Zmin=0.0, Zmax=0.0)


def test_GeomBndLib_CurveTest_Circle_CompareWithBndLib():
    circle = Geom_Circle(gp.XOY_s(), 7.5)
    _compare(_new(circle, CONF), _old(GeomAdaptor_Curve(circle), CONF), CONF)


def test_GeomBndLib_CurveTest_Circle_Arc_CompareWithBndLib():
    circle = Geom_Circle(gp.XOY_s(), 7.5)
    _compare(_new(circle, 0.5, 2.5, CONF), _old(GeomAdaptor_Curve(circle), 0.5, 2.5, CONF), CONF)


# Ellipse

def test_GeomBndLib_CurveTest_Ellipse_Full():
    maj, mnr = 10.0, 5.0
    c = GeomBndLib_Curve(Geom_Ellipse(gp.XOY_s(), maj, mnr))
    assert c.GetType() == GeomAbs_Ellipse
    b = Bnd_Box()
    c.Add(0.0, b)
    _near(b, Xmin=-maj, Xmax=maj, Ymin=-mnr, Ymax=mnr, Zmin=0.0, Zmax=0.0)


def test_GeomBndLib_CurveTest_Ellipse_CompareWithBndLib():
    ell = Geom_Ellipse(gp.XOY_s(), 8.0, 3.0)
    _compare(_new(ell, CONF), _old(GeomAdaptor_Curve(ell), CONF), CONF)


def test_GeomBndLib_CurveTest_Ellipse_Arc_CompareWithBndLib():
    ell = Geom_Ellipse(gp.XOY_s(), 8.0, 3.0)
    _compare(_new(ell, 0.3, 2.0, CONF), _old(GeomAdaptor_Curve(ell), 0.3, 2.0, CONF), CONF)


# Hyperbola

def test_GeomBndLib_CurveTest_Hyperbola_FiniteArc():
    maj, mnr = 5.0, 3.0
    c = GeomBndLib_Curve(Geom_Hyperbola(gp.XOY_s(), maj, mnr))
    assert c.GetType() == GeomAbs_Hyperbola
    b = Bnd_Box()
    u = 1.0
    c.Add(-u, u, 0.0, b)
    lim = _lim(b)
    x_end = maj * math.cosh(u)
    y_end = mnr * math.sinh(u)
    assert lim["Xmin"] <= maj + CONF
    assert lim["Xmax"] >= x_end - CONF
    assert lim["Ymin"] <= -y_end + CONF
    assert lim["Ymax"] >= y_end - CONF


def test_GeomBndLib_CurveTest_Hyperbola_CompareWithBndLib():
    hyp = Geom_Hyperbola(gp.XOY_s(), 5.0, 3.0)
    _compare(_new(hyp, -1.0, 1.0, CONF), _old(GeomAdaptor_Curve(hyp), -1.0, 1.0, CONF), CONF)


# Parabola

def test_GeomBndLib_CurveTest_Parabola_FiniteArc():
    focal = 2.0
    c = GeomBndLib_Curve(Geom_Parabola(gp.XOY_s(), focal))
    assert c.GetType() == GeomAbs_Parabola
    b = Bnd_Box()
    u = 5.0
    c.Add(-u, u, 0.0, b)
    lim = _lim(b)
    x_end = u * u / (4.0 * focal)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= x_end - CONF
    assert lim["Ymin"] <= -u + CONF
    assert lim["Ymax"] >= u - CONF


def test_GeomBndLib_CurveTest_Parabola_CompareWithBndLib():
    parab = Geom_Parabola(gp.XOY_s(), 2.0)
    _compare(_new(parab, -5.0, 5.0, CONF), _old(GeomAdaptor_Curve(parab), -5.0, 5.0, CONF), CONF)


# BezierCurve

def test_GeomBndLib_CurveTest_BezierCurve_Simple():
    c = GeomBndLib_Curve(Geom_BezierCurve(_array_pnt([(0.0, 0.0, 0.0), (5.0, 10.0, 0.0), (10.0, 0.0, 0.0)])))
    assert c.GetType() == GeomAbs_BezierCurve
    b = Bnd_Box()
    c.Add(CONF, b)
    lim = _lim(b)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= 10.0 - CONF
    assert lim["Ymin"] <= CONF
    assert lim["Ymax"] >= 0.0
    assert abs(lim["Zmin"]) <= CONF
    assert abs(lim["Zmax"]) <= CONF


def test_GeomBndLib_CurveTest_BezierCurve_CompareWithBndLib():
    bez = Geom_BezierCurve(_array_pnt([(0.0, 0.0, 0.0), (3.0, 8.0, 1.0), (7.0, 2.0, -1.0), (10.0, 5.0, 0.0)]))
    _compare(_new(bez, CONF), _old(GeomAdaptor_Curve(bez), CONF), CONF)


# BSplineCurve

def _bspline(pts, knots, mults, degree):
    return Geom_BSplineCurve(_array_pnt(pts), _array(float, knots), _array(int, mults), degree)


def test_GeomBndLib_CurveTest_BSplineCurve_Simple():
    bsp = _bspline([(0.0, 0.0, 0.0), (2.0, 5.0, 0.0), (8.0, 5.0, 0.0), (10.0, 0.0, 0.0)], [0.0, 0.5, 1.0], [3, 1, 3], 2)
    c = GeomBndLib_Curve(bsp)
    assert c.GetType() == GeomAbs_BSplineCurve
    b = Bnd_Box()
    c.Add(CONF, b)
    lim = _lim(b)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= 10.0 - CONF
    assert lim["Ymin"] <= CONF
    assert lim["Ymax"] >= 0.0
    assert abs(lim["Zmin"]) <= CONF
    assert abs(lim["Zmax"]) <= CONF


def test_GeomBndLib_CurveTest_BSplineCurve_CompareWithBndLib():
    bsp = _bspline([(0.0, 0.0, 0.0), (2.0, 5.0, 1.0), (8.0, 5.0, -1.0), (10.0, 0.0, 0.0)], [0.0, 0.5, 1.0], [3, 1, 3], 2)
    _compare(_new(bsp, CONF), _old(GeomAdaptor_Curve(bsp), CONF), CONF)


def test_GeomBndLib_CurveTest_BSplineCurve_TrimmedRange_CompareWithBndLib():
    pts = [(0.0, 0.0, 0.0), (10.0, 20.0, 0.0), (20.0, -10.0, 5.0), (30.0, 40.0, 0.0), (40.0, 5.0, -5.0),
           (50.0, 15.0, 0.0), (60.0, 0.0, 0.0)]
    bsp = _bspline(pts, [0.0, 1.0, 2.0, 3.0, 4.0], [4, 1, 1, 1, 4], 3)
    u1, u2 = 1.82, 2.04
    _compare(_new(bsp, u1, u2, CONF), _old(GeomAdaptor_Curve(bsp), u1, u2, CONF), CONF)


# Adaptor constructor

def test_GeomBndLib_CurveTest_AdaptorConstructor_Circle():
    circle = Geom_Circle(gp.XOY_s(), 5.0)
    bh = _new(circle, CONF)
    ad = GeomAdaptor_Curve(circle)  # must outlive ca: GeomBndLib_Curve keeps a raw pointer to it
    ca = GeomBndLib_Curve(ad)
    assert ca.GetType() == GeomAbs_Circle
    ba = Bnd_Box()
    ca.Add(CONF, ba)
    _compare(bh, ba, CONF)


# AddOptimal

def test_GeomBndLib_CurveTest_AddOptimal_Circle():
    c = GeomBndLib_Curve(Geom_Circle(gp.XOY_s(), 5.0))
    b, bo = Bnd_Box(), Bnd_Box()
    c.Add(CONF, b)
    c.AddOptimal(CONF, bo)
    n, o = _lim(b), _lim(bo)
    for k in KEYS:
        if k.endswith("min"):
            assert o[k] >= n[k] - CONF, k
        else:
            assert o[k] <= n[k] + CONF, k


def test_GeomBndLib_CurveTest_AddOptimal_CompareWithBndLib():
    ell = Geom_Ellipse(gp.XOY_s(), 8.0, 3.0)
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Curve(ell).AddOptimal(CONF, nb)
    BndLib_Add3dCurve.AddOptimal_s(GeomAdaptor_Curve(ell), CONF, ob)
    _compare(nb, ob, CONF)


def test_GeomBndLib_CurveTest_AdaptorConstructor_TrimmedRangeUsedForFullAdd():
    ad = GeomAdaptor_Curve(Geom_Circle(gp.XOY_s(), 10.0), 0.0, PI / 2.0)
    _compare(_new(ad, CONF), _old(ad, CONF), CONF)


def test_GeomBndLib_CurveTest_TrimmedCurveHandle_Fallback_CompareWithBndLib():
    trim = Geom_TrimmedCurve(Geom_Circle(gp.XOY_s(), 10.0), 0.0, PI / 2.0)
    nb = _new(trim, CONF)
    ob = _old(GeomAdaptor_Curve(trim), CONF)
    assert nb.IsVoid() is False
    _conservative_envelope(nb, ob, CONF)


def test_GeomBndLib_CurveTest_TrimmedCurveHandle_UsesBasisSpecialization():
    trim = Geom_TrimmedCurve(Geom_Circle(gp.XOY_s(), 10.0), 0.0, PI / 2.0)
    c = GeomBndLib_Curve(trim)
    assert c.GetType() == GeomAbs_Circle
    nb = Bnd_Box()
    c.Add(CONF, nb)
    _compare(nb, _old(GeomAdaptor_Curve(trim), CONF), CONF)
