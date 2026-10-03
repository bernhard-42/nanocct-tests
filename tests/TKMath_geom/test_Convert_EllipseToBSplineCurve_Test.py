# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_EllipseToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Convert import Convert_EllipseToBSplineCurve, Convert_RationalC1, Convert_TgtThetaOver2
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Elips2d, gp_Pnt2d


def _elips(x, y, maj, mnr):
    return gp_Elips2d(gp_Ax2d(gp_Pnt2d(x, y), gp_Dir2d(1.0, 0.0)), maj, mnr)


def _check_weights_and_knots(conv):
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
    knots = conv.Knots()
    for i in range(2, conv.NbKnots() + 1):
        assert knots[i] > knots[i - 1]


def test_Convert_EllipseToBSplineCurveTest_FullEllipse_TgtThetaOver2():
    conv = Convert_EllipseToBSplineCurve(_elips(0.0, 0.0, 5.0, 3.0), Convert_TgtThetaOver2)
    assert conv.IsPeriodic() is True
    assert conv.Degree() == 2
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    _check_weights_and_knots(conv)
    mults = conv.Multiplicities()
    for i in range(1, conv.NbKnots() + 1):
        assert mults[i] > 0
        assert mults[i] <= conv.Degree() + 1


def test_Convert_EllipseToBSplineCurveTest_Arc_TgtThetaOver2():
    el = _elips(1.0, 1.0, 4.0, 2.0)
    u1 = math.pi / 4.0
    u2 = 3.0 * math.pi / 2.0
    conv = Convert_EllipseToBSplineCurve(el, u1, u2, Convert_TgtThetaOver2)
    assert conv.IsPeriodic() is False
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    poles = conv.Poles()
    maj = el.MajorRadius()
    mnr = el.MinorRadius()
    c = el.Location()
    xd = el.XAxis().Direction()
    yd = el.YAxis().Direction()
    fx = c.X() + maj * math.cos(u1) * xd.X() + mnr * math.sin(u1) * yd.X()
    fy = c.Y() + maj * math.cos(u1) * xd.Y() + mnr * math.sin(u1) * yd.Y()
    assert abs(poles[1].X() - fx) <= 1.0e-10
    assert abs(poles[1].Y() - fy) <= 1.0e-10
    lx = c.X() + maj * math.cos(u2) * xd.X() + mnr * math.sin(u2) * yd.X()
    ly = c.Y() + maj * math.cos(u2) * xd.Y() + mnr * math.sin(u2) * yd.Y()
    assert abs(poles[conv.NbPoles()].X() - lx) <= 1.0e-10
    assert abs(poles[conv.NbPoles()].Y() - ly) <= 1.0e-10
    _check_weights_and_knots(conv)


def test_Convert_EllipseToBSplineCurveTest_FullEllipse_RationalC1():
    conv = Convert_EllipseToBSplineCurve(_elips(0.0, 0.0, 3.0, 1.0), Convert_RationalC1)
    assert conv.IsPeriodic() is True
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    _check_weights_and_knots(conv)


def test_Convert_EllipseToBSplineCurveTest_WeightsArePositive():
    conv = Convert_EllipseToBSplineCurve(_elips(0.0, 0.0, 5.0, 3.0), Convert_TgtThetaOver2)
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
