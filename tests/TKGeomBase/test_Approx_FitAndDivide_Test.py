# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Approx_FitAndDivide_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.AppCont import AppCont_Function, AppCont_LeastSquare
from nanocct.AppParCurves import AppParCurves_NoConstraint, AppParCurves_PassPoint, AppParCurves_TangencyPoint
from nanocct.Approx import Approx_FitAndDivide
from nanocct.Geom import Geom_BezierCurve
from nanocct.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Vec2d
from nanocct.NCollection import NCollection_Array1

pytestmark = pytest.mark.skip(reason="a Python subclass of an abstract OCCT class: nanocct binds no trampolines (docs/Excluded.md, Python subclasses of OCCT's abstract interfaces)")

TOL = 1.0e-5


class _EndLayer(AppCont_Function):
    """y = exp((u - 1) / width): an exponential end layer of the given width in parameter units."""

    def __init__(self, width):
        super().__init__()
        self.myNbPnt = 1
        self.myNbPnt2d = 0
        self._width = width

    def FirstParameter(self):
        return 0.0

    def LastParameter(self):
        return 1.0

    def Value(self, u, points2d, points):
        points[points.Lower()] = gp_Pnt(u, math.exp((u - 1.0) / self._width), 0.0)
        return True

    def D1(self, u, vectors2d, vectors):
        vectors[vectors.Lower()] = gp_Vec(1.0, math.exp((u - 1.0) / self._width) / self._width, 0.0)
        return True


class _TranslatedParabola(AppCont_Function):
    def __init__(self):
        super().__init__()
        self.myNbPnt = 1
        self.myNbPnt2d = 1

    def FirstParameter(self):
        return 0.0

    def LastParameter(self):
        return 1.0

    def Value(self, u, points2d, points):
        points2d[points2d.Lower()] = gp_Pnt2d(1.0e6 + u, 1.0e6 + u * u)
        points[points.Lower()] = gp_Pnt(1.0e6 + u, 1.0e6 + u * u, 1.0e6 - u)
        return True

    def D1(self, u, vectors2d, vectors):
        vectors2d[vectors2d.Lower()] = gp_Vec2d(1.0, 2.0 * u)
        vectors[vectors.Lower()] = gp_Vec(1.0, 2.0 * u, -1.0)
        return True


def _bezier_of(multi_curve):
    poles = NCollection_Array1[gp_Pnt](1, multi_curve.Degree() + 1)
    multi_curve.Curve(1, poles)
    return Geom_BezierCurve(poles)


def _check_end_layer(fit, width):
    function = _EndLayer(width)
    fit.SetMaxSegments(100)
    fit.Perform(function)
    assert fit.IsAllApproximated() is True
    assert fit.NbMultiCurves() > 0
    for segment in range(1, fit.NbMultiCurves() + 1):
        first, last = fit.Parameters(segment)
        error3d, _ = fit.Error(segment)
        assert error3d <= TOL, segment
        curve = _bezier_of(fit.Value(segment))
        for sample in range(101):
            fraction = sample / 100.0
            t = first + (last - first) * fraction
            expected = gp_Pnt(t, math.exp((t - 1.0) / width), 0.0)
            assert curve.EvalD0(fraction).Distance(expected) <= TOL, (segment, sample)


def test_ApproxFitAndDivideTest_DisabledHangCheckingResolvesNarrowEndLayer():
    fit = Approx_FitAndDivide(8, 8, TOL, TOL, True)
    fit.SetHangChecking(False)
    _check_end_layer(fit, 1.0e-7)


def test_ApproxFitAndDivideTest_DefaultHangCheckingApproximatesSmoothEndLayer():
    _check_end_layer(Approx_FitAndDivide(8, 8, TOL, TOL, True), 0.02)


def test_ApproxFitAndDivideTest_LeastSquaresPreservesTranslatedParabola():
    function = _TranslatedParabola()
    for first in (AppParCurves_PassPoint, AppParCurves_TangencyPoint):
        for last in (AppParCurves_NoConstraint, AppParCurves_PassPoint, AppParCurves_TangencyPoint):
            fit = AppCont_LeastSquare(function, 0.0, 1.0, first, last, 8, 17)
            assert fit.IsDone() is True, (first, last)
            _, error3d, error2d = fit.Error()
            assert error3d < 1.0e-8, (first, last)
            assert error2d < 1.0e-8, (first, last)
            curve = _bezier_of(fit.Value())
            for i in range(101):
                u = i / 100.0
                assert curve.EvalD0(u).Distance(gp_Pnt(1.0e6 + u, 1.0e6 + u * u, 1.0e6 - u)) < 1.0e-8, (first, last, u)


def test_ApproxFitAndDivideTest_LeastSquaresPreservesTranslatedParabolaWithFreeStart():
    fit = AppCont_LeastSquare(_TranslatedParabola(), 0.0, 1.0, AppParCurves_NoConstraint, AppParCurves_TangencyPoint, 8, 17)
    assert fit.IsDone() is True
    _, error3d, error2d = fit.Error()
    assert error3d < 1.0e-8
    assert error2d < 1.0e-8
