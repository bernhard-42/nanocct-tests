# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakeArcOfCircle_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakeArcOfCircle
from nanocct.gce import gce_Done
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.Precision import Precision


def test_GC_MakeArcOfCircleTest_FromPointsAndTangent_Done():
    m = GC_MakeArcOfCircle(gp_Pnt(1.0, 0.0, 0.0), gp_Vec(0.0, 1.0, 0.0), gp_Pnt(0.0, 1.0, 0.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value() is not None


def test_GC_MakeArcOfCircleTest_FromThreePoints_Done():
    m = GC_MakeArcOfCircle(gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(0.0, 1.0, 0.0), gp_Pnt(-1.0, 0.0, 0.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value() is not None


def test_GC_MakeArcOfCircleTest_FromPointsAndTangent_ConfusionScale_Done():
    s = 2.0 * Precision.Confusion_s()
    p1 = gp_Pnt(s, 0.0, 0.0)
    m = GC_MakeArcOfCircle(p1, gp_Vec(0.0, 1.0, 0.0), gp_Pnt(0.0, s, 0.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value() is not None
    assert m.Value().StartPoint().IsEqual(p1, Precision.Confusion_s())
