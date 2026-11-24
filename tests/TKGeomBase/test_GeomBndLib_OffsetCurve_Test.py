# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomBndLib_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box
from nanocct.BndLib import BndLib_Add3dCurve
from nanocct.Geom import Geom_BSplineCurve, Geom_Circle, Geom_Ellipse, Geom_Line, Geom_OffsetCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomBndLib import GeomBndLib_Curve
from nanocct.gp import gp, gp_Ax2, gp_Dir, gp_Pnt
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
            assert n[k] >= o[k] - tol, f"New {k} is smaller than old"
        else:
            assert n[k] <= o[k] + tol, f"New {k} is larger than old"


def _contains_curve(box, curve, u1, u2, nb_samples):
    step = (u2 - u1) / nb_samples
    lim = _lim(box)
    for i in range(nb_samples + 1):
        u = u1 + i * step
        p = curve.Value(u)
        assert lim["Xmin"] - CONF <= p.X() <= lim["Xmax"] + CONF, f"Point outside box at U={u}"
        assert lim["Ymin"] - CONF <= p.Y() <= lim["Ymax"] + CONF, f"Point outside box at U={u}"
        assert lim["Zmin"] - CONF <= p.Z() <= lim["Zmax"] + CONF, f"Point outside box at U={u}"


def _add_pair(off, *args):
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Curve(off).Add(*args, nb)
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(off), *args, ob)
    return nb, ob


def _add_optimal_pair(off, *args):
    nb, ob = Bnd_Box(), Bnd_Box()
    GeomBndLib_Curve(off).AddOptimal(*args, nb)
    BndLib_Add3dCurve.AddOptimal_s(GeomAdaptor_Curve(off), *args, ob)
    return nb, ob


# Circle offset in Z direction (displacement in XY plane)

def test_GeomBndLib_OffsetCurveTest_CircleOffsetZ_Full_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 5.0), 2.0, gp.DZ_s())
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


def test_GeomBndLib_OffsetCurveTest_CircleOffsetZ_Arc_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 5.0), 3.0, gp.DZ_s())
    nb, ob = _add_pair(off, 0.0, PI / 2.0, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, PI / 2.0, 50)


# Circle offset in X direction (displacement in YZ plane)

def test_GeomBndLib_OffsetCurveTest_CircleOffsetX_Full_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 7.0), 2.0, gp.DX_s())
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


def test_GeomBndLib_OffsetCurveTest_CircleOffsetX_Arc_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 7.0), 4.0, gp.DX_s())
    nb, ob = _add_pair(off, PI / 4.0, 3.0 * PI / 4.0, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, PI / 4.0, 3.0 * PI / 4.0, 50)


# Circle offset in Y direction: degenerate, the C++ checks only that the new box is not void

def test_GeomBndLib_OffsetCurveTest_CircleOffsetY_Full_Containment():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 3.0), 1.5, gp.DY_s())
    nb = Bnd_Box()
    GeomBndLib_Curve(off).Add(CONF, nb)
    assert nb.IsVoid() is False


# Circle offset in diagonal direction

def test_GeomBndLib_OffsetCurveTest_CircleOffsetDiagonal_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 5.0), 2.0, gp_Dir(1.0, 1.0, 1.0))
    nb, ob = _add_optimal_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


# Negative offset

def test_GeomBndLib_OffsetCurveTest_CircleNegativeOffset_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 10.0), -3.0, gp.DZ_s())
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


# Ellipse offset

def test_GeomBndLib_OffsetCurveTest_EllipseOffsetZ_Full_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Ellipse(gp.XOY_s(), 8.0, 3.0), 2.0, gp.DZ_s())
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


def test_GeomBndLib_OffsetCurveTest_EllipseOffsetX_Arc_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Ellipse(gp.XOY_s(), 8.0, 3.0), 1.5, gp.DX_s())
    nb, ob = _add_pair(off, 0.0, PI, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, PI, 50)


# Line offset

def test_GeomBndLib_OffsetCurveTest_LineOffset_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)), 3.0, gp.DZ_s())
    nb, ob = _add_pair(off, 0.0, 10.0, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 10.0, 50)


# BSpline offset

def test_GeomBndLib_OffsetCurveTest_BSplineOffset_CompareWithBndLib():
    poles = NCollection_Array1[gp_Pnt](1, 4)
    for i, p in enumerate([(0.0, 0.0, 0.0), (3.0, 5.0, 1.0), (7.0, -2.0, 2.0), (10.0, 0.0, 0.0)], 1):
        poles.SetValue(i, gp_Pnt(*p))
    knots = NCollection_Array1[float](1, 3)
    for i, k in enumerate([0.0, 0.5, 1.0], 1):
        knots.SetValue(i, k)
    mults = NCollection_Array1[int](1, 3)
    for i, m in enumerate([3, 1, 3], 1):
        mults.SetValue(i, m)
    off = Geom_OffsetCurve(Geom_BSplineCurve(poles, knots, mults, 2), 1.0, gp.DZ_s())
    nb, ob = _add_optimal_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 1.0, 50)


# Large offset

def test_GeomBndLib_OffsetCurveTest_LargeOffset_CompareWithBndLib():
    off = Geom_OffsetCurve(Geom_Circle(gp.XOY_s(), 2.0), 20.0, gp.DZ_s())
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


# Non-planar circle with offset

def test_GeomBndLib_OffsetCurveTest_TiltedCircle_CompareWithBndLib():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(1.0, 1.0, 1.0)), 4.0)
    off = Geom_OffsetCurve(circle, 1.5, gp_Dir(1.0, 1.0, 1.0))
    nb, ob = _add_pair(off, CONF)
    _no_larger(nb, ob, CONF)
    _contains_curve(nb, off, 0.0, 2.0 * PI, 100)


def test_GeomBndLib_OffsetCurveTest_InfiniteRange_OpennessPreserved():
    off = Geom_OffsetCurve(Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)), 3.0, gp.DZ_s())
    nb, ob = _add_pair(off, -Precision.Infinite_s(), 10.0, CONF)
    assert nb.IsVoid() is False
    assert nb.IsOpenXmin() is True
    assert nb.IsOpenXmax() is False
    assert nb.IsOpenYmin() is False
    assert nb.IsOpenYmax() is False
    assert nb.IsOpenZmin() is False
    assert nb.IsOpenZmax() is False
    assert ob.IsOpenXmin() is True
