# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_Gordon_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BSplineCurve, Geom_Curve, Geom_Line, Geom_TrimmedCurve
from nanocct.GeomAPI import GeomAPI_Interpolate, GeomAPI_ProjectPointOnCurve
from nanocct.GeomFill import GeomFill_Gordon, GeomFill_NetworkSurface
from nanocct.NCollection import NCollection_Array1, NCollection_Array2, NCollection_HArray1
from nanocct.Precision import Precision
from nanocct.StdFail import StdFail_NotDone
from nanocct.gp import gp_Dir, gp_Pnt, gp_Vec

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()

RS = GeomFill_Gordon.ResultStatus
BS = GeomFill_Gordon.BuildStage
AM = GeomFill_Gordon.ApproximationMode
NRS = GeomFill_NetworkSurface.ResultStatus


# ---------------------------------------------------------------------------
# helpers (anonymous namespace of the .cxx)
# ---------------------------------------------------------------------------


def arr1(values, item_type):
    arr = NCollection_Array1[item_type](1, len(values))
    for idx, value in enumerate(values):
        arr[idx + 1] = value
    return arr


def curves(values):
    return arr1(values, Geom_Curve)


def bcurves(values):
    return arr1(values, Geom_BSplineCurve)


def floats(values):
    return arr1(values, float)


def trimmed_line(p, d, first, last):
    return Geom_TrimmedCurve(Geom_Line(p, gp_Dir(*d)), first, last)


def mix(p1, p2, ratio):
    return gp_Pnt(
        p1.X() * (1.0 - ratio) + p2.X() * ratio,
        p1.Y() * (1.0 - ratio) + p2.Y() * ratio,
        p1.Z() * (1.0 - ratio) + p2.Z() * ratio,
    )


def makeLinearBSpline(p1, p2):
    return Geom_BSplineCurve(arr1([p1, p2], gp_Pnt), floats([0.0, 1.0]), arr1([2, 2], int), 1)


def makeQuadraticBSpline(p1, p2, p3, first=0.0, last=1.0):
    return Geom_BSplineCurve(arr1([p1, p2, p3], gp_Pnt), floats([first, last]), arr1([3, 3], int), 2)


def makeIntersectionGrid(profiles, guide_params):
    nb_g = guide_params.Size()
    nb_p = profiles.Size()
    points = NCollection_Array2[gp_Pnt](1, nb_g, 1, nb_p)
    for ip in range(nb_p):
        for ig in range(nb_g):
            points[ig + 1, ip + 1] = profiles[profiles.Lower() + ip].Value(guide_params[guide_params.Lower() + ig])
    return points


def makeUnitWeightGrid(profiles, guide_params):
    weights = NCollection_Array2[float](1, guide_params.Size(), 1, profiles.Size())
    weights.Init(1.0)
    return weights


def makeRationalQuadraticBSpline(p1, p2, p3, middle_weight):
    return Geom_BSplineCurve(
        arr1([p1, p2, p3], gp_Pnt),
        floats([1.0, middle_weight, 1.0]),
        floats([0.0, 1.0]),
        arr1([3, 3], int),
        2,
    )


def makeWeightedLinearBSpline(p1, p2, weight):
    return Geom_BSplineCurve(
        arr1([p1, p2], gp_Pnt), floats([weight, weight]), floats([0.0, 1.0]), arr1([2, 2], int), 1, False, False
    )


def makeRationalLineBSpline(p1, p2, degree):
    poles = []
    weights = []
    for idx in range(1, degree + 2):
        ratio = (idx - 1) / degree
        poles.append(mix(p1, p2, ratio))
        if idx == (degree + 2) // 2:
            weights.append(0.5)
        else:
            weights.append(1.0)
    return Geom_BSplineCurve(
        arr1(poles, gp_Pnt), floats(weights), floats([0.0, 1.0]), arr1([degree + 1, degree + 1], int), degree
    )


def makeRationalQuadraticLineBSpline(p1, p2, w_start, w_mid, w_end):
    return Geom_BSplineCurve(
        arr1([p1, mix(p1, p2, 0.5), p2], gp_Pnt),
        floats([w_start, w_mid, w_end]),
        floats([0.0, 1.0]),
        arr1([3, 3], int),
        2,
    )


def _periodic(poles):
    knots = floats([0.2 * i for i in range(6)])
    mults = NCollection_Array1[int](1, 6)
    mults.Init(1)
    return Geom_BSplineCurve(arr1(poles, gp_Pnt), knots, mults, 3, True)


def makePeriodicProfile(y):
    return _periodic(
        [
            gp_Pnt(1.0, y, 0.0),
            gp_Pnt(0.309, y, 0.951),
            gp_Pnt(-0.809, y, 0.588),
            gp_Pnt(-0.809, y, -0.588),
            gp_Pnt(0.309, y, -0.951),
        ]
    )


def makePeriodicGuide(x):
    return _periodic(
        [
            gp_Pnt(x, 1.0, 0.0),
            gp_Pnt(x, 0.309, 0.951),
            gp_Pnt(x, -0.809, 0.588),
            gp_Pnt(x, -0.809, -0.588),
            gp_Pnt(x, 0.309, -0.951),
        ]
    )


def makeClosedBSplineProfile(y, rx, rz):
    poles = [
        gp_Pnt(rx, y, 0.0),
        gp_Pnt(rx, y, 0.7 * rz),
        gp_Pnt(0.3 * rx, y, rz),
        gp_Pnt(-0.7 * rx, y, 0.8 * rz),
        gp_Pnt(-rx, y, 0.0),
        gp_Pnt(-0.7 * rx, y, -0.8 * rz),
        gp_Pnt(0.3 * rx, y, -rz),
        gp_Pnt(rx, y, -0.7 * rz),
        gp_Pnt(rx, y, 0.0),
    ]
    knots = floats([i / 6.0 for i in range(7)])
    mults = arr1([4, 1, 1, 1, 1, 1, 4], int)
    return Geom_BSplineCurve(arr1(poles, gp_Pnt), knots, mults, 3, False)


def interpolate(points, params=None, periodic=False):
    hp = NCollection_HArray1[gp_Pnt](1, len(points))
    for idx, pnt in enumerate(points):
        hp.SetValue(idx + 1, pnt)
    if params is None:
        interp = GeomAPI_Interpolate(hp, periodic, CONF)
    else:
        hpar = NCollection_HArray1[float](1, len(params))
        for idx, value in enumerate(params):
            hpar.SetValue(idx + 1, value)
        interp = GeomAPI_Interpolate(hp, hpar, periodic, CONF)
    interp.Perform()
    assert interp.IsDone()
    return interp.Curve()


def makeInterpolatedPeriodicProfile(y, seam_shift):
    nb = 8
    pts = []
    for i in range(nb):
        angle = 2.0 * math.pi * (i + seam_shift) / nb
        pts.append(gp_Pnt(math.cos(angle), y, math.sin(angle)))
    return interpolate(pts, None, True)


def makeCubicInterpBSpline(p1, p2, p3, p4):
    return interpolate([p1, p2, p3, p4], [0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0])


def makeSineBSpline(x_start, x_end, y, amplitude, nb=11):
    pts = []
    params = []
    for i in range(1, nb + 1):
        t = (i - 1) / (nb - 1)
        pts.append(gp_Pnt(x_start + t * (x_end - x_start), y, amplitude * math.sin(math.pi * t)))
        params.append(t)
    return interpolate(pts, params)


def makeMeanderingProfile(y):
    pts = [
        gp_Pnt(0.0, y, 0.0),
        gp_Pnt(0.62, y + 0.04, 0.01),
        gp_Pnt(0.38, y - 0.04, -0.01),
        gp_Pnt(0.5, y, 0.0),
        gp_Pnt(0.64, y + 0.03, 0.01),
        gp_Pnt(0.44, y - 0.02, -0.01),
        gp_Pnt(1.0, y, 0.0),
    ]
    return interpolate(pts, [i / 6.0 for i in range(7)])


def verifyPointOnSurface(surf, u, v, expected, tol):
    dist = surf.Value(u, v).Distance(expected)
    assert dist < tol, f"Surface point at ({u}, {v}) differs from expected by {dist}"


def wavyHeight(u, v):
    return 0.35 * math.sin(math.pi * u) * (0.4 + v) + 0.12 * math.sin(2.0 * math.pi * v) * (1.0 - u)


def saddleHeight(u, v):
    return 0.6 * (u - 0.5) * (v - 0.5) + 0.15 * math.sin(math.pi * u) * math.sin(math.pi * v)


def rippleHeight(u, v):
    return 0.2 * math.sin(2.0 * math.pi * u) * math.cos(math.pi * v) + 0.1 * math.sin(3.0 * math.pi * v)


class AnalyticNetwork:
    def __init__(self, nb_profiles, nb_guides, height, origin=(0.0, 0.0, 0.0), scale=1.0):
        def point(u, v):
            return gp_Pnt(origin[0] + scale * u, origin[1] + scale * v, origin[2] + scale * height(u, v))

        profiles = []
        for ip in range(nb_profiles):
            v = ip / (nb_profiles - 1)
            params = [ig / (nb_guides - 1) for ig in range(nb_guides)]
            profiles.append(interpolate([point(u, v) for u in params], params))
        guides = []
        for ig in range(nb_guides):
            u = ig / (nb_guides - 1)
            params = [ip / (nb_profiles - 1) for ip in range(nb_profiles)]
            guides.append(interpolate([point(u, v) for v in params], params))
        self.ProfileList = profiles
        self.GuideList = guides
        self.Profiles = curves(profiles)
        self.Guides = curves(guides)


def bounds(surf):
    return surf.UKnot(1), surf.UKnot(surf.NbUKnots()), surf.VKnot(1), surf.VKnot(surf.NbVKnots())


def mid(surf):
    u0, u1, v0, v1 = bounds(surf)
    return 0.5 * (u0 + u1), 0.5 * (v0 + v1)


def verifyUniformNetworkInterpolation(surface, network, tol):
    assert surface is not None
    nb_samples = 32
    u_min, u_max, v_min, v_max = bounds(surface)
    nb_p = len(network.ProfileList)
    for ip, profile in enumerate(network.ProfileList):
        v = v_min + ip / (nb_p - 1) * (v_max - v_min)
        for s in range(nb_samples + 1):
            param = s / nb_samples
            u = u_min + param * (u_max - u_min)
            assert surface.Value(u, v).Distance(profile.Value(param)) <= tol
    nb_g = len(network.GuideList)
    for ig, guide in enumerate(network.GuideList):
        u = u_min + ig / (nb_g - 1) * (u_max - u_min)
        for s in range(nb_samples + 1):
            param = s / nb_samples
            v = v_min + param * (v_max - v_min)
            assert surface.Value(u, v).Distance(guide.Value(param)) <= tol


def gordon(profiles, guides, tol, parallel=None, mode=None):
    g = GeomFill_Gordon()
    if parallel is not None:
        g.SetParallelMode(parallel)
    g.Init(profiles, guides, tol)
    if mode is not None:
        g.SetApproximationMode(mode)
    g.Perform()
    return g


def unit_square_lines():
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(0, 1, 0), (1, 0, 0), 0.0, 1.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 0, 0), (0, 1, 0), 0.0, 1.0)]
    )
    return profiles, guides


def single_lines():
    profile = curves([trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 1.0)])
    guide = curves([trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 1.0)])
    return profile, guide


def quad_profiles(z1, z2, z3):
    return curves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, z1), gp_Pnt(1, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(0.5, 0.5, z2), gp_Pnt(1, 0.5, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.5, 1, z3), gp_Pnt(1, 1, 0)),
        ]
    )


def unit_linear_guides():
    return curves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)), makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0))]
    )


def rational_degree9_network(as_bspline):
    d = 9
    profiles = [
        makeRationalLineBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), d),
        makeRationalLineBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(1, 0.5, 0), d),
        makeRationalLineBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0), d),
    ]
    guides = [
        makeRationalLineBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0), d),
        makeRationalLineBSpline(gp_Pnt(0.5, 0, 0), gp_Pnt(0.5, 1, 0), d),
        makeRationalLineBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0), d),
    ]
    if as_bspline:
        return bcurves(profiles), bcurves(guides)
    return curves(profiles), curves(guides)


def rational_quadratic_line_network():
    profiles = curves(
        [
            makeRationalQuadraticLineBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), 1.0, 0.45, 1.0),
            makeRationalQuadraticLineBSpline(gp_Pnt(0, 0.4, 0), gp_Pnt(1, 0.4, 0), 1.0, 1.8, 0.7),
            makeRationalQuadraticLineBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0), 0.8, 0.65, 1.5),
        ]
    )
    guides = curves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)),
            makeLinearBSpline(gp_Pnt(0.4, 0, 0), gp_Pnt(0.4, 1, 0)),
            makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0)),
        ]
    )
    return profiles, guides


def network_surface(profiles, guides, profile_params, guide_params, weights, tol, u_closed, v_closed):
    grid = makeIntersectionGrid(profiles, guide_params)
    if weights is None:
        weights = makeUnitWeightGrid(profiles, guide_params)
    net = GeomFill_NetworkSurface()
    net.Init(profiles, guides, profile_params, guide_params, grid, weights, tol, u_closed, v_closed)
    return net


# ============================================================================
# GeomFill_Gordon tests (high-level, automatic intersection detection)
# ============================================================================


def test_GeomFill_Gordon_SimpleLineNetwork_ProducesValidSurface():
    g = gordon(*unit_square_lines(), CONF)
    assert g.IsDone()
    assert g.Status() == RS.Done
    rep = g.Report()
    assert rep.Status == RS.Done
    assert rep.FailedStage == BS.NotStarted
    assert rep.IsApproximate is False
    assert rep.MaxContactGap <= CONF
    assert rep.MaxProfileDeviation <= 1.0e-7
    assert rep.MaxGuideDeviation <= 1.0e-7
    surf = g.Surface()
    assert surf is not None
    verifyPointOnSurface(surf, 0.0, 0.0, gp_Pnt(0, 0, 0), 1.0e-3)
    verifyPointOnSurface(surf, 1.0, 0.0, gp_Pnt(1, 0, 0), 1.0e-3)
    verifyPointOnSurface(surf, 0.0, 1.0, gp_Pnt(0, 1, 0), 1.0e-3)
    verifyPointOnSurface(surf, 1.0, 1.0, gp_Pnt(1, 1, 0), 1.0e-3)


def test_GeomFill_Gordon_EmptyInput_NotDone():
    g = gordon(*single_lines(), CONF)
    assert g.IsDone() is False
    assert g.Status() == RS.InvalidInput


def test_GeomFill_Gordon_SingleProfileOrGuide_NotDone():
    profiles = curves([trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 1.0)])
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 0, 0), (0, 1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone() is False
    assert g.Status() == RS.InvalidInput


def test_GeomFill_Gordon_NotDone_BeforePerform():
    g = GeomFill_Gordon()
    assert g.IsDone() is False
    assert g.Status() == RS.NotStarted
    assert g.Report().Status == RS.NotStarted
    assert g.Report().FailedStage == BS.NotStarted
    assert g.Report().IsApproximate is False
    with pytest.raises(StdFail_NotDone):
        g.Surface()


def test_GeomFill_Gordon_ReinitResetsReportAndSurface():
    g = gordon(*unit_square_lines(), CONF)
    assert g.IsDone()
    assert g.Report().Status == RS.Done
    assert g.Surface() is not None

    one_profile, one_guide = single_lines()
    g.Init(one_profile, one_guide, CONF)
    assert g.IsDone() is False
    assert g.Status() == RS.NotStarted
    rep = g.Report()
    assert rep.Status == RS.NotStarted
    assert rep.FailedStage == BS.NotStarted
    assert rep.IsApproximate is False
    assert abs(rep.MaxContactGap) <= 1.0e-12
    assert abs(rep.MaxReparametrizationDeviation) <= 1.0e-12
    assert abs(rep.MaxProfileDeviation) <= 1.0e-12
    assert abs(rep.MaxGuideDeviation) <= 1.0e-12
    assert abs(rep.MaxApproximationDeviation) <= 1.0e-12
    with pytest.raises(StdFail_NotDone):
        g.Surface()

    g.Perform()
    assert g.IsDone() is False
    assert g.Status() == RS.InvalidInput
    assert g.Report().Status == RS.InvalidInput
    assert g.Report().FailedStage == BS.InputConversion


def test_GeomFill_Gordon_DisjointNetworkReportsContactDiscoveryFailure():
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(0, 1, 0), (1, 0, 0), 0.0, 1.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(2, 0, 0), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(3, 0, 0), (0, 1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone() is False
    assert g.IsApproximate() is False
    assert g.Status() == RS.IntersectionFailed
    rep = g.Report()
    assert rep.Status == RS.IntersectionFailed
    assert rep.FailedStage == BS.ContactDiscovery
    assert rep.IsApproximate is False
    assert abs(rep.MaxContactGap) <= 1.0e-12
    assert abs(rep.MaxReparametrizationDeviation) <= 1.0e-12
    with pytest.raises(StdFail_NotDone):
        g.Surface()


def test_GeomFill_Gordon_ParallelMode_DefaultSingleThreadAndMatchesParallelResult():
    profiles = quad_profiles(0.4, 0.6, 0.4)
    guides = unit_linear_guides()

    single = GeomFill_Gordon()
    assert single.IsParallelMode() is False
    single.Init(profiles, guides, CONF)
    single.Perform()
    assert single.IsDone()

    par = GeomFill_Gordon()
    par.SetParallelMode(True)
    assert par.IsParallelMode() is True
    par.Init(profiles, guides, CONF)
    par.Perform()
    assert par.IsDone()

    assert single.Surface().Value(0.5, 0.5).Distance(par.Surface().Value(0.5, 0.5)) < 1.0e-9


def test_GeomFill_Gordon_CurvedBSplineNetwork_ProducesValidSurface():
    g = gordon(quad_profiles(0.4, 0.6, 0.4), unit_linear_guides(), CONF)
    assert g.IsDone()
    surf = g.Surface()
    assert surf is not None
    u, v = mid(surf)
    assert abs(surf.Value(u, v).Z() - 0.3) <= 1.0e-6


def test_GeomFill_Gordon_NonAffineProfileReparametrization_PreservesProfilesAndGuideContinuity():
    p1 = makeCubicInterpBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.25, 0, 0.4), gp_Pnt(0.75, 0, -0.3), gp_Pnt(1, 0, 0))
    p2 = makeCubicInterpBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(0.25, 0.5, 0.2), gp_Pnt(0.75, 0.5, -0.5), gp_Pnt(1, 0.5, 0))
    p3 = makeCubicInterpBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.25, 1, 0.5), gp_Pnt(0.75, 1, -0.2), gp_Pnt(1, 1, 0))
    profiles = curves([p1, p2, p3])

    guide2 = interpolate([p1.Value(0.4), p2.Value(0.5), p3.Value(0.6)], [0.0, 0.5, 1.0])
    guides = curves(
        [
            makeLinearBSpline(p1.Value(0.0), p3.Value(0.0)),
            guide2,
            makeLinearBSpline(p1.Value(1.0), p3.Value(1.0)),
        ]
    )

    g = gordon(profiles, guides, CONF)
    assert g.IsDone(), g.Status()
    s = g.Surface()
    assert g.Report().MaxProfileDeviation <= CONF
    assert g.Report().MaxGuideDeviation <= CONF
    u0, u1, v0, v1 = bounds(s)
    v_mid = 0.5 * (v0 + v1)
    nb = 32
    for i in range(nb + 1):
        r = i / nb
        u = u0 + r * (u1 - u0)
        if r <= 0.5:
            pp1 = 0.8 * r
            pp3 = 1.2 * r
        else:
            pp1 = 1.2 * r - 0.2
            pp3 = 0.2 + 0.8 * r
        assert s.Value(u, v0).Distance(p1.Value(pp1)) <= CONF
        assert s.Value(u, v_mid).Distance(p2.Value(r)) <= CONF
        assert s.Value(u, v1).Distance(p3.Value(pp3)) <= CONF

    guide_u = 0.5 * (u0 + u1)
    for i in range(nb + 1):
        r = i / nb
        v = v0 + r * (v1 - v0)
        assert s.Value(guide_u, v).Distance(guide2.Value(r)) <= CONF


def test_GeomFill_Gordon_MixedCurveTypes_ProducesValidSurface():
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 2.0), trimmed_line(gp_Pnt(0, 2, 0), (1, 0, 0), 0.0, 2.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 2.0), trimmed_line(gp_Pnt(2, 0, 0), (0, 1, 0), 0.0, 2.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    verifyPointOnSurface(s, s.UKnot(1), s.VKnot(1), gp_Pnt(0, 0, 0), 0.01)


def test_GeomFill_Gordon_PeriodicBSplineProfiles_AreExpandedBeforeConstruction():
    p = [makePeriodicProfile(0.0), makePeriodicProfile(0.5), makePeriodicProfile(1.0)]
    assert p[0].IsPeriodic()
    guides = curves(
        [
            makeLinearBSpline(p[0].Value(0.0), p[2].Value(0.0)),
            makeLinearBSpline(p[0].Value(0.5), p[2].Value(0.5)),
            makeLinearBSpline(p[0].Value(1.0), p[2].Value(1.0)),
        ]
    )
    g = gordon(curves(p), guides, CONF)
    assert g.IsDone()
    assert g.Surface() is not None
    assert g.Surface().IsUPeriodic()


def test_GeomFill_Gordon_PeriodicBSplineGuides_AreExpandedBeforeConstruction():
    gd = [makePeriodicGuide(0.0), makePeriodicGuide(0.5), makePeriodicGuide(1.0)]
    assert gd[0].IsPeriodic()
    profiles = curves(
        [
            makeLinearBSpline(gd[0].Value(0.0), gd[2].Value(0.0)),
            makeLinearBSpline(gd[0].Value(0.5), gd[2].Value(0.5)),
            makeLinearBSpline(gd[0].Value(1.0), gd[2].Value(1.0)),
        ]
    )
    g = gordon(profiles, curves(gd), CONF)
    assert g.IsDone()
    assert g.Surface() is not None
    assert g.Surface().IsVPeriodic()


def test_GeomFill_Gordon_InterpolatedPeriodicProfilesWithAlignedSeams_InterpolateWithoutDeviation():
    first = makeInterpolatedPeriodicProfile(0.0, 0)
    second = makeInterpolatedPeriodicProfile(1.0, 2)
    profiles = curves([first, second])

    first_seam = first.Value(first.FirstParameter())
    proj = GeomAPI_ProjectPointOnCurve(gp_Pnt(first_seam.X(), 1.0, first_seam.Z()), second)
    assert proj.NbPoints() > 0
    second.SetOrigin(proj.LowerDistanceParameter(), CONF)
    first_mid = 0.5 * (first.FirstParameter() + first.LastParameter())
    second_mid = 0.5 * (second.FirstParameter() + second.LastParameter())
    second_seam = second.Value(second.FirstParameter())
    first_middle = first.Value(first_mid)
    second_middle = second.Value(second_mid)
    assert first_seam.Distance(gp_Pnt(second_seam.X(), first_seam.Y(), second_seam.Z())) <= CONF
    assert first_middle.Distance(gp_Pnt(second_middle.X(), first_middle.Y(), second_middle.Z())) <= CONF

    guides = curves(
        [
            makeLinearBSpline(first.Value(first.FirstParameter()), second.Value(second.FirstParameter())),
            makeLinearBSpline(first.Value(first_mid), second.Value(second_mid)),
            makeLinearBSpline(first.Value(first.FirstParameter()), second.Value(second.FirstParameter())),
        ]
    )

    g = gordon(profiles, guides, CONF)
    assert g.IsDone(), g.Status()
    s = g.Surface()
    assert s.IsUPeriodic()
    assert g.Report().MaxProfileDeviation <= CONF
    assert g.Report().MaxGuideDeviation <= CONF

    u0, u1, v0, v1 = bounds(s)
    v_mid = 0.5 * (v0 + v1)
    d1_first = s.EvalD1(u0, v_mid)
    d1_last = s.EvalD1(u1, v_mid)
    assert d1_first.D1U.Angle(d1_last.D1U) <= ANG

    nb = 16
    for i in range(nb + 1):
        r = i / nb
        u = u0 + r * (u1 - u0)
        fp = first.FirstParameter() + r * (first.LastParameter() - first.FirstParameter())
        sp = second.FirstParameter() + r * (second.LastParameter() - second.FirstParameter())
        assert s.Value(u, v0).Distance(first.Value(fp)) <= CONF
        assert s.Value(u, v1).Distance(second.Value(sp)) <= CONF


def test_GeomFill_Gordon_MultipleIntersections_SelectsMonotoneBranch():
    profiles = curves([makeMeanderingProfile(0.0), makeMeanderingProfile(0.5), makeMeanderingProfile(1.0)])
    guides = curves(
        [
            makeLinearBSpline(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.0, 1.0, 0.0)),
            makeLinearBSpline(gp_Pnt(0.5, 0.0, 0.0), gp_Pnt(0.5, 1.0, 0.0)),
            makeLinearBSpline(gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(1.0, 1.0, 0.0)),
        ]
    )
    g = gordon(profiles, guides, 1.0e-5)
    assert g.IsDone(), g.Status()
    assert g.Surface() is not None
    assert g.Report().MaxProfileDeviation <= 1.0e-5
    assert g.Report().MaxGuideDeviation <= 1.0e-5
    verifyPointOnSurface(g.Surface(), 0.0, 0.0, gp_Pnt(0.0, 0.0, 0.0), 1.0e-3)
    verifyPointOnSurface(g.Surface(), 1.0, 0.0, gp_Pnt(1.0, 0.0, 0.0), 1.0e-3)
    verifyPointOnSurface(g.Surface(), 0.0, 1.0, gp_Pnt(0.0, 1.0, 0.0), 1.0e-3)
    verifyPointOnSurface(g.Surface(), 1.0, 1.0, gp_Pnt(1.0, 1.0, 0.0), 1.0e-3)

    first_center = g.Surface().Value(0.5, 0.5)
    g.Perform()
    assert g.IsDone(), g.Status()
    assert first_center.Distance(g.Surface().Value(0.5, 0.5)) <= CONF


def test_GeomFill_Gordon_FourByThreeGrid_NonUniformParams():
    profiles = curves([trimmed_line(gp_Pnt(0, y, 0), (1, 0, 0), 0.0, 1.0) for y in (0.0, 0.2, 0.7, 1.0)])
    guides = curves([trimmed_line(gp_Pnt(x, 0, 0), (0, 1, 0), 0.0, 1.0) for x in (0.0, 0.3, 1.0)])
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.Surface() is not None


def test_GeomFill_Gordon_SurfaceAlongInputCurves_IsAccurate():
    g = gordon(*unit_square_lines(), CONF)
    assert g.IsDone()
    s = g.Surface()
    u0, u1, v0, v1 = bounds(s)
    nb = 20
    for i in range(nb + 1):
        u = u0 + i * (u1 - u0) / nb
        p = s.Value(u, v0)
        assert abs(p.Y()) <= 0.01 and abs(p.Z()) <= 0.01
    for i in range(nb + 1):
        u = u0 + i * (u1 - u0) / nb
        p = s.Value(u, v1)
        assert abs(p.Y() - 1.0) <= 0.01 and abs(p.Z()) <= 0.01


def test_GeomFill_Gordon_ReversedCurveNetwork_ProducesValidSurface():
    profiles = curves(
        [trimmed_line(gp_Pnt(1, 0, 0), (-1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(0, 1, 0), (1, 0, 0), 0.0, 1.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 1, 0), (0, -1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u0, u1, v0, v1 = bounds(s)
    corners = [s.Value(u0, v0), s.Value(u1, v0), s.Value(u0, v1), s.Value(u1, v1)]
    for c in corners:
        assert abs(c.Z()) <= 0.01
    assert abs(min(c.X() for c in corners)) <= 0.01
    assert abs(max(c.X() for c in corners) - 1.0) <= 0.01
    assert abs(min(c.Y() for c in corners)) <= 0.01
    assert abs(max(c.Y() for c in corners) - 1.0) <= 0.01


def test_GeomFill_Gordon_CubicInterpolatedNetwork_ProducesValidSurface():
    profiles = curves(
        [
            makeCubicInterpBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.33, 0, 0.3), gp_Pnt(0.66, 0, -0.3), gp_Pnt(1, 0, 0)),
            makeCubicInterpBSpline(
                gp_Pnt(0, 0.5, 0), gp_Pnt(0.33, 0.5, 0.5), gp_Pnt(0.66, 0.5, -0.5), gp_Pnt(1, 0.5, 0)
            ),
            makeCubicInterpBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.33, 1, 0.3), gp_Pnt(0.66, 1, -0.3), gp_Pnt(1, 1, 0)),
        ]
    )
    g = gordon(profiles, unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u * 0.5, v).Z() - 0.6328125) <= 1.0e-9
    assert abs(s.Value(u * 1.5, v).Z() + 0.6328125) <= 1.0e-9


def test_GeomFill_Gordon_SinusoidalProfiles_SurfacePreservesShape():
    profiles = curves(
        [makeSineBSpline(0.0, 1.0, 0.0, 0.3), makeSineBSpline(0.0, 1.0, 0.5, 0.5), makeSineBSpline(0.0, 1.0, 1.0, 0.3)]
    )
    g = gordon(profiles, unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z() - 0.5) <= 0.05


def test_GeomFill_Gordon_ThreeByThreeGrid_SurfaceInterpolatesAllCurves():
    profiles = curves([trimmed_line(gp_Pnt(0, y, 0), (1, 0, 0), 0.0, 1.0) for y in (0.0, 0.5, 1.0)])
    guides = curves([trimmed_line(gp_Pnt(x, 0, 0), (0, 1, 0), 0.0, 1.0) for x in (0.0, 0.5, 1.0)])
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    u0, u1, v0, v1 = bounds(s)
    nb = 10
    for i in range(nb + 1):
        u = u0 + i * (u1 - u0) / nb
        assert abs(s.Value(u, v0).Y()) <= 0.01
        assert abs(s.Value(u, v1).Y() - 1.0) <= 0.01
    for i in range(nb + 1):
        v = v0 + i * (v1 - v0) / nb
        assert abs(s.Value(u0, v).X()) <= 0.01
        assert abs(s.Value(u1, v).X() - 1.0) <= 0.01


def test_GeomFill_Gordon_ScaledGeometry_LargeCoordinates():
    sc = 1000.0
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, sc), trimmed_line(gp_Pnt(0, sc, 0), (1, 0, 0), 0.0, sc)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, sc), trimmed_line(gp_Pnt(sc, 0, 0), (0, 1, 0), 0.0, sc)]
    )
    g = gordon(profiles, guides, 0.1)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    p = s.Value(u, v)
    assert abs(p.X() - 500.0) <= 1.0
    assert abs(p.Y() - 500.0) <= 1.0
    assert abs(p.Z()) <= 1.0


def test_GeomFill_Gordon_ScaledGeometry_SmallCoordinates():
    sc = 1.0e-3
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, sc), trimmed_line(gp_Pnt(0, sc, 0), (1, 0, 0), 0.0, sc)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, sc), trimmed_line(gp_Pnt(sc, 0, 0), (0, 1, 0), 0.0, sc)]
    )
    g = gordon(profiles, guides, sc * 1.0e-4)
    assert g.IsDone()
    assert g.Surface() is not None


def test_GeomFill_Gordon_AllReversedCurves_ProducesValidSurface():
    profiles = curves(
        [trimmed_line(gp_Pnt(1, 0, 0), (-1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 1, 0), (-1, 0, 0), 0.0, 1.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 1, 0), (0, -1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 1, 0), (0, -1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.Surface() is not None


def test_GeomFill_Gordon_ShuffledInputOrder_ProducesValidSurface():
    profiles = curves([trimmed_line(gp_Pnt(0, y, 0), (1, 0, 0), 0.0, 1.0) for y in (1.0, 0.5, 0.0)])
    guides = curves([trimmed_line(gp_Pnt(x, 0, 0), (0, 1, 0), 0.0, 1.0) for x in (1.0, 0.0)])
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z()) <= 0.01


def test_GeomFill_Gordon_SaddleSurface_BothDirectionsCurved():
    profiles = curves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, 0.5), gp_Pnt(1, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.5, 1, 0.5), gp_Pnt(1, 1, 0)),
        ]
    )
    guides = curves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 0.5, -0.5), gp_Pnt(0, 1, 0)),
            makeQuadraticBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 0.5, -0.5), gp_Pnt(1, 1, 0)),
        ]
    )
    g = gordon(profiles, guides, 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z()) <= 0.5


def test_GeomFill_Gordon_AsymmetricNetwork_FiveProfilesTwoGuides():
    profiles = curves([trimmed_line(gp_Pnt(0, i * 0.25, 0), (1, 0, 0), 0.0, 1.0) for i in range(5)])
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 0, 0), (0, 1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.Surface() is not None


def test_GeomFill_Gordon_AsymmetricNetwork_TwoProfilesFiveGuides():
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(0, 1, 0), (1, 0, 0), 0.0, 1.0)]
    )
    guides = curves([trimmed_line(gp_Pnt(i * 0.25, 0, 0), (0, 1, 0), 0.0, 1.0) for i in range(5)])
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.Surface() is not None


def test_GeomFill_Gordon_NonPlanarNetwork_CurvesInBothDirections():
    profiles = curves([makeSineBSpline(0.0, 1.0, 0.0, 0.2), makeSineBSpline(0.0, 1.0, 1.0, 0.2)])
    params = [(i - 1) / 10.0 for i in range(1, 12)]
    g1 = interpolate([gp_Pnt(0.0, t, 0.15 * math.sin(math.pi * t)) for t in params], params)
    g2 = interpolate([gp_Pnt(1.0, t, 0.15 * math.sin(math.pi * t)) for t in params], params)
    g = gordon(profiles, curves([g1, g2]), 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z() - 0.35) <= 0.05


def test_GeomFill_Gordon_SurfaceContinuity_IsSmooth():
    g = gordon(quad_profiles(0.3, 0.5, 0.3), unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    u0, u1, v0, v1 = bounds(s)
    v = 0.5 * (v0 + v1)
    nb = 50
    step = (u1 - u0) / nb
    prev_pt, prev_du, prev_dv = gp_Pnt(), gp_Vec(), gp_Vec()
    s.D1(u0 + 2.0 * step, v, prev_pt, prev_du, prev_dv)
    for i in range(3, nb - 1):
        u = u0 + i * step
        pt, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
        s.D1(u, v, pt, du, dv)
        change = du.Subtracted(prev_du).Magnitude()
        assert change < 1.0, f"DU jump at U={u}: {change}"
        prev_du = du


def test_GeomFill_Gordon_ArcLikeProfiles_NonRational():
    def makeArcProfile(y):
        nb = 9
        params = [(i - 1) / (nb - 1) for i in range(1, nb + 1)]
        pts = [gp_Pnt(0.5 - 0.5 * math.cos(math.pi * t), y, 0.3 * math.sin(math.pi * t)) for t in params]
        return interpolate(pts, params)

    g = gordon(curves([makeArcProfile(0.0), makeArcProfile(1.0)]), unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z() - 0.3) <= 0.05


def test_GeomFill_Gordon_RepeatPerform_GivesSameResult():
    g = GeomFill_Gordon()
    profiles, guides = unit_square_lines()
    g.Init(profiles, guides, CONF)
    g.Perform()
    assert g.IsDone()
    u, v = mid(g.Surface())
    mid1 = g.Surface().Value(u, v)
    g.Perform()
    assert g.IsDone()
    u, v = mid(g.Surface())
    mid2 = g.Surface().Value(u, v)
    assert mid1.Distance(mid2) <= CONF
    assert g.Report().Status == RS.Done


def test_GeomFill_Gordon_HighDensityNetwork_SixBySix():
    nb = 6
    profiles = curves([trimmed_line(gp_Pnt(0, i / (nb - 1), 0), (1, 0, 0), 0.0, 1.0) for i in range(nb)])
    guides = curves([trimmed_line(gp_Pnt(j / (nb - 1), 0, 0), (0, 1, 0), 0.0, 1.0) for j in range(nb)])
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u0, u1, v0, v1 = bounds(s)
    for i in range(nb):
        for j in range(nb):
            x = j / (nb - 1)
            y = i / (nb - 1)
            p = s.Value(u0 + x * (u1 - u0), v0 + y * (v1 - v0))
            assert abs(p.Z()) <= 0.02, f"Intersection point ({i}, {j}) Z-deviation"


def test_GeomFill_Gordon_QuadraticProfiles_SurfaceMatchesCurvesAtBoundaries():
    p1 = makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, 1.0), gp_Pnt(1, 0, 0))
    p2 = makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.5, 1, 1.0), gp_Pnt(1, 1, 0))
    g = gordon(curves([p1, p2]), unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    u0, u1, v0, v1 = bounds(s)
    for i in range(11):
        t = i / 10.0
        u = u0 + t * (u1 - u0)
        assert s.Value(u, v0).Distance(p1.Value(t)) < 0.05
    for i in range(11):
        t = i / 10.0
        u = u0 + t * (u1 - u0)
        assert s.Value(u, v1).Distance(p2.Value(t)) < 0.05


def test_GeomFill_Gordon_OffsetPlane_NetworkAtNonZeroZ():
    z = 5.0
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, z), (1, 0, 0), 0.0, 1.0), trimmed_line(gp_Pnt(0, 1, z), (1, 0, 0), 0.0, 1.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, z), (0, 1, 0), 0.0, 1.0), trimmed_line(gp_Pnt(1, 0, z), (0, 1, 0), 0.0, 1.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    u, v = mid(s)
    assert abs(s.Value(u, v).Z() - z) <= 0.01


def test_GeomFill_Gordon_TiltedPlane_DiagonalCurves():
    profiles = curves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 1)), makeLinearBSpline(gp_Pnt(0, 1, 1), gp_Pnt(1, 1, 2))]
    )
    guides = curves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 1)), makeLinearBSpline(gp_Pnt(1, 0, 1), gp_Pnt(1, 1, 2))]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    u0, u1, v0, v1 = bounds(s)
    for i in range(6):
        for j in range(6):
            p = s.Value(u0 + i * (u1 - u0) / 5.0, v0 + j * (v1 - v0) / 5.0)
            assert abs(p.Z() - (p.X() + p.Y())) <= 0.05


def test_GeomFill_Gordon_RectangularNotSquare_2x3AspectRatio():
    profiles = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (1, 0, 0), 0.0, 2.0), trimmed_line(gp_Pnt(0, 3, 0), (1, 0, 0), 0.0, 2.0)]
    )
    guides = curves(
        [trimmed_line(gp_Pnt(0, 0, 0), (0, 1, 0), 0.0, 3.0), trimmed_line(gp_Pnt(2, 0, 0), (0, 1, 0), 0.0, 3.0)]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    s = g.Surface()
    u, v = mid(s)
    p = s.Value(u, v)
    assert abs(p.X() - 1.0) <= 0.1
    assert abs(p.Y() - 1.5) <= 0.1


def test_GeomFill_Gordon_WavySurface_SinusoidalProfilesAndGuides():
    profiles = curves(
        [makeSineBSpline(0.0, 1.0, 0.0, 0.3), makeSineBSpline(0.0, 1.0, 0.5, 0.6), makeSineBSpline(0.0, 1.0, 1.0, 0.3)]
    )
    g = gordon(profiles, unit_linear_guides(), 0.01)
    assert g.IsDone()
    s = g.Surface()
    assert s is not None
    u, v = mid(s)
    assert abs(s.Value(u, v).Z() - 0.6) <= 0.05


def test_GeomFill_Gordon_NetworkSurface_UClosedNetwork_ProducesUPeriodicSurface():
    profiles = bcurves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(0, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 1), gp_Pnt(0, 1, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 2, 0), gp_Pnt(1, 2, 0), gp_Pnt(0, 2, 0)),
        ]
    )
    guides = bcurves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 2, 0)),
            makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 2, 0)),
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 2, 0)),
        ]
    )
    net = network_surface(
        profiles, guides, floats([0.0, 0.5, 1.0]), floats([0.0, 0.5, 1.0]), None, CONF, True, False
    )
    net.Perform()
    assert net.IsDone()
    s = net.Surface()
    assert s is not None
    assert s.IsUPeriodic()


def test_GeomFill_Gordon_NetworkSurface_UClosedNetwork_UsesInputToleranceForPeriodicity():
    gap = 1.0e-5
    tol = 1.0e-4
    profiles = bcurves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(gap, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 1), gp_Pnt(gap, 1, 0)),
            makeQuadraticBSpline(gp_Pnt(0, 2, 0), gp_Pnt(1, 2, 0), gp_Pnt(gap, 2, 0)),
        ]
    )
    guides = bcurves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 2, 0)),
            makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 2, 0)),
            makeLinearBSpline(gp_Pnt(gap, 0, 0), gp_Pnt(gap, 2, 0)),
        ]
    )
    net = network_surface(profiles, guides, floats([0.0, 0.5, 1.0]), floats([0.0, 0.5, 1.0]), None, tol, True, False)
    net.Perform()
    assert net.IsDone(), net.Status()
    assert net.Surface().IsUPeriodic()


def test_GeomFill_Gordon_NetworkSurface_InvalidPreparedNetworkReportsStatus():
    profiles = bcurves([makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0))])
    guides = bcurves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)), makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0))]
    )
    net = network_surface(profiles, guides, floats([0.0]), floats([0.0, 1.0]), None, CONF, False, False)
    assert net.Status() == NRS.NotStarted
    net.Perform()
    assert net.IsDone() is False
    assert net.Status() == NRS.InvalidInput
    with pytest.raises(StdFail_NotDone):
        net.Surface()


def test_GeomFill_Gordon_NetworkSurface_InvalidWeightsReportsInvalidInput():
    profiles = bcurves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0)), makeLinearBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0))]
    )
    guides = bcurves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)), makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0))]
    )
    guide_params = floats([0.0, 1.0])
    weights = makeUnitWeightGrid(profiles, guide_params)
    weights[2, 2] = 0.0
    net = network_surface(profiles, guides, floats([0.0, 1.0]), guide_params, weights, CONF, False, False)
    net.Perform()
    assert net.IsDone() is False
    assert net.Status() == NRS.InvalidInput


def test_GeomFill_Gordon_NetworkSurface_CompatibleRationalWeightsProducesRationalSurface():
    profiles = bcurves(
        [
            makeRationalQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, 0), gp_Pnt(1, 0, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(0.5, 0.5, 0), gp_Pnt(1, 0.5, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.5, 1, 0), gp_Pnt(1, 1, 0), 0.5),
        ]
    )
    guides = bcurves(
        [
            makeWeightedLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0), 1.0),
            makeWeightedLinearBSpline(gp_Pnt(0.5, 0, 0), gp_Pnt(0.5, 1, 0), 0.75),
            makeWeightedLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0), 1.0),
        ]
    )
    weights = NCollection_Array2[float](1, 3, 1, 3)
    for ip in range(1, 4):
        weights[1, ip] = 1.0
        weights[2, ip] = 0.75
        weights[3, ip] = 1.0
    net = network_surface(
        profiles, guides, floats([0.0, 0.5, 1.0]), floats([0.0, 0.5, 1.0]), weights, CONF, False, False
    )
    net.Perform()
    assert net.IsDone()
    s = net.Surface()
    assert s.IsURational() or s.IsVRational()


def test_GeomFill_Gordon_NetworkSurface_IncompatibleRationalFamilyReportsStatus():
    profiles = bcurves(
        [
            makeRationalQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, 0), gp_Pnt(1, 0, 0), 0.5),
            makeWeightedLinearBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0), 1.0),
        ]
    )
    guides = bcurves(
        [makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)), makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0))]
    )
    net = network_surface(profiles, guides, floats([0.0, 1.0]), floats([0.0, 1.0]), None, CONF, False, False)
    net.Perform()
    assert net.IsDone() is False
    assert net.Status() == NRS.CurveCompatibilityFailed


def test_GeomFill_Gordon_NetworkSurface_RationalDegreeOverflowReportsStatus():
    profiles, guides = rational_degree9_network(True)
    net = network_surface(
        profiles, guides, floats([0.0, 0.5, 1.0]), floats([0.0, 0.5, 1.0]), None, CONF, False, False
    )
    net.Perform()
    assert net.IsDone() is False
    assert net.Status() == NRS.RationalDegreeOverflow


def test_GeomFill_Gordon_RationalProfilesWithPolynomialGuidesProducesSurface():
    profiles = curves(
        [
            makeRationalQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0.5, 0, 0), gp_Pnt(1, 0, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(0.5, 0.5, 0), gp_Pnt(1, 0.5, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(0.5, 1, 0), gp_Pnt(1, 1, 0), 0.5),
        ]
    )
    guides = curves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0)),
            makeLinearBSpline(gp_Pnt(0.5, 0, 0), gp_Pnt(0.5, 1, 0)),
            makeLinearBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0)),
        ]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.IsApproximate() is False
    assert g.Surface().IsURational() or g.Surface().IsVRational()
    assert g.Report().MaxProfileDeviation <= CONF
    assert g.Report().MaxGuideDeviation <= CONF


def test_GeomFill_Gordon_PolynomialProfilesWithRationalGuidesProducesSurface():
    profiles = curves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0)),
            makeLinearBSpline(gp_Pnt(0, 0.5, 0), gp_Pnt(1, 0.5, 0)),
            makeLinearBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0)),
        ]
    )
    guides = curves(
        [
            makeRationalQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 0.5, 0), gp_Pnt(0, 1, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(0.5, 0, 0), gp_Pnt(0.5, 0.5, 0), gp_Pnt(0.5, 1, 0), 0.5),
            makeRationalQuadraticBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 0.5, 0), gp_Pnt(1, 1, 0), 0.5),
        ]
    )
    g = gordon(profiles, guides, CONF)
    assert g.IsDone()
    assert g.IsApproximate() is False
    assert g.Surface().IsURational() or g.Surface().IsVRational()
    assert g.Report().MaxProfileDeviation <= CONF
    assert g.Report().MaxGuideDeviation <= CONF


def test_GeomFill_Gordon_ApproximateFallbackCanRecoverRationalDegreeOverflow():
    profiles, guides = rational_degree9_network(False)
    g = gordon(profiles, guides, CONF, mode=AM.AllowApproximateFallback)
    assert g.IsDone(), g.Status()
    assert g.IsApproximate() is True
    rep = g.Report()
    assert rep.Status == RS.Done
    assert rep.IsApproximate is True
    assert rep.FailedStage == BS.NotStarted
    assert rep.MaxApproximationDeviation <= 0.001
    s = g.Surface()
    assert s is not None

    nb = 48
    u0, u1, v0, v1 = bounds(s)
    profile0 = profiles[profiles.Lower()]
    guide0 = guides[guides.Lower()]
    max_dev = 0.0
    for iu in range(nb + 1):
        up = iu / nb
        u = u0 + up * (u1 - u0)
        pp = profile0.Value(up)
        for iv in range(nb + 1):
            vp = iv / nb
            v = v0 + vp * (v1 - v0)
            gpnt = guide0.Value(vp)
            max_dev = max(max_dev, s.Value(u, v).Distance(gp_Pnt(pp.X(), gpnt.Y(), 0.0)))
    assert max_dev <= 0.002


def test_GeomFill_Gordon_ExactOnlyReportsRationalDegreeOverflow():
    profiles, guides = rational_degree9_network(False)
    g = GeomFill_Gordon()
    g.Init(profiles, guides, CONF)
    assert g.GetApproximationMode() == AM.ExactOnly
    g.Perform()
    assert g.IsDone() is False
    assert g.IsApproximate() is False
    assert g.Status() == RS.RationalDegreeOverflow
    rep = g.Report()
    assert rep.Status == RS.RationalDegreeOverflow
    assert rep.FailedStage == BS.ExactConstruction
    assert rep.IsApproximate is False


def test_GeomFill_Gordon_ExactOnlyReparametrizesRationalCurves():
    g = gordon(*rational_quadratic_line_network(), CONF)
    assert g.IsDone()
    assert g.IsApproximate() is False
    assert g.Status() == RS.Done
    rep = g.Report()
    assert rep.Status == RS.Done
    assert rep.FailedStage == BS.NotStarted
    assert rep.IsApproximate is False
    assert abs(rep.MaxReparametrizationDeviation) <= 1.0e-12


def test_GeomFill_Gordon_ApproximationModeUsesExactRationalReparametrizationWhenPossible():
    g = gordon(*rational_quadratic_line_network(), CONF, mode=AM.AllowApproximateFallback)
    assert g.IsDone(), g.Status()
    assert g.IsApproximate() is False
    rep = g.Report()
    assert rep.Status == RS.Done
    assert rep.IsApproximate is False
    assert abs(rep.MaxReparametrizationDeviation) <= 1.0e-12
    assert g.Surface() is not None


def test_GeomFill_Gordon_ExactRationalReparametrizationRepeatPerformKeepsReportStable():
    g = gordon(*rational_quadratic_line_network(), CONF, mode=AM.AllowApproximateFallback)
    centers = []
    for _ in range(2):
        assert g.IsDone(), g.Status()
        assert g.IsApproximate() is False
        rep = g.Report()
        assert rep.Status == RS.Done
        assert rep.FailedStage == BS.NotStarted
        assert rep.IsApproximate is False
        assert abs(rep.MaxContactGap) <= 1.0e-12
        assert abs(rep.MaxReparametrizationDeviation) <= 1.0e-12
        assert abs(rep.MaxApproximationDeviation) <= 1.0e-12
        centers.append(g.Surface().Value(0.5, 0.5))
        g.Perform()
    assert centers[0].Distance(centers[1]) <= CONF


def test_GeomFill_Gordon_NetworkSurface_VClosedNetwork_ProducesVPeriodicSurface():
    profiles = bcurves(
        [
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(2, 0, 0)),
            makeLinearBSpline(gp_Pnt(0, 1, 0), gp_Pnt(2, 1, 1)),
            makeLinearBSpline(gp_Pnt(0, 0, 0), gp_Pnt(2, 0, 0)),
        ]
    )
    guides = bcurves(
        [
            makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(0, 1, 0), gp_Pnt(0, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(1, 0, 0)),
            makeQuadraticBSpline(gp_Pnt(2, 0, 0), gp_Pnt(2, 1, 0), gp_Pnt(2, 0, 0)),
        ]
    )
    net = network_surface(
        profiles, guides, floats([0.0, 0.5, 1.0]), floats([0.0, 0.5, 1.0]), None, CONF, False, True
    )
    net.Perform()
    assert net.IsDone()
    s = net.Surface()
    assert s is not None
    assert s.IsVPeriodic()


def _dense(network, tol=CONF):
    g = gordon(network.Profiles, network.Guides, tol)
    assert g.IsDone(), g.Status()
    assert g.IsApproximate() is False
    verifyUniformNetworkInterpolation(g.Surface(), network, tol)


def test_GeomFill_Gordon_DenseWavyFiveByFiveNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(5, 5, wavyHeight))


def test_GeomFill_Gordon_DenseSaddleSevenByFourNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(7, 4, saddleHeight))


def test_GeomFill_Gordon_DenseRippleFourBySevenNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(4, 7, rippleHeight))


def test_GeomFill_Gordon_DenseWavyEightByEightNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(8, 8, wavyHeight))


def test_GeomFill_Gordon_TranslatedScaledSixByFiveNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(6, 5, rippleHeight, (1.0e5, -2.0e5, 3.0e5), 250.0), 1.0e-5)


def test_GeomFill_Gordon_SmallScaledFiveBySixNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(5, 6, saddleHeight, (0.0, 0.0, 0.0), 0.01))


def test_GeomFill_Gordon_DenseWavyNetwork_ParallelConstructionMatchesSerialQuality():
    network = AnalyticNetwork(6, 6, wavyHeight)
    serial = gordon(network.Profiles, network.Guides, CONF)
    assert serial.IsDone(), serial.Status()
    par = gordon(network.Profiles, network.Guides, CONF, parallel=True)
    assert par.IsDone(), par.Status()
    verifyUniformNetworkInterpolation(serial.Surface(), network, CONF)
    verifyUniformNetworkInterpolation(par.Surface(), network, CONF)
    nb = 24
    s1 = serial.Surface()
    s2 = par.Surface()
    for iu in range(nb + 1):
        for iv in range(nb + 1):
            u = iu / nb
            v = iv / nb
            assert s1.Value(u, v).Distance(s2.Value(u, v)) <= CONF


def test_GeomFill_Gordon_DenseSaddleNetwork_RepeatedPerformMaintainsQuality():
    network = AnalyticNetwork(6, 5, saddleHeight)
    g = gordon(network.Profiles, network.Guides, CONF)
    assert g.IsDone(), g.Status()
    first = g.Surface()
    g.Perform()
    assert g.IsDone(), g.Status()
    verifyUniformNetworkInterpolation(g.Surface(), network, CONF)
    nb = 24
    second = g.Surface()
    for iu in range(nb + 1):
        for iv in range(nb + 1):
            u = iu / nb
            v = iv / nb
            assert first.Value(u, v).Distance(second.Value(u, v)) <= CONF


def test_GeomFill_Gordon_DenseRippleNineByThreeNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(9, 3, rippleHeight))


def test_GeomFill_Gordon_DenseWavyThreeByNineNetwork_InterpolatesAllInputCurves():
    _dense(AnalyticNetwork(3, 9, wavyHeight))


def test_GeomFill_Gordon_ClosedBSplineProfilesWithInteriorGuides_ProducePeriodicSurface():
    p1 = makeClosedBSplineProfile(0.0, 1.0, 1.0)
    p2 = makeClosedBSplineProfile(1.0, 1.15, 0.85)
    assert p1.IsPeriodic() is False
    assert p1.Value(p1.FirstParameter()).Distance(p1.Value(p1.LastParameter())) <= CONF
    guides = curves([makeLinearBSpline(p1.Value(t), p2.Value(t)) for t in (0.12, 0.34, 0.59, 0.83)])
    g = gordon(curves([p1, p2]), guides, CONF)
    assert g.IsDone(), g.Status()
    assert g.IsApproximate() is False
    assert g.Surface().IsUPeriodic()
    assert g.Report().MaxProfileDeviation <= CONF
    assert g.Report().MaxGuideDeviation <= CONF


def test_GeomFill_Gordon_NetworkSurface_ClosedNetworkWithNonUnitUParameters_ProducesUPeriodicSurface():
    p1 = makeQuadraticBSpline(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(0, 0, 0), 2.0, 5.0)
    p2 = makeQuadraticBSpline(gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 1), gp_Pnt(0, 1, 0), 2.0, 5.0)
    profiles = bcurves([p1, p2])
    guide_params = floats([2.0, 3.5])
    guides = bcurves([makeLinearBSpline(p1.Value(t), p2.Value(t)) for t in (2.0, 3.5)])
    net = network_surface(profiles, guides, floats([0.0, 1.0]), guide_params, None, CONF, True, False)
    net.Perform()
    assert net.IsDone(), net.Status()
    assert net.Surface().IsUPeriodic()
