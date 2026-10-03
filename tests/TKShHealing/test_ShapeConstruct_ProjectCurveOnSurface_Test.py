# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeConstruct_ProjectCurveOnSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GC import GC_MakeSegment
from nanocct.Geom import (
    Geom_BSplineCurve,
    Geom_BSplineSurface,
    Geom_Circle,
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_Ellipse,
    Geom_Plane,
    Geom_SphericalSurface,
    Geom_ToroidalSurface,
    Geom_TrimmedCurve,
)
from nanocct.GeomAPI import GeomAPI_PointsToBSpline
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Elips, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision
from nanocct.ShapeAnalysis import ShapeAnalysis_Surface
from nanocct.ShapeConstruct import ShapeConstruct_ProjectCurveOnSurface
from nanocct.ShapeExtend import ShapeExtend_DONE, ShapeExtend_OK


def _tol():
    return Precision.Confusion_s()


def _xy_plane(z=0.0):
    return Geom_Plane(gp_Pln(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)))


def _z_ax2(z=0.0):
    return gp_Ax2(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1))


def _segment(p1, p2):
    return GC_MakeSegment(gp_Pnt(*p1), gp_Pnt(*p2)).Value()


def _planar_bspline():
    poles = NCollection_Array1[gp_Pnt](1, 5)
    poles[1] = gp_Pnt(0, 0, 0)
    poles[2] = gp_Pnt(2, 3, 0)
    poles[3] = gp_Pnt(5, 4, 0)
    poles[4] = gp_Pnt(8, 2, 0)
    poles[5] = gp_Pnt(10, 0, 0)
    return GeomAPI_PointsToBSpline(poles).Curve()


def _helical_bspline(radius, nb_points):
    poles = NCollection_Array1[gp_Pnt](1, nb_points)
    for i in range(1, nb_points + 1):
        angle = (i - 1) * math.pi / 4.0
        poles[i] = gp_Pnt(radius * math.cos(angle), radius * math.sin(angle), (i - 1) * 1.0)
    return GeomAPI_PointsToBSpline(poles).Curve()


def _verify_projection(curve, pcurve, surface, tol):
    first = curve.FirstParameter()
    last = curve.LastParameter()
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        param = first + t * (last - first)
        p3d = gp_Pnt()
        curve.D0(param, p3d)
        surf_pnt = surface.Value(pcurve.Value(param))
        assert p3d.Distance(surf_pnt) <= tol, f"Point mismatch at t={t}"


def _project(proj, curve, first, last, *tols):
    ok, pcurve = proj.Perform(curve, first, last, *tols)
    return ok, pcurve


def _project_full(proj, curve):
    return _project(proj, curve, curve.FirstParameter(), curve.LastParameter())


# --- Basic projection tests ---------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_LineOnPlane_A1():
    line = _segment((0, 0, 0), (10, 10, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    first, last = line.FirstParameter(), line.LastParameter()
    ok, pcurve = _project(proj, line, first, last)
    assert ok
    assert pcurve is not None
    start = pcurve.Value(first)
    end = pcurve.Value(last)
    assert abs(start.X() - 0.0) <= 0.01
    assert abs(start.Y() - 0.0) <= 0.01
    assert abs(end.X() - 10.0) <= 0.01
    assert abs(end.Y() - 10.0) <= 0.01


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_CircleOnCylinder_A2():
    radius = 5.0
    cyl = Geom_CylindricalSurface(_z_ax2(), radius)
    circle = Geom_Circle(gp_Circ(_z_ax2(3.0), radius))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(cyl), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None
    assert abs(pcurve.Value(math.pi).Y() - 3.0) <= 0.01


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_IsoparametricLineOnCylinder_A3():
    radius = 5.0
    cyl = Geom_CylindricalSurface(_z_ax2(), radius)
    line = _segment((radius, 0, 0), (radius, 0, 10))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(cyl), _tol())
    first, last = line.FirstParameter(), line.LastParameter()
    ok, pcurve = _project(proj, line, first, last)
    assert ok
    assert pcurve is not None
    assert abs(pcurve.Value(first).X() - pcurve.Value(last).X()) <= 0.01


# --- B-spline curve projection tests ------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_BSplineOnPlane_B1():
    bsp = _planar_bspline()
    assert bsp is not None
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    ok, pcurve = _project_full(proj, bsp)
    assert ok
    assert pcurve is not None
    start = pcurve.Value(bsp.FirstParameter())
    end = pcurve.Value(bsp.LastParameter())
    assert abs(start.X() - 0.0) <= 0.1
    assert abs(start.Y() - 0.0) <= 0.1
    assert abs(end.X() - 10.0) <= 0.1
    assert abs(end.Y() - 0.0) <= 0.1


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_HelicalBSplineOnCylinder_B2():
    radius = 5.0
    cyl = Geom_CylindricalSurface(_z_ax2(), radius)
    bsp = _helical_bspline(radius, 9)
    assert bsp is not None
    sas = ShapeAnalysis_Surface(cyl)
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(sas, _tol())
    ok, pcurve = _project_full(proj, bsp)
    assert ok
    assert pcurve is not None
    _verify_projection(bsp, pcurve, sas, 0.1)


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_HighDegreeBSpline_B3():
    nb_poles = 50
    poles = NCollection_Array1[gp_Pnt](1, nb_poles)
    for i in range(1, nb_poles + 1):
        x = (i - 1) * 0.5
        poles[i] = gp_Pnt(x, 5.0 * math.sin(x * math.pi / 10.0), 0)
    bsp = GeomAPI_PointsToBSpline(poles, 3, 8).Curve()
    assert bsp is not None
    sas = ShapeAnalysis_Surface(_xy_plane())
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(sas, _tol())
    ok, pcurve = _project_full(proj, bsp)
    assert ok
    assert pcurve is not None
    _verify_projection(bsp, pcurve, sas, 0.5)


# --- Periodic surface tests ---------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_EquatorOnSphere_C1():
    radius = 10.0
    sphere = Geom_SphericalSurface(_z_ax2(), radius)
    circle = Geom_Circle(gp_Circ(_z_ax2(), radius))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(sphere), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_LatitudeOnSphere_C2():
    radius = 10.0
    sphere = Geom_SphericalSurface(_z_ax2(), radius)
    lat = math.pi / 4.0
    circle = Geom_Circle(gp_Circ(_z_ax2(radius * math.sin(lat)), radius * math.cos(lat)))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(sphere), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None
    assert abs(pcurve.Value(0.0).Y() - pcurve.Value(math.pi).Y()) <= 0.01


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_CircleOnTorus_C3():
    major, minor = 10.0, 2.0
    torus = Geom_ToroidalSurface(_z_ax2(), major, minor)
    circle = Geom_Circle(gp_Circ(gp_Ax2(gp_Pnt(major + minor, 0, 0), gp_Dir(0, 1, 0)), minor))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(torus), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None


# --- Conical surface tests ----------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_CircleOnCone_D1():
    radius = 5.0
    semi = math.pi / 6.0
    cone = Geom_ConicalSurface(_z_ax2(), semi, radius)
    z = 5.0
    circle = Geom_Circle(gp_Circ(_z_ax2(z), radius + z * math.tan(semi)))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(cone), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None


# --- Trimmed curve tests ------------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_ArcOnPlane_E1():
    full = Geom_Circle(gp_Circ(_z_ax2(), 5.0))
    arc = Geom_TrimmedCurve(full, 0.0, math.pi / 2.0)
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    first, last = arc.FirstParameter(), arc.LastParameter()
    ok, pcurve = _project(proj, arc, first, last)
    assert ok
    assert pcurve is not None
    start = pcurve.Value(first)
    end = pcurve.Value(last)
    assert abs(start.X() - 5.0) <= 0.01
    assert abs(start.Y() - 0.0) <= 0.01
    assert abs(end.X() - 0.0) <= 0.01
    assert abs(end.Y() - 5.0) <= 0.01


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_DoublyTrimmedCurve_E2():
    bsp = _planar_bspline()
    assert bsp is not None
    first1, last1 = bsp.FirstParameter(), bsp.LastParameter()
    trim1 = Geom_TrimmedCurve(bsp, first1, (first1 + last1) / 2.0)
    first2, last2 = trim1.FirstParameter(), trim1.LastParameter()
    trim2 = Geom_TrimmedCurve(trim1, first2, first2 + (last2 - first2) / 4.0)
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    ok, pcurve = _project_full(proj, trim2)
    assert ok
    assert pcurve is not None


# --- Ellipse projection tests -------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_EllipseOnPlane_F1():
    ellipse = Geom_Ellipse(gp_Elips(_z_ax2(), 10.0, 5.0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    ok, pcurve = _project(proj, ellipse, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None
    p0 = pcurve.Value(0.0)
    assert abs(p0.X() - 10.0) <= 0.01
    assert abs(p0.Y() - 0.0) <= 0.01
    p1 = pcurve.Value(math.pi / 2.0)
    assert abs(p1.X() - 0.0) <= 0.01
    assert abs(p1.Y() - 5.0) <= 0.01


# --- API method tests ---------------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_InitWithGeomSurface_G1():
    line = _segment((0, 0, 0), (10, 10, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(_xy_plane(), Precision.Confusion_s())
    ok, pcurve = _project_full(proj, line)
    assert ok
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_SetSurfaceAndPrecision_G2():
    line = _segment((0, 0, 0), (10, 10, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.SetSurface(_xy_plane())
    proj.SetPrecision(Precision.Confusion_s())
    ok, pcurve = _project_full(proj, line)
    assert ok
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_AdjustOverDegenModeAccessor_G3():
    # C++ assigns through the int& accessor; nanocct exposes SetAdjustOverDegenMode for that
    proj = ShapeConstruct_ProjectCurveOnSurface()
    assert proj.AdjustOverDegenMode() == 1
    proj.SetAdjustOverDegenMode(0)
    assert proj.AdjustOverDegenMode() == 0
    proj.SetAdjustOverDegenMode(1)
    assert proj.AdjustOverDegenMode() == 1


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_StatusMethod_G4():
    line = _segment((0, 0, 0), (10, 10, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    _project_full(proj, line)
    assert proj.Status(ShapeExtend_OK) or proj.Status(ShapeExtend_DONE)


# --- Tolerance and precision tests --------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_TightTolerance_H1():
    line = _segment((0, 0, 0), (10, 10, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), 1e-15)
    ok, pcurve = _project_full(proj, line)
    assert ok
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_DifferentEndpointTolerances_H2():
    poles = NCollection_Array1[gp_Pnt](1, 3)
    poles[1] = gp_Pnt(0, 0, 0)
    poles[2] = gp_Pnt(5, 5, 0.05)
    poles[3] = gp_Pnt(10, 10, 0.1)
    bsp = GeomAPI_PointsToBSpline(poles, 2, 2).Curve()
    assert bsp is not None
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    ok, pcurve = _project(proj, bsp, bsp.FirstParameter(), bsp.LastParameter(), 0.01, 0.2)
    assert ok
    assert pcurve is not None


# --- Partial curve projection tests -------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_PartialCircle_I1():
    circle = Geom_Circle(gp_Circ(_z_ax2(), 5.0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    ok, pcurve = _project(proj, circle, 0.0, math.pi / 2.0)
    assert ok
    assert pcurve is not None
    start = pcurve.Value(0.0)
    end = pcurve.Value(math.pi / 2.0)
    assert abs(start.X() - 5.0) <= 0.01
    assert abs(start.Y() - 0.0) <= 0.01
    assert abs(end.X() - 0.0) <= 0.01
    assert abs(end.Y() - 5.0) <= 0.01


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_MiddlePortionBSpline_I2():
    bsp = _planar_bspline()
    assert bsp is not None
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    first, last = bsp.FirstParameter(), bsp.LastParameter()
    rng = last - first
    ok, pcurve = _project(proj, bsp, first + 0.25 * rng, first + 0.75 * rng)
    assert ok
    assert pcurve is not None


# --- Multiple projection and reinitialization tests ---------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_MultipleProjections_J1():
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    for i in range(5):
        offset = i * 10.0
        line = _segment((offset, 0, 0), (offset + 5, 5, 0))
        ok, pcurve = _project_full(proj, line)
        assert ok, f"Projection {i} should succeed"
        assert pcurve is not None, f"PCurve {i} should not be null"


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_SurfaceReinitialization_J2():
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    _ok1, pcurve1 = _project_full(proj, _segment((0, 0, 0), (10, 10, 0)))
    assert pcurve1 is not None

    proj.Init(ShapeAnalysis_Surface(_xy_plane(5.0)), _tol())
    _ok2, pcurve2 = _project_full(proj, _segment((0, 0, 5), (10, 10, 5)))
    assert pcurve2 is not None


# --- Near-singularity tests ---------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_NearPoleOnSphere_K1():
    radius = 10.0
    sphere = Geom_SphericalSurface(_z_ax2(), radius)
    lat = math.pi / 2.0 - 0.01
    circle = Geom_Circle(gp_Circ(_z_ax2(radius * math.sin(lat)), radius * math.cos(lat)))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(sphere), _tol())
    ok, pcurve = _project(proj, circle, 0.0, 2.0 * math.pi)
    assert ok
    assert pcurve is not None


# --- Edge case tests ----------------------------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_VeryShortCurve_L1():
    line = _segment((0, 0, 0), (1e-6, 0, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), 1e-4)
    # Result may vary but should not crash
    _project_full(proj, line)


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_CurveFarFromSurface_L2():
    line = _segment((0, 0, 100), (10, 10, 100))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), _tol())
    _ok, pcurve = _project_full(proj, line)
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_LargeTolerance_L3():
    line = _segment((0, 0, 0.1), (10, 10, 0.1))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(ShapeAnalysis_Surface(_xy_plane()), 1.0)
    ok, pcurve = _project_full(proj, line)
    assert ok
    assert pcurve is not None


# --- Regression tests from bug reports ----------------------------------------------------


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_Bug27569_ManyKnotsBSpline_M1():
    degree = 3
    nb_knots = 15
    nb_poles = nb_knots + degree - 1
    poles = NCollection_Array1[gp_Pnt](1, nb_poles)
    for i in range(1, nb_poles + 1):
        t = (i - 1.0) / (nb_poles - 1.0)
        angle = t * 2.0 * math.pi
        r = 50.0 + 20.0 * math.cos(3.0 * angle)
        poles[i] = gp_Pnt(r * math.cos(angle), -30.0 * t, r * math.sin(angle))
    knots = NCollection_Array1[float](1, nb_knots)
    mults = NCollection_Array1[int](1, nb_knots)
    for i in range(1, nb_knots + 1):
        knots[i] = (i - 1.0) / (nb_knots - 1.0)
        mults[i] = 1
    mults[1] = degree + 1
    mults[nb_knots] = degree + 1

    bsp = Geom_BSplineCurve(poles, knots, mults, degree)
    assert bsp.NbKnots() >= 10

    plane = Geom_Plane(gp_Pnt(0, -15, 0), gp_Dir(0, 1, 0))
    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(plane, Precision.Confusion_s())
    ok, pcurve = _project_full(proj, bsp)
    assert ok
    assert pcurve is not None


def test_ShapeConstruct_ProjectCurveOnSurfaceTest_Bug27569_HighMultiplicityBSpline_M2():
    degree = 7
    nb_knots = 7
    mults = NCollection_Array1[int](1, nb_knots)
    for i, m in enumerate((8, 7, 7, 7, 7, 7, 8), start=1):
        mults[i] = m
    nb_poles = 43
    knots = NCollection_Array1[float](1, nb_knots)
    for i in range(1, nb_knots + 1):
        knots[i] = float(i - 1)

    poles = NCollection_Array1[gp_Pnt](1, nb_poles)
    for i in range(1, 16):
        t = (i - 1.0) / 14.0
        poles[i] = gp_Pnt(144.0 - t * 74.0, -t * 0.0002, 8.3 + t * 51.7)
    for i in range(16, 29):
        poles[i] = gp_Pnt(70.0, 0.0, 60.0)
    for i in range(29, nb_poles + 1):
        t = (i - 29.0) / (nb_poles - 29.0)
        poles[i] = gp_Pnt(70.0 - t * 80.0, -t * 32.0, 60.0 - t * 60.0)

    bsp = Geom_BSplineCurve(poles, knots, mults, degree)

    surf_poles = NCollection_Array2[gp_Pnt](1, 8, 1, 2)
    row1 = [(70, 0, 60), (85.01, 0, 60), (98.87, 0, 55.07), (111.6, 0, 46.57),
            (123.15, 0, 35.68), (133.46, 0, 23.56), (142.46, 0, 11.32), (150, 0, 0)]
    row2 = [(54.99, 0, 60), (41.13, 0, 55.07), (28.4, 0, 46.57), (16.85, 0, 35.68),
            (6.54, 0, 23.56), (-2.46, 0, 11.32), (-10, 0, 0), (-10, -35.91, 0)]
    for i in range(8):
        surf_poles[i + 1, 1] = gp_Pnt(*row1[i])
        surf_poles[i + 1, 2] = gp_Pnt(*row2[i])

    u_knots = NCollection_Array1[float](1, 2)
    v_knots = NCollection_Array1[float](1, 2)
    u_mults = NCollection_Array1[int](1, 2)
    v_mults = NCollection_Array1[int](1, 2)
    u_knots[1], u_knots[2] = 0.0, 1.0
    v_knots[1], v_knots[2] = 0.0, 1.0
    u_mults[1], u_mults[2] = 8, 8
    v_mults[1], v_mults[2] = 2, 2

    surf = Geom_BSplineSurface(surf_poles, u_knots, v_knots, u_mults, v_mults, 7, 1)

    proj = ShapeConstruct_ProjectCurveOnSurface()
    proj.Init(surf, Precision.Confusion_s())
    ok, pcurve = _project_full(proj, bsp)
    assert ok
    assert pcurve is not None
