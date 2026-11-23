# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepToGeom_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.NCollection import NCollection_HArray1
from nanocct.Precision import Precision
from nanocct.StepData import StepData_LFalse
from nanocct.StepGeom import (StepGeom_bscfUnspecified, StepGeom_BSplineCurveWithKnots,
                              StepGeom_BSplineCurveWithKnotsAndRationalBSplineCurve, StepGeom_CartesianPoint,
                              StepGeom_ktUnspecified)
from nanocct.StepToGeom import StepToGeom
from nanocct.TCollection import TCollection_HAsciiString


def _array(kind, values):
    a = NCollection_HArray1[kind](1, len(values))
    for i, v in enumerate(values, 1):
        a.SetValue(i, v)
    return a


def _poles(name, n):
    poles = NCollection_HArray1[StepGeom_CartesianPoint](1, n)
    for i in range(1, n + 1):
        point = StepGeom_CartesianPoint()
        point.Init3D(name, float(i), 0.0, 0.0)
        poles.SetValue(i, point)
    return poles


def _curve(nb_poles, mults, knots):
    name = TCollection_HAsciiString("curve")
    curve = StepGeom_BSplineCurveWithKnots()
    curve.Init(name, 1, _poles(name, nb_poles), StepGeom_bscfUnspecified, StepData_LFalse, StepData_LFalse,
               _array(int, mults), _array(float, knots), StepGeom_ktUnspecified)
    return curve


def _linear_curve(first_knot):
    return _curve(2, [2, 2], [first_knot, 1.0])


def _rational_linear_curve(first_weight, second_weight):
    curve = _linear_curve(0.0)
    rational = StepGeom_BSplineCurveWithKnotsAndRationalBSplineCurve()
    rational.Init(curve.Name(), curve.Degree(), curve.ControlPointsList(), curve.CurveForm(), curve.ClosedCurve(),
                  curve.SelfIntersect(), curve.KnotMultiplicities(), curve.Knots(), StepGeom_ktUnspecified,
                  _array(float, [first_weight, second_weight]))
    return rational


def test_StepToGeomTest_RejectsMismatchedBSplineKnotArrays():
    assert StepToGeom.MakeBSplineCurve_s(_curve(3, [2, 2], [0.0])) is None


def test_StepToGeomTest_RejectsMissingBSplineData():
    assert StepToGeom.MakeBSplineCurve_s(StepGeom_BSplineCurveWithKnots()) is None


def test_StepToGeomTest_RejectsInvalidKnotValues():
    assert StepToGeom.MakeBSplineCurve_s(_linear_curve(Precision.Infinite_s())) is None
    assert StepToGeom.MakeBSplineCurve_s(_linear_curve(-Precision.Infinite_s())) is None
    assert StepToGeom.MakeBSplineCurve_s(_linear_curve(math.nan)) is None


def test_StepToGeomTest_RejectsLargeMergedKnotMultiplicities():
    assert StepToGeom.MakeBSplineCurve_s(_curve(2, [2000000000, 2000000000, 2], [0.0, 0.0, 1.0])) is None


def test_StepToGeomTest_RejectsInvalidInteriorKnotMultiplicity():
    assert StepToGeom.MakeBSplineCurve_s(_curve(4, [2, 2, 2], [0.0, 1.0, 2.0])) is None


def test_StepToGeomTest_RejectsOversizedMultiplicitySum():
    assert StepToGeom.MakeBSplineCurve_s(_curve(2, [1, 1, 1, 1, 1], [0.0, 1.0, 2.0, 3.0, 4.0])) is None


def test_StepToGeomTest_ValidatesRationalWeights():
    assert StepToGeom.MakeBSplineCurve_s(_rational_linear_curve(1.0, 2.0)) is not None
    assert StepToGeom.MakeBSplineCurve_s(_rational_linear_curve(1.0, math.nan)) is None
    assert StepToGeom.MakeBSplineCurve_s(_rational_linear_curve(1.0, 0.0)) is None


def test_StepToGeomTest_ConvertsValidBSplineCurve():
    assert StepToGeom.MakeBSplineCurve_s(_linear_curve(0.0)) is not None
