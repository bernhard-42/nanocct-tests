# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_CylinderToBSplineSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BSplSLib import BSplSLib
from nanocct.Convert import Convert_CylinderToBSplineSurface
from nanocct.gp import gp_Ax3, gp_Cylinder, gp_Dir, gp_Pnt


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


def test_Convert_CylinderToBSplineSurfaceTest_FullCylinder():
    conv = Convert_CylinderToBSplineSurface(gp_Cylinder(_ax3(), 3.0), 0.0, 10.0)
    assert conv.UDegree() == 2
    assert conv.VDegree() == 1
    assert conv.IsUPeriodic() is True
    assert conv.IsVPeriodic() is False
    assert conv.NbUPoles() > 0
    assert conv.NbVPoles() > 0


def test_Convert_CylinderToBSplineSurfaceTest_TrimmedCylinder():
    conv = Convert_CylinderToBSplineSurface(gp_Cylinder(_ax3(), 2.0), 0.0, math.pi, -5.0, 5.0)
    assert conv.IsUPeriodic() is False
    assert conv.IsVPeriodic() is False
    assert conv.NbUPoles() > 0
    assert conv.NbVPoles() > 0


def test_Convert_CylinderToBSplineSurfaceTest_WeightsArePositive():
    conv = Convert_CylinderToBSplineSurface(gp_Cylinder(_ax3(), 1.0), 0.0, 1.0)
    _check_weights_positive(conv)


def test_Convert_CylinderToBSplineSurfaceTest_KnotsAreMonotonic():
    conv = Convert_CylinderToBSplineSurface(gp_Cylinder(_ax3(), 1.0), 0.0, 1.0)
    _check_knots_monotonic(conv)


def test_Convert_CylinderToBSplineSurfaceTest_GeometricVerification():
    radius, v1, v2, tol = 3.0, -5.0, 5.0, 1.0e-10
    conv = Convert_CylinderToBSplineSurface(gp_Cylinder(_ax3(), radius), 0.0, math.pi, v1, v2)
    for p in _sample(conv, True, False):
        assert abs(math.sqrt(p.X() * p.X() + p.Y() * p.Y()) - radius) <= tol
        assert p.Z() >= v1 - tol
        assert p.Z() <= v2 + tol
