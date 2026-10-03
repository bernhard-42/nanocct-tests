# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Pnt2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d, gp_XY
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def xy(p, x, y, t=CONF):
    return abs(p.X() - x) <= t and abs(p.Y() - y) <= t


def test_gp_Pnt2dTest_DefaultConstructor():
    p = gp_Pnt2d()
    assert (p.X(), p.Y()) == (0.0, 0.0)


def test_gp_Pnt2dTest_CoordinateConstructor():
    p = gp_Pnt2d(1.0, 2.0)
    assert (p.X(), p.Y()) == (1.0, 2.0)


def test_gp_Pnt2dTest_XYConstructor():
    p = gp_Pnt2d(gp_XY(3.0, 4.0))
    assert (p.X(), p.Y()) == (3.0, 4.0)


def test_gp_Pnt2dTest_SetCoord():
    p = gp_Pnt2d()
    p.SetX(10.0)
    p.SetY(20.0)
    assert (p.X(), p.Y()) == (10.0, 20.0)
    p.SetCoord(7.0, 8.0)
    assert (p.X(), p.Y()) == (7.0, 8.0)


def test_gp_Pnt2dTest_Distance():
    assert abs(gp_Pnt2d(0.0, 0.0).Distance(gp_Pnt2d(3.0, 4.0)) - 5.0) <= CONF


def test_gp_Pnt2dTest_SquareDistance():
    assert abs(gp_Pnt2d(1.0, 2.0).SquareDistance(gp_Pnt2d(4.0, 6.0)) - 25.0) <= CONF


def test_gp_Pnt2dTest_IsEqual():
    p1 = gp_Pnt2d(1.0, 2.0)
    assert p1.IsEqual(gp_Pnt2d(1.0, 2.0), CONF)
    assert not p1.IsEqual(gp_Pnt2d(1.0, 3.0), CONF)


def test_gp_Pnt2dTest_Translate_ByVec2d():
    assert xy(gp_Pnt2d(1.0, 2.0).Translated(gp_Vec2d(10.0, 20.0)), 11.0, 22.0)


def test_gp_Pnt2dTest_Scale():
    assert xy(gp_Pnt2d(2.0, 4.0).Scaled(gp_Pnt2d(0.0, 0.0), 2.0), 4.0, 8.0)


def test_gp_Pnt2dTest_Rotate():
    assert xy(gp_Pnt2d(1.0, 0.0).Rotated(gp_Pnt2d(0.0, 0.0), math.pi / 2), 0.0, 1.0)


def test_gp_Pnt2dTest_Mirror_Point():
    assert xy(gp_Pnt2d(1.0, 0.0).Mirrored(gp_Pnt2d(0.0, 0.0)), -1.0, 0.0)


def test_gp_Pnt2dTest_Mirror_Axis():
    r = gp_Pnt2d(1.0, 1.0).Mirrored(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)))
    assert xy(r, 1.0, -1.0)


def test_gp_Pnt2dTest_Transformed():
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(0.0, 5.0))
    assert xy(gp_Pnt2d(1.0, 0.0).Transformed(t), 1.0, 5.0)


def test_gp_Pnt2dTest_OCC22736_TwoIdenticalMirrorCompositionIsIdentity():
    f, s = gp_Pnt2d(2.0, 1.0), gp_Pnt2d(3.0, 1.0)
    axis = gp_Ax2d(f, gp_Dir2d(gp_Vec2d(f, s)))
    p1, p2 = gp_Pnt2d(1.0, 0.0), gp_Pnt2d(1.0, 2.0)
    m1, m2 = gp_Trsf2d(), gp_Trsf2d()
    m1.SetMirror(axis)
    m2.SetMirror(axis)
    r1 = p1.Transformed(m1)
    assert xy(r1, p2.X(), p2.Y())
    r2 = r1.Transformed(m2)
    assert xy(r2, p1.X(), p1.Y())
    assert xy(p1.Transformed(m2.Multiplied(m1)), p1.X(), p1.Y())
