# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomLib_CheckCurveOnSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Adaptor3d import Adaptor3d_CurveOnSurface
from nanocct.Geom import Geom_Circle, Geom_CylindricalSurface, Geom_Line, Geom_Plane, Geom_ToroidalSurface
from nanocct.Geom2d import Geom2d_Ellipse, Geom2d_Line
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.GeomLib import GeomLib_CheckCurveOnSurface
from nanocct.gp import gp_Ax2, gp_Ax2d, gp_Ax3, gp_Dir, gp_Dir2d, gp_Pnt, gp_Pnt2d
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _ax2(z=0.0):
    return gp_Ax2(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))


def _ax3():
    return gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))


def _check(c3d, c2d, surf):
    cos = Adaptor3d_CurveOnSurface(c2d, GeomAdaptor_Surface(surf))
    chk = GeomLib_CheckCurveOnSurface()
    chk.Init(c3d, Precision.PConfusion_s())
    chk.Perform(cos)
    return chk


def _circle_on_cylinder(rc, ry, h):
    c3d = GeomAdaptor_Curve(Geom_Circle(_ax2(h), rc), 0.0, 2.0 * math.pi)
    c2d = Geom2dAdaptor_Curve(Geom2d_Line(gp_Pnt2d(0.0, h), gp_Dir2d(1, 0)), 0.0, 2.0 * math.pi)
    return _check(c3d, c2d, Geom_CylindricalSurface(_ax3(), ry))


def _line_on_plane(d3, d2, first, last):
    c3d = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0, 0, 0), d3), first, last)
    c2d = Geom2dAdaptor_Curve(Geom2d_Line(gp_Pnt2d(0, 0), d2), first, last)
    return _check(c3d, c2d, Geom_Plane(_ax3()))


def _circle_and_ellipse(major, minor, first, last):
    c3d = GeomAdaptor_Curve(Geom_Circle(_ax2(), 2.0), first, last)
    c2d = Geom2dAdaptor_Curve(Geom2d_Ellipse(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), major, minor), first, last)
    return _check(c3d, c2d, Geom_Plane(_ax3()))


def test_GeomLib_CheckCurveOnSurfaceTest_AnalyticCoincident_ReportsZeroDeviation():
    chk = _circle_on_cylinder(2.0, 2.0, 5.0)
    assert chk.IsDone()
    assert chk.MaxDistance() <= CONF


def test_GeomLib_CheckCurveOnSurfaceTest_AnalyticDeviating_ReportsActualDeviation():
    chk = _circle_on_cylinder(1.95, 2.0, 5.0)
    assert chk.IsDone()
    assert abs(chk.MaxDistance() - 0.05) <= 1.0e-9


def test_GeomLib_CheckCurveOnSurfaceTest_LineOnPlane_ReportsZeroDeviation():
    chk = _line_on_plane(gp_Dir(1, 0, 0), gp_Dir2d(1, 0), -10.0, 10.0)
    assert chk.IsDone()
    assert chk.MaxDistance() <= CONF


def test_GeomLib_CheckCurveOnSurfaceTest_DeviatingLines_ReportsEndpointMaximum():
    chk = _line_on_plane(gp_Dir(1, 0, 0), gp_Dir2d(0, 1), -2.0, 3.0)
    assert chk.IsDone()
    assert abs(chk.MaxDistance() - math.sqrt(18.0)) <= CONF
    assert chk.MaxParameter() == 3.0


def test_GeomLib_CheckCurveOnSurfaceTest_CircleAndEllipse_ReportsAnalyticMaximum():
    chk = _circle_and_ellipse(4.0, 1.0, 0.0, 2.0 * math.pi)
    assert chk.IsDone()
    assert abs(chk.MaxDistance() - 2.0) <= CONF


def test_GeomLib_CheckCurveOnSurfaceTest_NegativeTrim_ReportsInteriorMaximum():
    chk = _circle_and_ellipse(2.0, 1.0, -2.0, -1.0)
    assert chk.IsDone()
    assert abs(chk.MaxDistance() - 1.0) <= CONF
    assert abs(chk.MaxParameter() + 0.5 * math.pi) <= Precision.PConfusion_s()


def test_GeomLib_CheckCurveOnSurfaceTest_AnalyticAliasing_ReportsActualDeviation():
    first, last = 0.0, 80.0 * math.pi
    c3d = GeomAdaptor_Curve(Geom_Circle(_ax2(), 4.0), first, last)
    c2d = Geom2dAdaptor_Curve(Geom2d_Line(gp_Pnt2d(0, 0), gp_Dir2d(3, 4)), first, last)
    chk = _check(c3d, c2d, Geom_ToroidalSurface(_ax3(), 3.0, 1.0))
    assert chk.IsDone()
    assert abs(chk.MaxDistance() - 8.0) <= CONF
