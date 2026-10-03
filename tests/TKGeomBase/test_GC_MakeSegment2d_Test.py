# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakeSegment2d_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakeSegment2d
from nanocct.gce import gce_ConfusedPoints, gce_Done
from nanocct.gp import gp, gp_Dir2d, gp_Pnt2d

RES = gp.Resolution_s()


def test_GC_MakeSegment2dTest_FromPoints_BelowResolution_ConfusedPoints():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Pnt2d(0.5 * RES, 0.0))
    assert not m.IsDone()
    assert m.Status() == gce_ConfusedPoints


def test_GC_MakeSegment2dTest_FromPoints_AboveResolution_Done():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Pnt2d(1.0e-150, 0.0))
    assert m.IsDone()
    assert m.Status() == gce_Done


def test_GC_MakeSegment2dTest_FromPoints_AtResolution_ConfusedPoints():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Pnt2d(RES, 0.0))
    assert not m.IsDone()
    assert m.Status() == gce_ConfusedPoints


def test_GC_MakeSegment2dTest_FromPointDir_BelowResolutionParameter_ConfusedPoints():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0), gp_Pnt2d(0.5 * RES, 3.0))
    assert not m.IsDone()
    assert m.Status() == gce_ConfusedPoints


def test_GC_MakeSegment2dTest_FromPointDir_AboveResolutionParameter_Done():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0), gp_Pnt2d(2.0 * RES, 3.0))
    assert m.IsDone()
    assert m.Status() == gce_Done


def test_GC_MakeSegment2dTest_FromPointDir_AtResolutionParameter_ConfusedPoints():
    m = GC_MakeSegment2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0), gp_Pnt2d(RES, 5.0))
    assert not m.IsDone()
    assert m.Status() == gce_ConfusedPoints
