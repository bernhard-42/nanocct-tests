# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_CircleToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Convert import (
    Convert_CircleToBSplineCurve,
    Convert_Polynomial,
    Convert_QuasiAngular,
    Convert_RationalC1,
    Convert_TgtThetaOver2,
)
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d


def _circ(x, y, r):
    return gp_Circ2d(gp_Ax2d(gp_Pnt2d(x, y), gp_Dir2d(1.0, 0.0)), r)


def _check_weights_and_knots(conv):
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
    knots = conv.Knots()
    for i in range(2, conv.NbKnots() + 1):
        assert knots[i] > knots[i - 1]


def test_Convert_CircleToBSplineCurveTest_FullCircle_TgtThetaOver2():
    conv = Convert_CircleToBSplineCurve(_circ(0.0, 0.0, 5.0), Convert_TgtThetaOver2)
    assert conv.Degree() == 2
    assert conv.IsPeriodic() is True
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    _check_weights_and_knots(conv)


def test_Convert_CircleToBSplineCurveTest_FullCircle_RationalC1():
    conv = Convert_CircleToBSplineCurve(_circ(1.0, 2.0, 3.0), Convert_RationalC1)
    assert conv.IsPeriodic() is True
    assert conv.NbPoles() > 0
    _check_weights_and_knots(conv)


def test_Convert_CircleToBSplineCurveTest_Arc_TgtThetaOver2():
    circ = _circ(0.0, 0.0, 1.0)
    u1 = math.pi / 6.0
    u2 = 5.0 * math.pi / 3.0
    conv = Convert_CircleToBSplineCurve(circ, u1, u2, Convert_TgtThetaOver2)
    assert conv.IsPeriodic() is False
    assert conv.Degree() == 2
    assert conv.NbPoles() > 0
    poles = conv.Poles()
    r = circ.Radius()
    c = circ.Location()
    xd = circ.XAxis().Direction()
    yd = circ.YAxis().Direction()
    fx = c.X() + r * (math.cos(u1) * xd.X() + math.sin(u1) * yd.X())
    fy = c.Y() + r * (math.cos(u1) * xd.Y() + math.sin(u1) * yd.Y())
    assert abs(poles[1].X() - fx) <= 1.0e-10
    assert abs(poles[1].Y() - fy) <= 1.0e-10
    lx = c.X() + r * (math.cos(u2) * xd.X() + math.sin(u2) * yd.X())
    ly = c.Y() + r * (math.cos(u2) * xd.Y() + math.sin(u2) * yd.Y())
    assert abs(poles[conv.NbPoles()].X() - lx) <= 1.0e-10
    assert abs(poles[conv.NbPoles()].Y() - ly) <= 1.0e-10
    _check_weights_and_knots(conv)


def test_Convert_CircleToBSplineCurveTest_Arc_QuasiAngular():
    conv = Convert_CircleToBSplineCurve(_circ(0.0, 0.0, 2.0), 0.0, math.pi, Convert_QuasiAngular)
    assert conv.IsPeriodic() is False
    assert conv.Degree() == 6
    assert conv.NbPoles() > 0
    _check_weights_and_knots(conv)


def test_Convert_CircleToBSplineCurveTest_Arc_Polynomial():
    conv = Convert_CircleToBSplineCurve(_circ(0.0, 0.0, 1.0), 0.0, math.pi * 0.5, Convert_Polynomial)
    assert conv.IsPeriodic() is False
    assert conv.Degree() == 7
    assert conv.NbPoles() == 8


def test_Convert_CircleToBSplineCurveTest_WeightsArePositive():
    conv = Convert_CircleToBSplineCurve(_circ(0.0, 0.0, 1.0), Convert_TgtThetaOver2)
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
