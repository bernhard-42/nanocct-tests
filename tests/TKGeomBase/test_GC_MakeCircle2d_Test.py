# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakeCircle2d_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakeCircle2d
from nanocct.gce import gce_Done
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _base():
    return gp_Circ2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 5.0)


def test_GC_MakeCircle2dTest_FromCircAndPoint_Done():
    m = GC_MakeCircle2d(_base(), gp_Pnt2d(0.0, 10.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert abs(m.Value().Circ2d().Radius() - 10.0) <= TOL


def test_GC_MakeCircle2dTest_FromCircAndDist_Done():
    m = GC_MakeCircle2d(_base(), -2.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert abs(m.Value().Circ2d().Radius() - 3.0) <= TOL


def test_GC_MakeCircle2dTest_FromCircAndPoint_AtCenter_DoneZeroRadius():
    m = GC_MakeCircle2d(_base(), gp_Pnt2d(0.0, 0.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert m.Value() is not None
    assert abs(m.Value().Circ2d().Radius()) <= TOL
