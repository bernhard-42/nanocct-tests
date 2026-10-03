# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_Line_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Line
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()
ANG = Precision.Angular_s()


def test_Geom_LineTest_ConstructFromAx1():
    line = Geom_Line(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    assert line is not None
    assert line.Lin().Location().IsEqual(gp_Pnt(0.0, 0.0, 0.0), TOL)


def test_Geom_LineTest_ConstructFromPointAndDir():
    line = Geom_Line(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0))
    assert line.Lin().Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), TOL)
    assert line.Lin().Direction().IsEqual(gp_Dir(0.0, 0.0, 1.0), ANG)


def test_Geom_LineTest_D0Evaluation():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    p = gp_Pnt()
    line.D0(5.0, p)
    assert abs(p.X() - 5.0) <= TOL and abs(p.Y()) <= TOL and abs(p.Z()) <= TOL


def test_Geom_LineTest_D1Evaluation():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
    p, v1 = gp_Pnt(), gp_Vec()
    line.D1(3.0, p, v1)
    assert abs(p.Y() - 3.0) <= TOL
    assert abs(v1.X()) <= TOL and abs(v1.Y() - 1.0) <= TOL and abs(v1.Z()) <= TOL


def test_Geom_LineTest_D2Evaluation():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    line.D2(1.0, p, v1, v2)
    assert abs(v2.Magnitude()) <= TOL


def test_Geom_LineTest_InfiniteParameters():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert line.FirstParameter() == -Precision.Infinite_s()
    assert line.LastParameter() == Precision.Infinite_s()


def test_Geom_LineTest_Reverse():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    line.Reverse()
    assert line.Lin().Direction().IsEqual(gp_Dir(-1.0, 0.0, 0.0), ANG)


def test_Geom_LineTest_Reversed():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    rev = line.Reversed()
    assert rev is not None
    assert isinstance(rev, Geom_Line)
    assert rev.Lin().Direction().IsEqual(gp_Dir(-1.0, 0.0, 0.0), ANG)


def test_Geom_LineTest_Transform():
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0.0, 0.0, 5.0))
    line.Transform(t)
    assert abs(line.Lin().Location().Z() - 5.0) <= TOL


def test_Geom_LineTest_Copy():
    line = Geom_Line(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0))
    cp = line.Copy()
    assert cp is not None
    assert isinstance(cp, Geom_Line)
    assert cp.Lin().Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), TOL)
