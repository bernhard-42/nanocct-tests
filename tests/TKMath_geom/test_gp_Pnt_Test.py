# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Pnt_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_XYZ
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def xyz(p, x, y, z, t=CONF):
    return abs(p.X() - x) <= t and abs(p.Y() - y) <= t and abs(p.Z() - z) <= t


def test_gp_PntTest_DefaultConstructor():
    p = gp_Pnt()
    assert (p.X(), p.Y(), p.Z()) == (0.0, 0.0, 0.0)


def test_gp_PntTest_CoordinateConstructor():
    p = gp_Pnt(1.0, 2.0, 3.0)
    assert (p.X(), p.Y(), p.Z()) == (1.0, 2.0, 3.0)


def test_gp_PntTest_XYZConstructor():
    p = gp_Pnt(gp_XYZ(4.0, 5.0, 6.0))
    assert (p.X(), p.Y(), p.Z()) == (4.0, 5.0, 6.0)


def test_gp_PntTest_SetCoord():
    p = gp_Pnt()
    p.SetX(10.0)
    p.SetY(20.0)
    p.SetZ(30.0)
    assert (p.X(), p.Y(), p.Z()) == (10.0, 20.0, 30.0)
    p.SetCoord(7.0, 8.0, 9.0)
    assert (p.X(), p.Y(), p.Z()) == (7.0, 8.0, 9.0)


def test_gp_PntTest_Distance():
    assert abs(gp_Pnt(0.0, 0.0, 0.0).Distance(gp_Pnt(3.0, 4.0, 0.0)) - 5.0) <= CONF


def test_gp_PntTest_SquareDistance():
    assert abs(gp_Pnt(1.0, 2.0, 3.0).SquareDistance(gp_Pnt(4.0, 6.0, 3.0)) - 25.0) <= CONF


def test_gp_PntTest_IsEqual():
    p1 = gp_Pnt(1.0, 2.0, 3.0)
    assert p1.IsEqual(gp_Pnt(1.0, 2.0, 3.0), CONF)
    assert not p1.IsEqual(gp_Pnt(1.0, 2.0, 4.0), CONF)


def test_gp_PntTest_BaryCenter():
    p1 = gp_Pnt(0.0, 0.0, 0.0)
    p1.BaryCenter(1.0, gp_Pnt(10.0, 0.0, 0.0), 1.0)
    assert xyz(p1, 5.0, 0.0, 0.0)


def test_gp_PntTest_Translate_ByVec():
    assert xyz(gp_Pnt(1.0, 2.0, 3.0).Translated(gp_Vec(10.0, 20.0, 30.0)), 11.0, 22.0, 33.0)


def test_gp_PntTest_Translate_ByTwoPoints():
    r = gp_Pnt(1.0, 2.0, 3.0).Translated(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(5.0, 5.0, 5.0))
    assert xyz(r, 6.0, 7.0, 8.0)


def test_gp_PntTest_Scale():
    assert xyz(gp_Pnt(2.0, 4.0, 6.0).Scaled(gp_Pnt(0.0, 0.0, 0.0), 2.0), 4.0, 8.0, 12.0)


def test_gp_PntTest_Rotate():
    r = gp_Pnt(1.0, 0.0, 0.0).Rotated(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2)
    assert xyz(r, 0.0, 1.0, 0.0)


def test_gp_PntTest_Mirror_Point():
    assert xyz(gp_Pnt(1.0, 0.0, 0.0).Mirrored(gp_Pnt(0.0, 0.0, 0.0)), -1.0, 0.0, 0.0)


def test_gp_PntTest_Mirror_Axis():
    r = gp_Pnt(1.0, 1.0, 0.0).Mirrored(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    assert xyz(r, 1.0, -1.0, 0.0)


def test_gp_PntTest_Mirror_Plane():
    r = gp_Pnt(1.0, 2.0, 3.0).Mirrored(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    assert xyz(r, 1.0, 2.0, -3.0)


def test_gp_PntTest_Transformed():
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0.0, 0.0, 5.0))
    assert xyz(gp_Pnt(1.0, 0.0, 0.0).Transformed(t), 1.0, 0.0, 5.0)
