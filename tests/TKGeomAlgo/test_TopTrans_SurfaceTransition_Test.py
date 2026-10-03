# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/TopTrans_SurfaceTransition_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Dir
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_UNKNOWN
from nanocct.TopTrans import TopTrans_SurfaceTransition


def test_TopTrans_SurfaceTransition_Test_UndefinedStateStaysInstanceLocal():
    ref = TopTrans_SurfaceTransition()
    ref.Reset(gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    ref.Compare(Precision.Angular_s(), gp_Dir(0.0, 0.0, 1.0), TopAbs_FORWARD, TopAbs_FORWARD)
    before = ref.StateBefore()
    after = ref.StateAfter()
    assert before != TopAbs_UNKNOWN
    assert after != TopAbs_UNKNOWN

    invalid = TopTrans_SurfaceTransition()
    invalid.Reset(gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0),
                  1.0, 1.0)
    assert invalid.StateBefore() == TopAbs_UNKNOWN
    assert invalid.StateAfter() == TopAbs_UNKNOWN
    assert ref.StateBefore() == before
    assert ref.StateAfter() == after


def test_TopTrans_SurfaceTransition_Test_CompareUsesProvidedTolerance():
    tr = TopTrans_SurfaceTransition()
    tr.Reset(gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    tr.Compare(1.0, gp_Dir(0.0, 0.0, 1.0), gp_Dir(0.6, 0.8, 0.0), gp_Dir(0.6, -0.8, 0.0), 1.0, 0.5,
               TopAbs_FORWARD, TopAbs_FORWARD)
    assert tr.StateBefore() != TopAbs_UNKNOWN
    assert tr.StateAfter() != TopAbs_UNKNOWN
