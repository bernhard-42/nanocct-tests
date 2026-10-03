# Translated from OCCT src/ModelingData/TKGeomBase/GTests/gce_MakeCirc2d_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gce import gce_Done, gce_MakeCirc2d
from nanocct.gp import gp, gp_Pnt2d
from nanocct.Precision import Precision


def test_gce_MakeCirc2dTest_ThreePoints_AllCoincidentWithinResolution_DoneZeroRadius():
    d = 0.25 * gp.Resolution_s()
    m = gce_MakeCirc2d(gp_Pnt2d(0, 0), gp_Pnt2d(d, 0), gp_Pnt2d(0, d))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert abs(m.Value().Radius()) <= Precision.Confusion_s()


def test_gce_MakeCirc2dTest_ThreePoints_OneNearCoincidentPair_Done():
    m = gce_MakeCirc2d(gp_Pnt2d(0, 0), gp_Pnt2d(1.0e-150, 0), gp_Pnt2d(0, 1))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value().Radius() > 0.0


def test_gce_MakeCirc2dTest_ThreePoints_SmallDistinct_Done():
    m = gce_MakeCirc2d(gp_Pnt2d(0, 0), gp_Pnt2d(2.0e-150, 0), gp_Pnt2d(0, 1))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value().Radius() > 0.0
