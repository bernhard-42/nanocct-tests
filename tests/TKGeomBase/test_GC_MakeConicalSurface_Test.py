# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakeConicalSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GC import GC_MakeConicalSurface
from nanocct.gce import gce_BadAngle, gce_Done
from nanocct.gp import gp, gp_Ax2, gp_Dir, gp_Pnt


def test_GC_MakeConicalSurfaceTest_FromAxis_AngleBelowResolution_BadAngle():
    m = GC_MakeConicalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 0.5 * gp.Resolution_s(), 2.0)
    assert not m.IsDone()
    assert m.Status() == gce_BadAngle


def test_GC_MakeConicalSurfaceTest_FromAxis_ValidAngle_Done():
    m = GC_MakeConicalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 6.0, 2.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
