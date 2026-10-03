# Translated from OCCT src/ModelingData/TKGeomBase/GTests/BndLib_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box, Bnd_Box2d
from nanocct.BndLib import BndLib, BndLib_Add2dCurve, BndLib_Add3dCurve, BndLib_AddSurface
from nanocct.Geom import (Geom_BezierCurve, Geom_BezierSurface, Geom_BSplineCurve, Geom_Circle, Geom_ConicalSurface,
                          Geom_CylindricalSurface, Geom_Ellipse, Geom_Line, Geom_Plane, Geom_SphericalSurface,
                          Geom_ToroidalSurface, Geom_TrimmedCurve)
from nanocct.Geom2d import Geom2d_BezierCurve, Geom2d_Circle, Geom2d_Ellipse, Geom2d_Line, Geom2d_TrimmedCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import (gp_Ax2, gp_Ax2d, gp_Ax3, gp_Circ, gp_Circ2d, gp_Cone, gp_Cylinder, gp_Dir, gp_Dir2d,
                        gp_Elips, gp_Elips2d, gp_Hypr, gp_Hypr2d, gp_Lin, gp_Lin2d, gp_Parab, gp_Parab2d, gp_Pnt,
                        gp_Pnt2d, gp_Sphere, gp_Torus)
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
INF = math.inf
PI = math.pi


def _near(box, tol=CONF, **expected):
    lim = box.Get()
    for name, exp in expected.items():
        got = getattr(lim, name)
        assert abs(got - exp) <= tol, f"{name}: {got} != {exp}"


def _ax2():
    return gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _ax3(p=(0, 0, 0)):
    return gp_Ax3(gp_Pnt(*p), gp_Dir(0, 0, 1))


def _ax2d(p=(0, 0)):
    return gp_Ax2d(gp_Pnt2d(*p), gp_Dir2d(1, 0))


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


# ---- Line --------------------------------------------------------------------------------------

def test_BndLibTest_Line_FiniteSegment():
    b = Bnd_Box()
    BndLib.Add_s(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0, 0.0, b)
    _near(b, Xmin=0, Xmax=10, Ymin=0, Ymax=0, Zmin=0, Zmax=0)


def test_BndLibTest_Line_PositiveDirection_NegativeInfinite():
    b = Bnd_Box()
    BndLib.Add_s(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -INF, 5.0, 0.0, b)
    assert b.IsOpenXmin()
    assert not b.IsOpenXmax()


def test_BndLibTest_Line_NegativeDirection_NegativeInfinite():
    b = Bnd_Box()
    BndLib.Add_s(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(-1, 0, 0)), -INF, 5.0, 0.0, b)
    assert b.IsOpenXmax()
    assert not b.IsOpenXmin()


def test_BndLibTest_Line_NegativeDirection_PositiveInfinite():
    b = Bnd_Box()
    BndLib.Add_s(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(-1, 0, 0)), -5.0, INF, 0.0, b)
    assert b.IsOpenXmin()
    assert not b.IsOpenXmax()


def test_BndLibTest_Line_DiagonalDirection_BothInfinite():
    b = Bnd_Box()
    BndLib.Add_s(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(-1, -1, -1)), -INF, INF, 0.0, b)
    assert b.IsOpenXmin() and b.IsOpenXmax()
    assert b.IsOpenYmin() and b.IsOpenYmax()
    assert b.IsOpenZmin() and b.IsOpenZmax()


# ---- Circle / Ellipse / Hyperbola / Parabola ---------------------------------------------------

def test_BndLibTest_Circle_Full():
    c = gp_Circ(_ax2(), 5.0)
    full, arc = Bnd_Box(), Bnd_Box()
    BndLib.Add_s(c, 0.0, full)
    _near(full, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=0)
    BndLib.Add_s(c, 0.0, 2.0 * PI, 0.0, arc)
    _near(arc, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5)


def test_BndLibTest_Circle_Arc_FirstQuadrant():
    b = Bnd_Box()
    BndLib.Add_s(gp_Circ(_ax2(), 5.0), 0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0, Xmax=5, Ymin=0, Ymax=5)


def test_BndLibTest_Circle_RotatedAxis():
    b = Bnd_Box()
    BndLib.Add_s(gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), 3.0), 0.0, b)
    _near(b, Xmin=-3, Xmax=3, Ymin=0, Ymax=0, Zmin=-3, Zmax=3)


def test_BndLibTest_Ellipse_Full():
    b = Bnd_Box()
    BndLib.Add_s(gp_Elips(_ax2(), 10.0, 5.0), 0.0, b)
    _near(b, Xmin=-10, Xmax=10, Ymin=-5, Ymax=5, Zmin=0, Zmax=0)


def test_BndLibTest_Ellipse_Arc():
    b = Bnd_Box()
    BndLib.Add_s(gp_Elips(_ax2(), 10.0, 5.0), 0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0, Xmax=10, Ymin=0, Ymax=5)


def test_BndLibTest_Hyperbola_SimpleArc():
    b = Bnd_Box()
    BndLib.Add_s(gp_Hypr(_ax2(), 3.0, 2.0), -1.0, 1.0, 0.0, b)
    _near(b, Xmin=3.0, Xmax=3.0 * math.cosh(1.0), Ymin=2.0 * math.sinh(-1.0), Ymax=2.0 * math.sinh(1.0))


def test_BndLibTest_Hyperbola_Rotated_MultipleExtrema():
    b = Bnd_Box()
    BndLib.Add_s(gp_Hypr(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 1, 1), gp_Dir(1, -1, 0)), 5.0, 3.0), -2.0, 2.0, 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Xmin < lim.Xmax
    assert lim.Ymin < lim.Ymax


def test_BndLibTest_Hyperbola_InfiniteParameter():
    b = Bnd_Box()
    BndLib.Add_s(gp_Hypr(_ax2(), 3.0, 2.0), 0.0, INF, 0.0, b)
    assert b.IsOpenXmax()
    assert b.IsOpenYmax()


def test_BndLibTest_Parabola_FiniteArc():
    b = Bnd_Box()
    BndLib.Add_s(gp_Parab(_ax2(), 2.0), -4.0, 4.0, 0.0, b)
    _near(b, Xmin=0, Xmax=2, Ymin=-4, Ymax=4)


def test_BndLibTest_Parabola_InfiniteParameter():
    b = Bnd_Box()
    BndLib.Add_s(gp_Parab(_ax2(), 2.0), 0.0, INF, 0.0, b)
    assert b.IsOpenXmax()
    assert b.IsOpenYmax()


# ---- Sphere / Cylinder / Cone / Torus ----------------------------------------------------------

def test_BndLibTest_Sphere_Full():
    b = Bnd_Box()
    BndLib.Add_s(gp_Sphere(_ax3(), 7.0), 0.0, b)
    _near(b, Xmin=-7, Xmax=7, Ymin=-7, Ymax=7, Zmin=-7, Zmax=7)


def test_BndLibTest_Sphere_Patch():
    b = Bnd_Box()
    BndLib.Add_s(gp_Sphere(_ax3(), 5.0), 0.0, 2.0 * PI, 0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=5)


def test_BndLibTest_Sphere_Translated():
    b = Bnd_Box()
    BndLib.Add_s(gp_Sphere(_ax3((10, 20, 30)), 3.0), 0.0, b)
    _near(b, Xmin=7, Xmax=13, Ymin=17, Ymax=23, Zmin=27, Zmax=33)


def test_BndLibTest_Cylinder_FinitePatch():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cylinder(_ax3(), 4.0), 0.0, 2.0 * PI, 0.0, 10.0, 0.0, b)
    _near(b, Xmin=-4, Xmax=4, Ymin=-4, Ymax=4, Zmin=0, Zmax=10)


def test_BndLibTest_Cylinder_InfiniteV():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cylinder(_ax3(), 4.0), 0.0, INF, 0.0, b)
    assert b.IsOpenZmax()
    assert not b.IsOpenZmin()


def test_BndLibTest_Cylinder_PartialU():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cylinder(_ax3(), 5.0), 0.0, PI / 2.0, 0.0, 10.0, 0.0, b)
    _near(b, Xmin=0, Xmax=5, Ymin=0, Ymax=5, Zmin=0, Zmax=10)


def test_BndLibTest_Cone_FinitePatch():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cone(_ax3(), PI / 4.0, 2.0), 0.0, 2.0 * PI, 0.0, 5.0, 0.0, b)
    r = 2.0 + 5.0 * math.sin(PI / 4.0)
    _near(b, Xmax=r, Ymax=r, Zmax=5.0 * math.cos(PI / 4.0), Zmin=0.0)


def test_BndLibTest_Cone_NegativeV():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cone(_ax3(), PI / 6.0, 3.0), 0.0, 2.0 * PI, -5.0, 0.0, 0.0, b)
    _near(b, Zmin=-5.0 * math.cos(PI / 6.0), Zmax=0.0)


def test_BndLibTest_Cone_InfiniteV():
    b = Bnd_Box()
    BndLib.Add_s(gp_Cone(_ax3(), PI / 4.0, 2.0), 0.0, INF, 0.0, b)
    assert b.IsOpenZmax()


def test_BndLibTest_Torus_Full():
    b = Bnd_Box()
    BndLib.Add_s(gp_Torus(_ax3(), 10.0, 3.0), 0.0, b)
    _near(b, Xmin=-13, Xmax=13, Ymin=-13, Ymax=13, Zmin=-3, Zmax=3)


def test_BndLibTest_Torus_Patch():
    b = Bnd_Box()
    BndLib.Add_s(gp_Torus(_ax3(), 10.0, 3.0), 0.0, PI / 2.0, 0.0, PI, 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Xmin >= -CONF
    assert lim.Ymin >= -CONF
    assert lim.Zmax <= 3.0 + CONF


def test_BndLibTest_Torus_NegativeVParameter():
    b = Bnd_Box()
    BndLib.Add_s(gp_Torus(_ax3(), 10.0, 3.0), 0.0, 2.0 * PI, -PI, 0.0, 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Zmin <= 0.0
    assert lim.Zmin >= -3.0 - CONF


def test_BndLibTest_Torus_LargeNegativeVParameter():
    b = Bnd_Box()
    BndLib.Add_s(gp_Torus(_ax3(), 10.0, 3.0), 0.0, 2.0 * PI, -3.0 * PI, -2.0 * PI, 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Xmin <= -13.0 + CONF
    assert lim.Xmax >= 13.0 - CONF
    assert lim.Ymin <= -13.0 + CONF
    assert lim.Ymax >= 13.0 - CONF


def test_BndLibTest_Torus_Translated():
    b = Bnd_Box()
    BndLib.Add_s(gp_Torus(_ax3((5, 5, 5)), 8.0, 2.0), 0.0, b)
    _near(b, Xmin=-5, Xmax=15, Ymin=-5, Ymax=15, Zmin=3, Zmax=7)


# ---- 2d ----------------------------------------------------------------------------------------

def test_BndLibTest_Line2d_FiniteSegment():
    b = Bnd_Box2d()
    BndLib.Add_s(gp_Lin2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 1)), 0.0, 10.0, 0.0, b)
    e = 10.0 / math.sqrt(2.0)
    _near(b, Xmin=0, Xmax=e, Ymin=0, Ymax=e)


def test_BndLibTest_Circle2d_Full():
    b = Bnd_Box2d()
    BndLib.Add_s(gp_Circ2d(_ax2d(), 5.0), 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5)


def test_BndLibTest_Ellipse2d_Full():
    b = Bnd_Box2d()
    BndLib.Add_s(gp_Elips2d(_ax2d(), 8.0, 4.0), 0.0, b)
    _near(b, Xmin=-8, Xmax=8, Ymin=-4, Ymax=4)


def test_BndLibTest_Hyperbola2d_SimpleArc():
    b = Bnd_Box2d()
    BndLib.Add_s(gp_Hypr2d(_ax2d(), 3.0, 2.0), -1.0, 1.0, 0.0, b)
    _near(b, Xmin=3.0, Xmax=3.0 * math.cosh(1.0), Ymin=2.0 * math.sinh(-1.0), Ymax=2.0 * math.sinh(1.0))


def test_BndLibTest_Parabola2d_FiniteArc():
    b = Bnd_Box2d()
    BndLib.Add_s(gp_Parab2d(_ax2d(), 2.0), -4.0, 4.0, 0.0, b)
    _near(b, Xmin=0, Xmax=2, Ymin=-4, Ymax=4)


def test_BndLibTest_Circle_WithTolerance():
    b = Bnd_Box()
    BndLib.Add_s(gp_Circ(_ax2(), 5.0), 0.5, b)
    _near(b, Xmin=-5.5, Xmax=5.5, Ymin=-5.5, Ymax=5.5, Zmin=-0.5, Zmax=0.5)


def test_BndLibTest_Sphere_WithTolerance():
    b = Bnd_Box()
    BndLib.Add_s(gp_Sphere(_ax3(), 3.0), 1.0, b)
    _near(b, Xmin=-4, Xmax=4, Ymin=-4, Ymax=4, Zmin=-4, Zmax=4)


# ---- BndLib_Add3dCurve -------------------------------------------------------------------------

def test_BndLib_Add3dCurveTest_Circle_Full():
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(Geom_Circle(_ax2(), 5.0)), 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=0)


def test_BndLib_Add3dCurveTest_Circle_Arc():
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(Geom_Circle(_ax2(), 5.0)), 0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0, Xmax=5, Ymin=0, Ymax=5)


def test_BndLib_Add3dCurveTest_Ellipse_Full():
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(Geom_Ellipse(_ax2(), 10.0, 5.0)), 0.0, b)
    _near(b, Xmin=-10, Xmax=10, Ymin=-5, Ymax=5)


def test_BndLib_Add3dCurveTest_Line_Segment():
    b = Bnd_Box()
    trimmed = Geom_TrimmedCurve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0)
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(trimmed), 0.0, b)
    _near(b, Xmin=0, Xmax=10, Ymin=0, Ymax=0, Zmin=0, Zmax=0)


def test_BndLib_Add3dCurveTest_BezierCurve():
    poles = _arr(gp_Pnt, [gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 0), gp_Pnt(3, 2, 0), gp_Pnt(4, 0, 0)])
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(Geom_BezierCurve(poles)), 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Xmin <= 0.0
    assert lim.Xmax >= 4.0
    assert lim.Ymin <= 0.0
    assert lim.Ymax > 1.0


def test_BndLib_Add3dCurveTest_BSplineCurve():
    poles = _arr(gp_Pnt, [gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(2, 1, 0), gp_Pnt(3, 0, 0)])
    bs = Geom_BSplineCurve(poles, _arr(float, [0.0, 1.0]), _arr(int, [4, 4]), 3)
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(bs), 0.0, b)
    assert not b.IsVoid()
    lim = b.Get()
    assert lim.Xmin <= 0.0
    assert lim.Xmax >= 3.0


def test_BndLib_Add3dCurveTest_AddOptimal_Circle():
    b = Bnd_Box()
    BndLib_Add3dCurve.AddOptimal_s(GeomAdaptor_Curve(Geom_Circle(_ax2(), 5.0)), 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5)


def test_BndLib_Add3dCurveTest_Circle_Rotated():
    b = Bnd_Box()
    BndLib_Add3dCurve.Add_s(GeomAdaptor_Curve(Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 4.0)), 0.0, b)
    _near(b, Xmin=0, Xmax=0, Ymin=-4, Ymax=4, Zmin=-4, Zmax=4)


# ---- BndLib_Add2dCurve -------------------------------------------------------------------------

def test_BndLib_Add2dCurveTest_Circle_Full():
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2d_Circle(_ax2d(), 5.0), 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5)


def test_BndLib_Add2dCurveTest_Circle_Arc():
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2d_Circle(_ax2d(), 5.0), 0.0, PI / 2.0, 0.0, b)
    _near(b, Xmin=0, Xmax=5, Ymin=0, Ymax=5)


def test_BndLib_Add2dCurveTest_Ellipse_Full():
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2d_Ellipse(_ax2d(), 8.0, 4.0), 0.0, b)
    _near(b, Xmin=-8, Xmax=8, Ymin=-4, Ymax=4)


def test_BndLib_Add2dCurveTest_Line_Segment():
    trimmed = Geom2d_TrimmedCurve(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(2, 1)), 0.0, math.sqrt(125.0))
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2dAdaptor_Curve(trimmed), 0.0, b)
    _near(b, Xmin=0, Ymin=0)
    _near(b, 0.01, Xmax=10, Ymax=5)


def test_BndLib_Add2dCurveTest_BezierCurve():
    poles = _arr(gp_Pnt2d, [gp_Pnt2d(0, 0), gp_Pnt2d(1, 3), gp_Pnt2d(3, 3), gp_Pnt2d(4, 0)])
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2dAdaptor_Curve(Geom2d_BezierCurve(poles)), 0.0, b)
    lim = b.Get()
    assert lim.Xmin <= 0.0
    assert lim.Xmax >= 4.0
    assert lim.Ymin <= 0.0
    assert lim.Ymax > 1.0


def test_BndLib_Add2dCurveTest_AddOptimal_Ellipse():
    b = Bnd_Box2d()
    BndLib_Add2dCurve.AddOptimal_s(Geom2d_Ellipse(_ax2d(), 6.0, 3.0), 0.0, 2.0 * PI, 0.0, b)
    _near(b, Xmin=-6, Xmax=6, Ymin=-3, Ymax=3)


def test_BndLib_Add2dCurveTest_Adaptor_Circle():
    b = Bnd_Box2d()
    BndLib_Add2dCurve.Add_s(Geom2dAdaptor_Curve(Geom2d_Circle(_ax2d((5, 5)), 3.0)), 0.0, b)
    _near(b, Xmin=2, Xmax=8, Ymin=2, Ymax=8)


# ---- BndLib_AddSurface -------------------------------------------------------------------------

def test_BndLib_AddSurfaceTest_Plane():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_Plane(_ax3())), -5.0, 5.0, -5.0, 5.0, 0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=0)


def test_BndLib_AddSurfaceTest_Cylinder_Full():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_CylindricalSurface(_ax3(), 5.0)), 0.0, 2.0 * PI, 0.0, 10.0,
                            0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=10)


def test_BndLib_AddSurfaceTest_Sphere_Full():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_SphericalSurface(_ax3(), 7.0)), 0.0, b)
    _near(b, Xmin=-7, Xmax=7, Ymin=-7, Ymax=7, Zmin=-7, Zmax=7)


def test_BndLib_AddSurfaceTest_Sphere_Patch():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_SphericalSurface(_ax3(), 5.0)), 0.0, 2.0 * PI, 0.0, PI / 2.0,
                            0.0, b)
    _near(b, Xmin=-5, Xmax=5, Ymin=-5, Ymax=5, Zmin=0, Zmax=5)


def test_BndLib_AddSurfaceTest_Cone_Full():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_ConicalSurface(_ax3(), PI / 4.0, 2.0)), 0.0, 2.0 * PI, 0.0, 5.0,
                            0.0, b)
    r = 2.0 + 5.0 * math.sin(PI / 4.0)
    _near(b, Xmax=r, Ymax=r, Zmax=5.0 * math.cos(PI / 4.0))


def test_BndLib_AddSurfaceTest_Torus_Full():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_ToroidalSurface(_ax3(), 10.0, 3.0)), 0.0, b)
    lim = b.Get()
    assert lim.Xmin <= -13.0 + CONF
    assert lim.Xmax >= 13.0 - CONF
    assert lim.Ymin <= -13.0 + CONF
    assert lim.Ymax >= 13.0 - CONF
    _near(b, Zmin=-3, Zmax=3)


def test_BndLib_AddSurfaceTest_BezierSurface():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0, 0, 0))
    poles.SetValue(1, 2, gp_Pnt(0, 10, 2))
    poles.SetValue(2, 1, gp_Pnt(10, 0, 2))
    poles.SetValue(2, 2, gp_Pnt(10, 10, 0))
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_BezierSurface(poles)), 0.0, b)
    lim = b.Get()
    assert lim.Xmin <= 0.0 and lim.Xmax >= 10.0
    assert lim.Ymin <= 0.0 and lim.Ymax >= 10.0
    assert lim.Zmin <= 0.0 and lim.Zmax >= 2.0


def test_BndLib_AddSurfaceTest_AddOptimal_Sphere():
    b = Bnd_Box()
    BndLib_AddSurface.AddOptimal_s(GeomAdaptor_Surface(Geom_SphericalSurface(_ax3(), 4.0)), 0.0, b)
    _near(b, Xmin=-4, Xmax=4, Ymin=-4, Ymax=4, Zmin=-4, Zmax=4)


def test_BndLib_AddSurfaceTest_Cylinder_Translated():
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_CylindricalSurface(_ax3((5, 5, 0)), 3.0)), 0.0, 2.0 * PI, 0.0,
                            10.0, 0.0, b)
    _near(b, Xmin=2, Xmax=8, Ymin=2, Ymax=8, Zmin=0, Zmax=10)


def test_BndLib_AddSurfaceTest_Plane_Tilted():
    b = Bnd_Box()
    plane = Geom_Plane(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 1)))
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(plane), 0.0, 1.0, 0.0, 1.0, 0.0, b)
    assert not b.IsVoid()


def test_BndLib_AddSurfaceTest_LargeParameters_PrecisionTest():
    poles = NCollection_Array2[gp_Pnt](1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            poles.SetValue(i, j, gp_Pnt((i - 1) * 10.0, (j - 1) * 10.0, 0.0))
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_BezierSurface(poles)), 0.0, 1.0, 0.0, 1.0, 0.0, b)
    lim = b.Get()
    assert lim.Xmin <= 1.0
    assert lim.Xmax >= 19.0
    assert lim.Ymin <= 1.0
    assert lim.Ymax >= 19.0


def test_BndLib_AddSurfaceTest_OffsetSurface_ParameterPrecision():
    off, rng = 1.0e10, 100.0
    b = Bnd_Box()
    BndLib_AddSurface.Add_s(GeomAdaptor_Surface(Geom_Plane(_ax3())), off, off + rng, off, off + rng, 0.0, b)
    _near(b, 1.0, Xmin=off, Xmax=off + rng, Ymin=off, Ymax=off + rng)
    lim = b.Get()
    assert lim.Xmax - lim.Xmin > rng * 0.9
    assert lim.Ymax - lim.Ymin > rng * 0.9
