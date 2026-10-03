# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_ConeToBSplineSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BSplSLib import BSplSLib
from nanocct.Convert import Convert_ConeToBSplineSurface
from nanocct.gp import gp_Ax3, gp_Cone, gp_Dir, gp_Pnt


def _ax3():
    return gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))


def _check_weights_positive(conv, strict=True):
    weights = conv.Weights()
    for i in range(1, conv.NbUPoles() + 1):
        for j in range(1, conv.NbVPoles() + 1):
            if strict:
                assert weights[i, j] > 0.0
            else:
                assert weights[i, j] >= 0.0


def _check_knots_monotonic(conv):
    uk = conv.UKnots()
    for i in range(2, conv.NbUKnots() + 1):
        assert uk[i] > uk[i - 1]
    vk = conv.VKnots()
    for i in range(2, conv.NbVKnots() + 1):
        assert vk[i] > vk[i - 1]


def _sample(conv, urat, vrat):
    # BSplSLib::D0 on a 5x5 grid over the knot range, as in the OCCT test
    uk = conv.UKnots()
    vk = conv.VKnots()
    umin, umax = uk[uk.Lower()], uk[uk.Upper()]
    vmin, vmax = vk[vk.Lower()], vk[vk.Upper()]
    for i in range(5):
        u = umin + i * (umax - umin) / 4.0
        for j in range(5):
            v = vmin + j * (vmax - vmin) / 4.0
            pnt = gp_Pnt()
            BSplSLib.D0_s(u, v, 0, 0, conv.Poles(), conv.Weights(), conv.UKnots(), conv.VKnots(),
                          conv.UMultiplicities(), conv.VMultiplicities(), conv.UDegree(), conv.VDegree(),
                          urat, vrat, False, False, pnt)
            yield pnt


def test_Convert_ConeToBSplineSurfaceTest_FullCone():
    conv = Convert_ConeToBSplineSurface(gp_Cone(_ax3(), math.pi / 6.0, 3.0), 0.0, 10.0)
    assert conv.UDegree() == 2
    assert conv.VDegree() == 1
    assert conv.IsUPeriodic() is True
    assert conv.IsVPeriodic() is False
    assert conv.NbUPoles() > 0
    assert conv.NbVPoles() > 0


def test_Convert_ConeToBSplineSurfaceTest_TrimmedCone():
    conv = Convert_ConeToBSplineSurface(gp_Cone(_ax3(), math.pi / 4.0, 2.0), 0.0, math.pi, 0.0, 5.0)
    assert conv.IsUPeriodic() is False
    assert conv.IsVPeriodic() is False


def test_Convert_ConeToBSplineSurfaceTest_WeightsArePositive():
    conv = Convert_ConeToBSplineSurface(gp_Cone(_ax3(), math.pi / 6.0, 1.0), 0.0, 5.0)
    _check_weights_positive(conv)


def test_Convert_ConeToBSplineSurfaceTest_GeometricVerification():
    semi, radius = math.pi / 6.0, 3.0
    conv = Convert_ConeToBSplineSurface(gp_Cone(_ax3(), semi, radius), 0.0, math.pi, 0.0, 10.0)
    for p in _sample(conv, True, False):
        dist = math.sqrt(p.X() * p.X() + p.Y() * p.Y())
        assert abs(dist - (radius + p.Z() * math.tan(semi))) <= 1.0e-10
