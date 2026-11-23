# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AppDef_LeastSquare_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.AppDef import (AppDef_BSpParLeastSquareOfMyBSplGradientOfBSplineCompute, AppDef_MultiLine,
                            AppDef_MultiPointConstraint, AppDef_ParLeastSquareOfMyGradientbisOfBSplineCompute,
                            AppDef_ParLeastSquareOfMyGradientOfCompute, AppDef_ParLeastSquareOfTheGradient,
                            AppDef_TheLeastSquares)
from nanocct.AppParCurves import AppParCurves_CurvaturePoint, AppParCurves_NoConstraint, AppParCurves_PassPoint
from nanocct.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Vec2d
from nanocct.math import math_Vector


def _check_endpoint_constraints(fit_class):
    line = AppDef_MultiLine(21)
    params = math_Vector(1, 21)
    for i in range(1, 22):
        u = (i - 1) / 20.0
        # SetValue shares the point arrays, so each row needs an independent object.
        point = AppDef_MultiPointConstraint(1, 1)
        point.SetPoint(1, gp_Pnt(10 + u, 20 + u * u, 30 + u * u * u))
        point.SetTang(1, gp_Vec(1, 2 * u, 3 * u * u))
        point.SetCurv(1, gp_Vec(0, 2, 6 * u))
        point.SetPoint2d(2, gp_Pnt2d(40 + u, 50 + u * u))
        point.SetTang2d(2, gp_Vec2d(1, 2 * u))
        point.SetCurv2d(2, gp_Vec2d(0, 2))
        line.SetValue(i, point)
        params[i] = u

    constraints = ((AppParCurves_PassPoint, AppParCurves_CurvaturePoint),
                   (AppParCurves_CurvaturePoint, AppParCurves_PassPoint),
                   (AppParCurves_NoConstraint, AppParCurves_CurvaturePoint),
                   (AppParCurves_CurvaturePoint, AppParCurves_NoConstraint),
                   (AppParCurves_CurvaturePoint, AppParCurves_CurvaturePoint))
    for first, last in constraints:
        where = f"{first}, {last}"
        fit = fit_class(line, 1, 21, first, last, 8)
        # A degree-seven Bezier uses lambda = 1/7 for the supplied derivatives.
        fit.Perform(params, 1.0 / 7.0, 1.0 / 7.0)
        assert fit.IsDone() is True, where
        curve = fit.BezierValue()
        for u in (0.0, 1.0):
            p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
            curve.D2(1, u, p, d1, d2)
            p2, d12, d22 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
            curve.D2(2, u, p2, d12, d22)
            # The input is a cubic polynomial, so all endpoint values have an exact fit.
            assert p.Distance(gp_Pnt(10 + u, 20 + u * u, 30 + u * u * u)) == pytest.approx(0, abs=1e-9), where
            assert p2.Distance(gp_Pnt2d(40 + u, 50 + u * u)) == pytest.approx(0, abs=1e-9), where
            if (first if u == 0 else last) == AppParCurves_CurvaturePoint:
                assert (d1 - gp_Vec(1, 2 * u, 3 * u * u)).Magnitude() == pytest.approx(0, abs=1e-9), where
                assert (d2 - gp_Vec(0, 2, 6 * u)).Magnitude() == pytest.approx(0, abs=1e-8), where
                assert (d12 - gp_Vec2d(1, 2 * u)).Magnitude() == pytest.approx(0, abs=1e-9), where
                assert (d22 - gp_Vec2d(0, 2)).Magnitude() == pytest.approx(0, abs=1e-8), where


def test_AppDef_LeastSquareTest_EndpointCurvature_TheLeastSquares():
    _check_endpoint_constraints(AppDef_TheLeastSquares)


def test_AppDef_LeastSquareTest_EndpointCurvature_BSpParLeastSquare():
    _check_endpoint_constraints(AppDef_BSpParLeastSquareOfMyBSplGradientOfBSplineCompute)


def test_AppDef_LeastSquareTest_EndpointCurvature_MyGradientOfCompute():
    _check_endpoint_constraints(AppDef_ParLeastSquareOfMyGradientOfCompute)


def test_AppDef_LeastSquareTest_EndpointCurvature_MyGradientbisOfBSplineCompute():
    _check_endpoint_constraints(AppDef_ParLeastSquareOfMyGradientbisOfBSplineCompute)


def test_AppDef_LeastSquareTest_EndpointCurvature_TheGradient():
    _check_endpoint_constraints(AppDef_ParLeastSquareOfTheGradient)
