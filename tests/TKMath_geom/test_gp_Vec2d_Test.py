# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Vec2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Dir2d, gp_Pnt2d, gp_Vec2d
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def c2(v):
    return (v.X(), v.Y())


def near(a, b, t=CONF):
    return abs(a - b) <= t


def test_gp_Vec2dTest_DefaultConstructor():
    assert c2(gp_Vec2d()) == (0.0, 0.0)


def test_gp_Vec2dTest_CoordinateConstructor():
    assert c2(gp_Vec2d(1.0, 2.0)) == (1.0, 2.0)


def test_gp_Vec2dTest_TwoPointConstructor():
    assert c2(gp_Vec2d(gp_Pnt2d(1.0, 2.0), gp_Pnt2d(4.0, 6.0))) == (3.0, 4.0)


def test_gp_Vec2dTest_Dir2dConstructor():
    v = gp_Vec2d(gp_Dir2d(0.0, 1.0))
    assert near(v.Magnitude(), 1.0) and near(v.Y(), 1.0)


def test_gp_Vec2dTest_AddSubtract():
    v1, v2 = gp_Vec2d(1.0, 2.0), gp_Vec2d(4.0, 5.0)
    assert c2(v1 + v2) == (5.0, 7.0)
    assert c2(v2 - v1) == (3.0, 3.0)


def test_gp_Vec2dTest_MultiplyDivide():
    v = gp_Vec2d(2.0, 4.0)
    assert c2(v * 3.0) == (6.0, 12.0)
    assert c2(v / 2.0) == (1.0, 2.0)


def test_gp_Vec2dTest_Dot():
    assert gp_Vec2d(1.0, 0.0).Dot(gp_Vec2d(0.0, 1.0)) == 0.0
    assert gp_Vec2d(1.0, 2.0).Dot(gp_Vec2d(4.0, 5.0)) == 14.0


def test_gp_Vec2dTest_Crossed():
    assert near(gp_Vec2d(1.0, 0.0).Crossed(gp_Vec2d(0.0, 1.0)), 1.0)
    assert near(gp_Vec2d(3.0, 4.0).Crossed(gp_Vec2d(2.0, 5.0)), 7.0)


def test_gp_Vec2dTest_Magnitude():
    v = gp_Vec2d(3.0, 4.0)
    assert near(v.Magnitude(), 5.0) and near(v.SquareMagnitude(), 25.0)


def test_gp_Vec2dTest_Normalize():
    n = gp_Vec2d(3.0, 4.0).Normalized()
    assert near(n.Magnitude(), 1.0) and near(n.X(), 0.6) and near(n.Y(), 0.8)


def test_gp_Vec2dTest_Angle():
    assert near(gp_Vec2d(1.0, 0.0).Angle(gp_Vec2d(0.0, 1.0)), math.pi / 2, ANG)


def test_gp_Vec2dTest_IsParallel():
    assert gp_Vec2d(1.0, 0.0).IsParallel(gp_Vec2d(5.0, 0.0), ANG)


def test_gp_Vec2dTest_IsNormal():
    assert gp_Vec2d(1.0, 0.0).IsNormal(gp_Vec2d(0.0, 1.0), ANG)


def test_gp_Vec2dTest_IsOpposite():
    assert gp_Vec2d(1.0, 0.0).IsOpposite(gp_Vec2d(-3.0, 0.0), ANG)


def test_gp_Vec2dTest_Reverse():
    assert c2(gp_Vec2d(1.0, 2.0).Reversed()) == (-1.0, -2.0)


def test_gp_Vec2dTest_SetLinearForm():
    r = gp_Vec2d()
    r.SetLinearForm(2.0, gp_Vec2d(1.0, 0.0), 3.0, gp_Vec2d(0.0, 1.0))
    assert near(r.X(), 2.0) and near(r.Y(), 3.0)


def test_gp_Vec2dTest_OCC26750_IsNormal_NegativeAngle():
    assert gp_Vec2d(1.0, 0.0).IsNormal(gp_Vec2d(0.0, -1.0), ANG)
    assert gp_Dir2d(gp_Dir2d.D.X).IsNormal(gp_Dir2d(gp_Dir2d.D.NY), ANG)
