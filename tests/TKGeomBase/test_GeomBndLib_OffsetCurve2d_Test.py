# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_OffsetCurve2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box2d
from nanocct.BndLib import BndLib_Add2dCurve
from nanocct.Geom2d import Geom2d_BSplineCurve, Geom2d_Circle, Geom2d_Ellipse, Geom2d_Line, Geom2d_OffsetCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomBndLib import GeomBndLib_Curve2d
from nanocct.gp import gp_Ax2d, gp_Ax22d, gp_Dir2d, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
PI = math.pi


def _no_larger(new, old, tol=CONF):
    n, o = new.Get(), old.Get()
    assert n.Xmin >= o.Xmin - tol, "New Xmin is smaller than old"
    assert n.Xmax <= o.Xmax + tol, "New Xmax is larger than old"
    assert n.Ymin >= o.Ymin - tol, "New Ymin is smaller than old"
    assert n.Ymax <= o.Ymax + tol, "New Ymax is larger than old"


def _contains(box, curve, u1, u2, nb_samples):
    step = (u2 - u1) / nb_samples
    xmin, ymin, xmax, ymax = box.Get__float__float__float__float()
    for i in range(nb_samples + 1):
        u = u1 + i * step
        p = curve.Value(u)
        assert p.X() >= xmin - CONF, f"Point outside box at U={u}"
        assert p.X() <= xmax + CONF, f"Point outside box at U={u}"
        assert p.Y() >= ymin - CONF, f"Point outside box at U={u}"
        assert p.Y() <= ymax + CONF, f"Point outside box at U={u}"


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a.SetValue(i, v)
    return a


def _circle(radius, center=(0.0, 0.0)):
    return Geom2d_Circle(gp_Ax2d(gp_Pnt2d(*center), gp_Dir2d(1.0, 0.0)), radius)


def _ellipse():
    return Geom2d_Ellipse(gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0), gp_Dir2d(0.0, 1.0)), 8.0, 3.0)


def _compare_full(off, nb_samples):
    adaptor = Geom2dAdaptor_Curve(off)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(off).Add(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, CONF, old)
    _no_larger(new, old, CONF)
    _contains(new, off, 0.0, 2.0 * PI, nb_samples)


def _compare_arc(off, u1, u2, nb_samples):
    adaptor = Geom2dAdaptor_Curve(off)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(off).Add(u1, u2, CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(adaptor, u1, u2, CONF, old)
    _no_larger(new, old, CONF)
    _contains(new, off, u1, u2, nb_samples)


# ---- Circle offset (positive) ------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_Circle_PositiveOffset_Full_CompareWithBndLib():
    _compare_full(Geom2d_OffsetCurve(_circle(5.0), 2.0), 100)


def test_GeomBndLib_OffsetCurve2dTest_Circle_PositiveOffset_Arc_CompareWithBndLib():
    _compare_arc(Geom2d_OffsetCurve(_circle(5.0), 2.0), 0.0, PI / 2.0, 50)


# ---- Circle offset (negative) ------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_Circle_NegativeOffset_Full_CompareWithBndLib():
    _compare_full(Geom2d_OffsetCurve(_circle(10.0), -3.0), 100)


def test_GeomBndLib_OffsetCurve2dTest_Circle_NegativeOffset_Arc_CompareWithBndLib():
    _compare_arc(Geom2d_OffsetCurve(_circle(10.0), -3.0), PI / 4.0, PI, 50)


# ---- Ellipse offset ----------------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_Ellipse_Full_CompareWithBndLib():
    _compare_full(Geom2d_OffsetCurve(_ellipse(), 1.5), 100)


def test_GeomBndLib_OffsetCurve2dTest_Ellipse_Arc_OptimalCompareWithBndLib():
    off = Geom2d_OffsetCurve(_ellipse(), 1.5)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(off).AddOptimal(0.0, PI, CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.AddOptimal_s(off, 0.0, PI, CONF, old)
    _no_larger(new, old, CONF)
    _contains(new, off, 0.0, PI, 50)


# ---- Line offset -------------------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_Line_CompareWithBndLib():
    off = Geom2d_OffsetCurve(Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 3.0)
    _compare_arc(off, 0.0, 10.0, 50)


# ---- BSpline offset ----------------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_BSpline_OptimalCompareWithBndLib():
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(3.0, 5.0), gp_Pnt2d(7.0, -2.0), gp_Pnt2d(10.0, 0.0)])
    knots = _arr(float, [0.0, 0.5, 1.0])
    mults = _arr(int, [3, 1, 3])
    off = Geom2d_OffsetCurve(Geom2d_BSplineCurve(poles, knots, mults, 2), 1.0)
    new = Bnd_Box2d()
    GeomBndLib_Curve2d(off).AddOptimal(CONF, new)
    old = Bnd_Box2d()
    BndLib_Add2dCurve.AddOptimal_s(off, 0.0, 1.0, CONF, old)
    _no_larger(new, old, CONF)
    _contains(new, off, 0.0, 1.0, 50)


# ---- Large offset ------------------------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_LargeOffset_CompareWithBndLib():
    _compare_full(Geom2d_OffsetCurve(_circle(2.0), 20.0), 100)


# ---- Off-center circle with offset -------------------------------------------------------------

def test_GeomBndLib_OffsetCurve2dTest_OffCenterCircle_CompareWithBndLib():
    _compare_full(Geom2d_OffsetCurve(_circle(4.0, (5.0, 3.0)), 1.0), 100)
