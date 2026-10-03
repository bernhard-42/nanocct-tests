# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_ParabolaToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BSplCLib import BSplCLib
from nanocct.Convert import Convert_ParabolaToBSplineCurve
from nanocct.ElCLib import ElCLib
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Parab2d, gp_Pnt2d


def _parab(focal):
    return gp_Parab2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), focal)


def _check_point(conv, parab, param):
    pnt = gp_Pnt2d()
    BSplCLib.D0_s(param, 0, conv.Degree(), conv.IsPeriodic(), conv.Poles(), conv.Weights(), conv.Knots(),
                  conv.Multiplicities(), pnt)
    exp = ElCLib.Value_s(param, parab)
    assert abs(pnt.X() - exp.X()) <= 1.0e-10
    assert abs(pnt.Y() - exp.Y()) <= 1.0e-10


def test_Convert_ParabolaToBSplineCurveTest_BasicConversion():
    parab = _parab(1.0)
    u1, u2 = -2.0, 2.0
    conv = Convert_ParabolaToBSplineCurve(parab, u1, u2)
    assert conv.IsPeriodic() is False
    assert conv.Degree() == 2
    assert conv.NbPoles() > 0
    assert conv.NbKnots() > 0
    for i in range(5):
        _check_point(conv, parab, u1 + i * (u2 - u1) / 4.0)


def test_Convert_ParabolaToBSplineCurveTest_SmallRange():
    parab = _parab(0.5)
    u1, u2 = -0.5, 0.5
    conv = Convert_ParabolaToBSplineCurve(parab, u1, u2)
    for i in range(5):
        _check_point(conv, parab, u1 + i * (u2 - u1) / 4.0)


def test_Convert_ParabolaToBSplineCurveTest_AllWeightsAreOne():
    conv = Convert_ParabolaToBSplineCurve(_parab(1.0), -1.0, 1.0)
    weights = conv.Weights()
    for i in range(weights.Lower(), weights.Upper() + 1):
        assert abs(weights[i] - 1.0) <= 1.0e-15
