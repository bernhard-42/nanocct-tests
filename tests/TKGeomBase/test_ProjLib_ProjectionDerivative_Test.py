# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ProjLib_ProjectionDerivative_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BezierCurve, Geom_Line, Geom_SurfaceOfLinearExtrusion
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.ProjLib import ProjLib_CompProjectedCurve


def _bezier(*pts):
    poles = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        poles[i] = gp_Pnt(*p)
    return Geom_BezierCurve(poles)


def test_ProjLib_ProjectionDerivativeTest_RegularProjectionNearSingularSurfaceDerivatives():
    # S(u,v)=(u*u,u+v,0), C(t)=(t,0,0): the pcurve is (sqrt(t),-sqrt(t)).
    basis = _bezier((0.0, 0.0, 0.0), (0.0, 0.5, 0.0), (1.0, 1.0, 0.0))
    surface = GeomAdaptor_Surface(Geom_SurfaceOfLinearExtrusion(basis, gp_Dir(0.0, 1.0, 0.0)), 0.0, 1.0, -2.0, 2.0)
    tol = 1.0e-13
    # At u=1e-6, D2 amplifies the relative parameter error by a factor of eight.
    rel = 1.0e-6
    for first in (1.0e-12, 0.25):
        curve = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)), first, 1.0)
        projection = ProjLib_CompProjectedCurve(surface, curve, tol, tol)
        assert projection.NbCurves() == 1, first
        start, end = projection.Bounds(1)
        assert math.isfinite(start) is True and math.isfinite(end) is True, first
        assert start <= first <= end, first
        exp_u = math.sqrt(first)
        exp_d1 = 0.5 / exp_u
        exp_d2 = -0.25 / (first * exp_u)
        d1 = projection.EvalD1(first)
        d2 = projection.EvalD2(first)
        for point in (d1.Point, d2.Point):
            assert point.X() == pytest.approx(exp_u, abs=tol), first
            assert point.Y() == pytest.approx(-exp_u, abs=tol), first
            assert surface.EvalD0(point.X(), point.Y()).Distance(curve.EvalD0(first)) <= Precision.Confusion_s(), first
        # The inverse point is resolved first; the remaining relative error is derivative arithmetic.
        for derivative in (d1.D1, d2.D1):
            assert derivative.X() == pytest.approx(exp_d1, abs=exp_d1 * rel), first
            assert derivative.Y() == pytest.approx(-exp_d1, abs=exp_d1 * rel), first
        assert d2.D2.X() == pytest.approx(exp_d2, abs=abs(exp_d2) * rel), first
        assert d2.D2.Y() == pytest.approx(-exp_d2, abs=abs(exp_d2) * rel), first


def test_ProjLib_ProjectionDerivativeTest_ProjectionDerivativesIncludeNormalOffsetCurvature():
    # S(u,v)=(u,u*u,v), C(t)=(0,t,0): the positive branch has u=sqrt(t-0.5).
    basis = _bezier((0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 0.0))
    surface = GeomAdaptor_Surface(Geom_SurfaceOfLinearExtrusion(basis, gp_Dir(0.0, 0.0, 1.0)), 0.0, 1.0, -1.0, 1.0)
    curve = GeomAdaptor_Curve(Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)), 0.75, 1.0)
    projection = ProjLib_CompProjectedCurve(surface, curve, 1.0e-13, 1.0e-13)
    assert projection.NbCurves() == 1
    d1 = projection.EvalD1(0.75)
    d2 = projection.EvalD2(0.75)
    pc = Precision.PConfusion_s()
    assert d1.Point.X() == pytest.approx(0.5, abs=pc)
    assert d1.Point.Y() == pytest.approx(0.0, abs=pc)
    assert d2.Point.X() == pytest.approx(0.5, abs=pc)
    assert d2.Point.Y() == pytest.approx(0.0, abs=pc)
    tol = 1.0e-6
    assert d1.D1.X() == pytest.approx(1.0, abs=tol)
    assert d1.D1.Y() == pytest.approx(0.0, abs=tol)
    assert d2.D1.X() == pytest.approx(1.0, abs=tol)
    assert d2.D1.Y() == pytest.approx(0.0, abs=tol)
    assert d2.D2.X() == pytest.approx(-2.0, abs=2.0 * tol)
    assert d2.D2.Y() == pytest.approx(0.0, abs=tol)
