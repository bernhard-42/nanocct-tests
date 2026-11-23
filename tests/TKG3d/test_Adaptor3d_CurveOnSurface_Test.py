# Translated from OCCT src/ModelingData/TKG3d/GTests/Adaptor3d_CurveOnSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Adaptor3d import Adaptor3d_CurveOnSurface
from nanocct.Geom import Geom_BezierSurface, Geom_BSplineSurface, Geom_Plane
from nanocct.Geom2d import Geom2d_BezierCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomAbs import GeomAbs_C1
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Pln, gp_Pnt, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1, NCollection_Array2


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _pcurve(*pts):
    poles = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, p in enumerate(pts, 1):
        poles[i] = gp_Pnt2d(*p)
    return Geom2d_BezierCurve(poles)


def test_Adaptor3d_CurveOnSurfaceTest_D3UsesThirdDerivativeOfPlanarPCurve():
    pcurve = _pcurve((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 2.0))
    curve = Adaptor3d_CurveOnSurface(Geom2dAdaptor_Curve(pcurve), GeomAdaptor_Surface(Geom_Plane(gp_Pln())))
    d3 = curve.EvalD3(0.5).D3
    assert d3.X() == _eq(6.0)
    assert d3.Y() == _eq(12.0)
    assert d3.Z() == _eq(0.0)


def test_Adaptor3d_CurveOnSurfaceTest_D3CountsMixedSurfaceTermOnce():
    # Surface (u, v, u*v*v) and pcurve (t, t) give z = t*t*t.
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 3)
    for u in range(2):
        for v in range(3):
            poles.SetValue(u + 1, v + 1, gp_Pnt(u, 0.5 * v, u if v == 2 else 0.0))
    curve = Adaptor3d_CurveOnSurface(Geom2dAdaptor_Curve(_pcurve((0.0, 0.0), (1.0, 1.0))),
                                     GeomAdaptor_Surface(Geom_BezierSurface(poles)))
    assert curve.EvalD3(0.4).D3.Z() == pytest.approx(6.0, abs=1e-12)


def test_Adaptor3d_CurveOnSurfaceTest_ReloadCurveRebuildsIntervalBounds():
    pcurve = _pcurve((0.0, 0.0), (1.0, 1.0))
    curve = Adaptor3d_CurveOnSurface(Geom2dAdaptor_Curve(pcurve), GeomAdaptor_Surface(Geom_Plane(gp_Pln())))
    intervals = NCollection_Array1[float](1, 2)
    assert curve.NbIntervals(GeomAbs_C1) == 1
    curve.Intervals(intervals, GeomAbs_C1)
    assert intervals[1] == _eq(0.0)
    assert intervals[2] == _eq(1.0)
    curve.Load(Geom2dAdaptor_Curve(pcurve, 0.2, 0.8))
    assert curve.NbIntervals(GeomAbs_C1) == 1
    curve.Intervals(intervals, GeomAbs_C1)
    assert intervals[1] == _eq(0.2)
    assert intervals[2] == _eq(0.8)


def test_Adaptor3d_CurveOnSurfaceTest_ReloadSurfaceRebuildsEndpointEvaluation():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    for u in range(2):
        for v in range(2):
            poles.SetValue(u + 1, v + 1, gp_Pnt(u, v, 10.0))
    knots = NCollection_Array1[float](1, 2)
    knots[1], knots[2] = 0.0, 1.0
    mults = NCollection_Array1[int](1, 2)
    mults.Init(2)
    bspline = Geom_BSplineSurface(poles, knots, knots, mults, mults, 1, 1)
    curve = Adaptor3d_CurveOnSurface(Geom2dAdaptor_Curve(_pcurve((0.2, 0.2), (0.8, 0.8))),
                                     GeomAdaptor_Surface(bspline))
    copy = curve.ShallowCopy()
    assert copy is not None
    assert curve.EvalD1(0.0).Point.Z() == _eq(10.0)
    assert curve.EvalD1(1.0).Point.Z() == _eq(10.0)
    curve.Load(GeomAdaptor_Surface(Geom_Plane(gp_Pln())))
    assert curve.EvalD1(0.0).Point.Z() == _eq(0.0)
    assert curve.EvalD1(1.0).Point.Z() == _eq(0.0)
    assert copy.EvalD1(0.0).Point.Z() == _eq(10.0)
