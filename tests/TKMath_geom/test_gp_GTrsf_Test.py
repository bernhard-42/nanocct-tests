# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_GTrsf_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Ax2, gp_Dir, gp_GTrsf, gp_Pnt, gp_XYZ
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _affinity(ratio):
    pln = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, -1.0, 0.0))
    trf = gp_GTrsf()
    trf.SetAffinity(pln, ratio)
    res = gp_XYZ(1.0, 0.0, 0.0)
    trf.Transforms(res)
    return res


def test_gp_GTrsfTest_OCC13963_SetAffinity_Ratio1_IsIdentity():
    r = _affinity(1.0)
    assert abs(r.X() - 1.0) <= TOL
    assert abs(r.Y() - 0.0) <= TOL
    assert abs(r.Z() - 0.0) <= TOL


def test_gp_GTrsfTest_OCC13963_SetAffinity_Ratio2_ScalesAlongNormal():
    r = _affinity(2.0)
    assert abs(r.X() - 1.5) <= TOL
    assert abs(r.Y() + 0.5) <= TOL
    assert abs(r.Z() - 0.0) <= TOL
