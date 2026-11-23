# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomAdaptor_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_Circle, Geom_Ellipse, Geom_Line, Geom_OffsetCurve, Geom_TrimmedCurve
from nanocct.GeomAdaptor import GeomAdaptor, GeomAdaptor_Curve
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_GeomAdaptorTest_MakeCurve_PeriodicIntervals_PreserveParameterChart():
    axis = gp_Ax2(gp_Pnt(2, -3, 1), gp_Dir(1, 1, 1))
    curves = (Geom_Circle(axis, 4), Geom_Ellipse(axis, 5, 2))
    period = 2 * math.acos(-1.0)
    ranges = ((-8.0, -3.0), (5.0, 8.0), (7.0, 11.0), (0.0, period), (7.0, 7.0 + period), (7.0, 21.0))
    for curve in curves:
        for first, last in ranges:
            trim = Geom_TrimmedCurve(curve, first, last, True, False)
            result = GeomAdaptor.MakeCurve_s(GeomAdaptor_Curve(trim))
            assert result is not None
            assert result.FirstParameter() == _eq(first)
            assert result.LastParameter() == _eq(last)
            for t in (first, (first + last) / 2, last):
                assert result.EvalD0(t).Distance(trim.EvalD0(t)) < 1e-12, (first, last, t)
                assert (result.EvalD1(t).D1 - trim.EvalD1(t).D1).Magnitude() < 1e-12, (first, last, t)


def test_GeomAdaptorTest_MakeCurve_BoundedLine_PreservesInterval():
    line = Geom_Line(gp_Pnt(2, -3, 1), gp_Dir(1, 2, 3))
    result = GeomAdaptor.MakeCurve_s(GeomAdaptor_Curve(line, -5, 7))
    assert result is not None
    assert result.FirstParameter() == _eq(-5)
    assert result.LastParameter() == _eq(7)
    assert result.EvalD0(-5).Distance(line.EvalD0(-5)) < 1e-12
    assert result.EvalD0(7).Distance(line.EvalD0(7)) < 1e-12


def test_GeomAdaptorTest_CopyAndOffsetPreserveReversedMultiPeriodTrim():
    basis = Geom_Circle(gp_Ax2(gp_Pnt(2, -3, 1), gp_Dir(0, 0, 1)), 4)
    trim = Geom_TrimmedCurve(basis, 18.0, 23.0, False, False)
    copy = trim.Copy()
    assert isinstance(copy, Geom_TrimmedCurve)
    offset = Geom_OffsetCurve(trim, 0.5, gp_Dir(0, 0, 1))
    assert copy.FirstParameter() == _eq(trim.FirstParameter())
    assert copy.LastParameter() == _eq(trim.LastParameter())
    assert offset.FirstParameter() == _eq(trim.FirstParameter())
    assert offset.LastParameter() == _eq(trim.LastParameter())
    t = (trim.FirstParameter() + trim.LastParameter()) / 2
    assert copy.EvalD0(t).Distance(trim.EvalD0(t)) <= 1e-12
    assert offset.EvalD0(t).Distance(trim.EvalD0(t)) == pytest.approx(0.5, abs=1e-12)
