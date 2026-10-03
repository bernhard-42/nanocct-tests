# Translated from OCCT src/ModelingData/TKGeomBase/GTests/gce_MakeHypr_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gce import (gce_ColinearPoints, gce_ConfusedPoints, gce_Done, gce_MakeHypr, gce_MakeHypr2d,
                         gce_NegativeRadius)
from nanocct.gp import gp, gp_Ax2, gp_Ax2d, gp_Ax22d, gp_Pnt, gp_Pnt2d
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _ok(m, major=None, minor=None):
    assert m.IsDone()
    assert m.Status() == gce_Done
    if major is not None:
        h = m.Value()
        assert abs(h.MajorRadius() - major) <= CONF
        assert abs(h.MinorRadius() - minor) <= CONF


def _bad(m, status):
    assert not m.IsDone()
    assert m.Status() == status


def test_gce_MakeHyprTest_FromAxis_ValidRadii_Done():
    _ok(gce_MakeHypr(gp_Ax2(), 10.0, 5.0), 10.0, 5.0)


def test_gce_MakeHyprTest_FromAxis_MajorLessThanMinor_Done():
    _ok(gce_MakeHypr(gp_Ax2(), 3.0, 7.0), 3.0, 7.0)


def test_gce_MakeHyprTest_FromAxis_EqualRadii_Done():
    _ok(gce_MakeHypr(gp_Ax2(), 5.0, 5.0))


def test_gce_MakeHyprTest_FromAxis_ZeroRadii_Done():
    _ok(gce_MakeHypr(gp_Ax2(), 0.0, 0.0))


def test_gce_MakeHyprTest_FromAxis_NegativeMajor_NegativeRadius():
    _bad(gce_MakeHypr(gp_Ax2(), -1.0, 5.0), gce_NegativeRadius)


def test_gce_MakeHyprTest_FromAxis_NegativeMinor_NegativeRadius():
    _bad(gce_MakeHypr(gp_Ax2(), 5.0, -1.0), gce_NegativeRadius)


def test_gce_MakeHyprTest_FromAxis_BothNegative_NegativeRadius():
    _bad(gce_MakeHypr(gp_Ax2(), -3.0, -2.0), gce_NegativeRadius)


def test_gce_MakeHyprTest_FromPoints_Valid_Done():
    _ok(gce_MakeHypr(gp_Pnt(10, 0, 0), gp_Pnt(0, 5, 0), gp_Pnt(0, 0, 0)), 10.0, 5.0)


def test_gce_MakeHyprTest_FromPoints_MajorLessThanMinor_Done():
    _ok(gce_MakeHypr(gp_Pnt(3, 0, 0), gp_Pnt(0, 7, 0), gp_Pnt(0, 0, 0)), 3.0, 7.0)


def test_gce_MakeHyprTest_FromPoints_ConfusedS1Center_ConfusedPoints():
    _bad(gce_MakeHypr(gp_Pnt(1, 2, 3), gp_Pnt(4, 5, 6), gp_Pnt(1, 2, 3)), gce_ConfusedPoints)


def test_gce_MakeHyprTest_FromPoints_ConfusedS2Center_ConfusedPoints():
    _bad(gce_MakeHypr(gp_Pnt(4, 5, 6), gp_Pnt(1, 2, 3), gp_Pnt(1, 2, 3)), gce_ConfusedPoints)


def test_gce_MakeHyprTest_FromPoints_ConfusedS1S2_ConfusedPoints():
    _bad(gce_MakeHypr(gp_Pnt(5, 5, 5), gp_Pnt(5, 5, 5), gp_Pnt(0, 0, 0)), gce_ConfusedPoints)


def test_gce_MakeHyprTest_FromPoints_Collinear_ColinearPoints():
    _bad(gce_MakeHypr(gp_Pnt(10, 0, 0), gp_Pnt(5, 0, 0), gp_Pnt(0, 0, 0)), gce_ColinearPoints)


def test_gce_MakeHyprTest_FromPoints_TinyScale_ConfusedPoints():
    r = gp.Resolution_s()
    _bad(gce_MakeHypr(gp_Pnt(2.0 * r, 0, 0), gp_Pnt(0, 1.1 * r, 0), gp_Pnt(0, 0, 0)), gce_ConfusedPoints)


def test_gce_MakeHypr2dTest_FromMajorAxis_ValidRadii_Done():
    _ok(gce_MakeHypr2d(gp_Ax2d(), 10.0, 5.0, True), 10.0, 5.0)


def test_gce_MakeHypr2dTest_FromMajorAxis_MajorLessThanMinor_Done():
    _ok(gce_MakeHypr2d(gp_Ax2d(), 3.0, 7.0, True), 3.0, 7.0)


def test_gce_MakeHypr2dTest_FromMajorAxis_NegativeRadius_NegativeRadius():
    _bad(gce_MakeHypr2d(gp_Ax2d(), -1.0, 5.0, True), gce_NegativeRadius)


def test_gce_MakeHypr2dTest_FromAx22d_ValidRadii_Done():
    _ok(gce_MakeHypr2d(gp_Ax22d(), 8.0, 4.0))


def test_gce_MakeHypr2dTest_FromAx22d_NegativeRadius_NegativeRadius():
    _bad(gce_MakeHypr2d(gp_Ax22d(), 5.0, -2.0), gce_NegativeRadius)


def test_gce_MakeHypr2dTest_FromPoints_Valid_Done():
    _ok(gce_MakeHypr2d(gp_Pnt2d(10, 0), gp_Pnt2d(0, 5), gp_Pnt2d(0, 0)), 10.0, 5.0)


def test_gce_MakeHypr2dTest_FromPoints_MajorLessThanMinor_Done():
    _ok(gce_MakeHypr2d(gp_Pnt2d(3, 0), gp_Pnt2d(0, 7), gp_Pnt2d(0, 0)), 3.0, 7.0)


def test_gce_MakeHypr2dTest_FromPoints_ConfusedS1Center_ConfusedPoints():
    _bad(gce_MakeHypr2d(gp_Pnt2d(1, 2), gp_Pnt2d(4, 5), gp_Pnt2d(1, 2)), gce_ConfusedPoints)


def test_gce_MakeHypr2dTest_FromPoints_ConfusedS2Center_ConfusedPoints():
    _bad(gce_MakeHypr2d(gp_Pnt2d(4, 5), gp_Pnt2d(1, 2), gp_Pnt2d(1, 2)), gce_ConfusedPoints)


def test_gce_MakeHypr2dTest_FromPoints_Collinear_ColinearPoints():
    _bad(gce_MakeHypr2d(gp_Pnt2d(10, 0), gp_Pnt2d(5, 0), gp_Pnt2d(0, 0)), gce_ColinearPoints)
