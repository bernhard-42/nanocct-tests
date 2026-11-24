# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_Curve2d_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: SamplingHelpers2d_MatchesLegacyPolicy (calls GeomBndLib_SamplingHelpers::ComputeNbSamples2d, a
# namespace function of the private header GeomBndLib_SamplingHelpers.pxx, which is in no installed header).
import math

from nanocct.Bnd import Bnd_Box2d
from nanocct.BndLib import BndLib_Add2dCurve
from nanocct.Geom2d import (Geom2d_BezierCurve, Geom2d_BSplineCurve, Geom2d_Circle, Geom2d_Ellipse, Geom2d_Hyperbola,
                            Geom2d_Line, Geom2d_Parabola, Geom2d_TrimmedCurve)
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomAbs import (GeomAbs_BezierCurve, GeomAbs_BSplineCurve, GeomAbs_Circle, GeomAbs_Ellipse,
                             GeomAbs_Hyperbola, GeomAbs_Line, GeomAbs_Parabola)
from nanocct.GeomBndLib import GeomBndLib_Curve2d
from nanocct.gp import gp_Ax2d, gp_Ax22d, gp_Dir2d, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi
KEYS = ("Xmin", "Xmax", "Ymin", "Ymax")


def _lim(box):
    lim = box.Get()
    return {k: getattr(lim, k) for k in KEYS}


def _compare(new, old, tol):
    n, o = _lim(new), _lim(old)
    for k in KEYS:
        assert abs(n[k] - o[k]) <= tol, k


def _conservative_envelope(new, old, tol):
    n, o = _lim(new), _lim(old)
    assert n["Xmin"] <= o["Xmin"] + tol
    assert n["Xmax"] >= o["Xmax"] - tol
    assert n["Ymin"] <= o["Ymin"] + tol
    assert n["Ymax"] >= o["Ymax"] - tol


def _near(box, **exp):
    lim = _lim(box)
    for k, v in exp.items():
        assert abs(lim[k] - v) <= CONF, k


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a.SetValue(i, v)
    return a


def _circle(radius, center=(0.0, 0.0)):
    return Geom2d_Circle(gp_Ax2d(gp_Pnt2d(*center), gp_Dir2d(1.0, 0.0)), radius)


def _ax22d():
    return gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0), gp_Dir2d(0.0, 1.0))


def _bspline():
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(2.0, 5.0), gp_Pnt2d(8.0, 5.0), gp_Pnt2d(10.0, 0.0)])
    knots = _arr(float, [0.0, 0.5, 1.0])
    mults = _arr(int, [3, 1, 3])
    return Geom2d_BSplineCurve(poles, knots, mults, 2)


# ---- Line2d ------------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_Line_FiniteSegment():
    curve = GeomBndLib_Curve2d(Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 1.0)))
    assert curve.GetType() == GeomAbs_Line
    b = Bnd_Box2d()
    curve.Add(0.0, 10.0, 0.0, b)
    length = 10.0 / math.sqrt(2.0)
    _near(b, Xmin=0.0, Ymin=0.0, Xmax=length, Ymax=length)


def test_GeomBndLib_Curve2dTest_Line_CompareWithBndLib():
    line = Geom2d_Line(gp_Pnt2d(1.0, 2.0), gp_Dir2d(0.0, 1.0))
    adaptor = Geom2dAdaptor_Curve(line)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(line).Add(0.0, 5.0, CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, 0.0, 5.0, CONF, old)
    _compare(new, old, CONF)


# ---- Circle2d ----------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_Circle_Full():
    radius = 5.0
    curve = GeomBndLib_Curve2d(_circle(radius))
    assert curve.GetType() == GeomAbs_Circle
    b = Bnd_Box2d()
    curve.Add(0.0, b)
    _near(b, Xmin=-radius, Ymin=-radius, Xmax=radius, Ymax=radius)


def test_GeomBndLib_Curve2dTest_Circle_Arc():
    radius = 10.0
    curve = GeomBndLib_Curve2d(_circle(radius))
    b = Bnd_Box2d()
    curve.Add(0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0.0, Ymin=0.0, Xmax=radius, Ymax=radius)


def test_GeomBndLib_Curve2dTest_Circle_CompareWithBndLib():
    circle = _circle(7.5)
    adaptor = Geom2dAdaptor_Curve(circle)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(circle).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _compare(new, old, CONF)


# ---- Ellipse2d ---------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_Ellipse_Full():
    maj, mnr = 10.0, 5.0
    curve = GeomBndLib_Curve2d(Geom2d_Ellipse(_ax22d(), maj, mnr))
    assert curve.GetType() == GeomAbs_Ellipse
    b = Bnd_Box2d()
    curve.Add(0.0, b)
    _near(b, Xmin=-maj, Xmax=maj, Ymin=-mnr, Ymax=mnr)


def test_GeomBndLib_Curve2dTest_Ellipse_CompareWithBndLib():
    ellipse = Geom2d_Ellipse(_ax22d(), 8.0, 3.0)
    adaptor = Geom2dAdaptor_Curve(ellipse)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(ellipse).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _compare(new, old, CONF)


# ---- Hyperbola2d -------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_Hyperbola_FiniteArc():
    maj, mnr = 5.0, 3.0
    curve = GeomBndLib_Curve2d(Geom2d_Hyperbola(_ax22d(), maj, mnr))
    assert curve.GetType() == GeomAbs_Hyperbola
    b = Bnd_Box2d()
    u = 1.0
    curve.Add(-u, u, 0.0, b)
    lim = _lim(b)
    x_end = maj * math.cosh(u)
    y_end = mnr * math.sinh(u)
    assert lim["Xmin"] <= maj + CONF
    assert lim["Xmax"] >= x_end - CONF
    assert lim["Ymin"] <= -y_end + CONF
    assert lim["Ymax"] >= y_end - CONF


def test_GeomBndLib_Curve2dTest_Hyperbola_CompareWithBndLib():
    hyp = Geom2d_Hyperbola(_ax22d(), 5.0, 3.0)
    adaptor = Geom2dAdaptor_Curve(hyp)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(hyp).Add(-1.0, 1.0, CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, -1.0, 1.0, CONF, old)
    _compare(new, old, CONF)


# ---- Parabola2d --------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_Parabola_FiniteArc():
    focal = 2.0
    curve = GeomBndLib_Curve2d(Geom2d_Parabola(_ax22d(), focal))
    assert curve.GetType() == GeomAbs_Parabola
    b = Bnd_Box2d()
    u = 5.0
    curve.Add(-u, u, 0.0, b)
    lim = _lim(b)
    x_end = u * u / (4.0 * focal)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= x_end - CONF
    assert lim["Ymin"] <= -u + CONF
    assert lim["Ymax"] >= u - CONF


def test_GeomBndLib_Curve2dTest_Parabola_CompareWithBndLib():
    parab = Geom2d_Parabola(_ax22d(), 2.0)
    adaptor = Geom2dAdaptor_Curve(parab)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(parab).Add(-5.0, 5.0, CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, -5.0, 5.0, CONF, old)
    _compare(new, old, CONF)


# ---- BezierCurve2d -----------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_BezierCurve_Simple():
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(5.0, 10.0), gp_Pnt2d(10.0, 0.0)])
    curve = GeomBndLib_Curve2d(Geom2d_BezierCurve(poles))
    assert curve.GetType() == GeomAbs_BezierCurve
    b = Bnd_Box2d()
    curve.Add(CONF, b)
    lim = _lim(b)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= 10.0 - CONF
    assert lim["Ymin"] <= CONF
    assert lim["Ymax"] >= 0.0


def test_GeomBndLib_Curve2dTest_BezierCurve_CompareWithBndLib():
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(3.0, 8.0), gp_Pnt2d(7.0, 2.0), gp_Pnt2d(10.0, 5.0)])
    bez = Geom2d_BezierCurve(poles)
    adaptor = Geom2dAdaptor_Curve(bez)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(bez).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    n, o = _lim(new), _lim(old)
    assert n["Xmin"] >= o["Xmin"] - CONF
    assert n["Xmax"] <= o["Xmax"] + CONF
    assert n["Ymin"] >= o["Ymin"] - CONF
    assert n["Ymax"] <= o["Ymax"] + CONF


# ---- BSplineCurve2d ----------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_BSplineCurve_Simple():
    curve = GeomBndLib_Curve2d(_bspline())
    assert curve.GetType() == GeomAbs_BSplineCurve
    b = Bnd_Box2d()
    curve.Add(CONF, b)
    lim = _lim(b)
    assert lim["Xmin"] <= CONF
    assert lim["Xmax"] >= 10.0 - CONF
    assert lim["Ymin"] <= CONF
    assert lim["Ymax"] >= 0.0


def test_GeomBndLib_Curve2dTest_BSplineCurve_CompareWithBndLib():
    bspl = _bspline()
    adaptor = Geom2dAdaptor_Curve(bspl)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(bspl).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _compare(new, old, CONF)


# ---- Adaptor constructor -----------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_AdaptorConstructor_Circle():
    circle = _circle(5.0)
    box_h = Bnd_Box2d()
    GeomBndLib_Curve2d(circle).Add(CONF, box_h)
    adaptor = Geom2dAdaptor_Curve(circle)
    curve_a = GeomBndLib_Curve2d(adaptor)
    assert curve_a.GetType() == GeomAbs_Circle
    box_a = Bnd_Box2d()
    curve_a.Add(CONF, box_a)
    _compare(box_h, box_a, CONF)


# ---- AddOptimal --------------------------------------------------------------------------------

def test_GeomBndLib_Curve2dTest_AddOptimal_Circle():
    radius = 5.0
    curve = GeomBndLib_Curve2d(_circle(radius))
    b = Bnd_Box2d()
    curve.AddOptimal(0.0, b)
    _near(b, Xmin=-radius, Ymin=-radius, Xmax=radius, Ymax=radius)


def test_GeomBndLib_Curve2dTest_AdaptorConstructor_TrimmedRangeUsedForFullAdd():
    adaptor = Geom2dAdaptor_Curve(_circle(10.0), 0.0, PI / 2.0)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(adaptor).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _compare(new, old, CONF)


def test_GeomBndLib_Curve2dTest_TrimmedCurveHandle_Fallback_CompareWithBndLib():
    trim = Geom2d_TrimmedCurve(_circle(10.0), 0.0, PI / 2.0)
    adaptor = Geom2dAdaptor_Curve(trim)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(trim).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    assert not new.IsVoid()
    _conservative_envelope(new, old, CONF)


def test_GeomBndLib_Curve2dTest_TrimmedCurveHandle_UsesBasisSpecialization():
    trim = Geom2d_TrimmedCurve(_circle(10.0), 0.0, PI / 2.0)
    curve = GeomBndLib_Curve2d(trim)
    assert curve.GetType() == GeomAbs_Circle
    adaptor = Geom2dAdaptor_Curve(trim)
    new = Bnd_Box2d()
    curve.Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _compare(new, old, CONF)
