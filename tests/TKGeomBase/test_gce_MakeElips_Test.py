# Translated from OCCT src/ModelingData/TKGeomBase/GTests/gce_MakeElips_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gce import gce_Done, gce_InvertAxis, gce_MakeElips, gce_NullAxis
from nanocct.gp import gp, gp_Pnt
from nanocct.Precision import Precision


def test_gce_MakeElipsTest_FromPoints_Valid_Done():
    m = gce_MakeElips(gp_Pnt(10, 0, 0), gp_Pnt(0, 5, 0), gp_Pnt(0, 0, 0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    e = m.Value()
    assert abs(e.MajorRadius() - 10.0) <= Precision.Confusion_s()
    assert abs(e.MinorRadius() - 5.0) <= Precision.Confusion_s()


def test_gce_MakeElipsTest_FromPoints_Collinear_InvertAxis():
    m = gce_MakeElips(gp_Pnt(10, 0, 0), gp_Pnt(5, 0, 0), gp_Pnt(0, 0, 0))
    assert not m.IsDone()
    assert m.Status() == gce_InvertAxis


def test_gce_MakeElipsTest_FromPoints_TinyScale_NullAxis():
    r = gp.Resolution_s()
    m = gce_MakeElips(gp_Pnt(2.0 * r, 0, 0), gp_Pnt(0, 1.1 * r, 0), gp_Pnt(0, 0, 0))
    assert not m.IsDone()
    assert m.Status() == gce_NullAxis
