# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakePlane_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakePlane
from nanocct.gce import gce_Done
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pln, gp_Pnt
from nanocct.Precision import Precision


def test_GC_MakePlaneTest_FromPlaneAndDist_Done():
    m = GC_MakePlane(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert abs(m.Value().Pln().Location().Z() - 5.0) <= Precision.Confusion_s()


def test_GC_MakePlaneTest_FromPlaneAndPoint_Done():
    p = gp_Pnt(2.0, -3.0, 7.0)
    m = GC_MakePlane(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), p)
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value().Pln().Location().IsEqual(p, Precision.Confusion_s())


def test_GC_MakePlaneTest_FromAxis_Done():
    ax = gp_Ax1(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 1.0, 0.0))
    m = GC_MakePlane(ax)
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value().Pln().Axis().Direction().IsParallel(ax.Direction(), Precision.Angular_s())
