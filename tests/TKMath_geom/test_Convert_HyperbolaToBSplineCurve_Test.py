# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_HyperbolaToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Convert import Convert_HyperbolaToBSplineCurve
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Hypr2d, gp_Pnt2d


def _hypr(maj, mnr):
    return gp_Hypr2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), maj, mnr)


def _check_ends(conv, h, u1, u2):
    poles = conv.Poles()
    maj = h.MajorRadius()
    mnr = h.MinorRadius()
    c = h.Location()
    xd = h.XAxis().Direction()
    yd = h.YAxis().Direction()
    fx = c.X() + maj * math.cosh(u1) * xd.X() + mnr * math.sinh(u1) * yd.X()
    fy = c.Y() + maj * math.cosh(u1) * xd.Y() + mnr * math.sinh(u1) * yd.Y()
    assert abs(poles[1].X() - fx) <= 1.0e-10
    assert abs(poles[1].Y() - fy) <= 1.0e-10
    lx = c.X() + maj * math.cosh(u2) * xd.X() + mnr * math.sinh(u2) * yd.X()
    ly = c.Y() + maj * math.cosh(u2) * xd.Y() + mnr * math.sinh(u2) * yd.Y()
    assert abs(poles[conv.NbPoles()].X() - lx) <= 1.0e-10
    assert abs(poles[conv.NbPoles()].Y() - ly) <= 1.0e-10


def _check_weights_and_knots(conv):
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
    knots = conv.Knots()
    for i in range(2, conv.NbKnots() + 1):
        assert knots[i] > knots[i - 1]


def test_Convert_HyperbolaToBSplineCurveTest_BasicConversion():
    h = _hypr(3.0, 2.0)
    conv = Convert_HyperbolaToBSplineCurve(h, -1.0, 1.0)
    assert conv.IsPeriodic() is False
    assert conv.Degree() == 2
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    _check_ends(conv, h, -1.0, 1.0)
    _check_weights_and_knots(conv)
    mults = conv.Multiplicities()
    for i in range(1, conv.NbKnots() + 1):
        assert mults[i] > 0
        assert mults[i] <= conv.Degree() + 1


def test_Convert_HyperbolaToBSplineCurveTest_LargeRange():
    h = _hypr(1.0, 1.0)
    conv = Convert_HyperbolaToBSplineCurve(h, -2.0, 2.0)
    assert conv.IsPeriodic() is False
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    _check_ends(conv, h, -2.0, 2.0)
    _check_weights_and_knots(conv)


def test_Convert_HyperbolaToBSplineCurveTest_WeightsArePositive():
    conv = Convert_HyperbolaToBSplineCurve(_hypr(3.0, 2.0), -1.0, 1.0)
    weights = conv.Weights()
    for i in range(1, conv.NbPoles() + 1):
        assert weights[i] > 0.0
