# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntSurf_LineOn2S_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.IntSurf import IntSurf_LineOn2S, IntSurf_PntOn2S


def _point(p, u1, v1, u2, v2):
    pnt = IntSurf_PntOn2S()
    pnt.SetValue(p, u1, v1, u2, v2)
    return pnt


def test_IntSurf_LineOn2S_Test_EmptyLineBoxesAreNotOut():
    line = IntSurf_LineOn2S()
    assert not line.IsOutBox(gp_Pnt(10.0, 10.0, 10.0))
    assert not line.IsOutSurf1Box(gp_Pnt2d(10.0, 10.0))
    assert not line.IsOutSurf2Box(gp_Pnt2d(10.0, 10.0))


def test_IntSurf_LineOn2S_Test_PointReplacementInvalidatesCachedBoxes():
    line = IntSurf_LineOn2S()
    line.Add(_point(gp_Pnt(0.0, 0.0, 0.0), 0.0, 0.0, 0.0, 0.0))
    line.Add(_point(gp_Pnt(1.0, 1.0, 1.0), 1.0, 1.0, 1.0, 1.0))
    assert line.IsOutBox(gp_Pnt(100.0, 100.0, 100.0))
    assert line.IsOutSurf1Box(gp_Pnt2d(50.0, 50.0))

    line.SetPoint(2, gp_Pnt(100.0, 100.0, 100.0))
    assert not line.IsOutBox(gp_Pnt(100.0, 100.0, 100.0))

    line.Value(2, _point(gp_Pnt(100.0, 100.0, 100.0), 50.0, 50.0, 60.0, 60.0))
    assert not line.IsOutSurf1Box(gp_Pnt2d(50.0, 50.0))
    assert not line.IsOutSurf2Box(gp_Pnt2d(60.0, 60.0))


def test_IntSurf_LineOn2S_Test_Split_DividesCorrectly():
    line = IntSurf_LineOn2S()
    for i in range(4):
        line.Add(_point(gp_Pnt(i, 0, 0), i, 0, i, 0))
    split = line.Split(2)
    assert line.NbPoints() == 1
    assert split.NbPoints() == 3
    assert abs(line.Value(1).Value().X() - 0.0) <= 1e-15
    assert abs(split.Value(1).Value().X() - 1.0) <= 1e-15
