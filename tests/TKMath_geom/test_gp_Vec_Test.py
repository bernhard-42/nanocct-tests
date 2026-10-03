# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Vec_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Dir, gp_Pnt, gp_Vec
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def c3(v):
    return (v.X(), v.Y(), v.Z())


def near(a, b, t=CONF):
    return abs(a - b) <= t


def test_gp_VecTest_DefaultConstructor():
    assert c3(gp_Vec()) == (0.0, 0.0, 0.0)


def test_gp_VecTest_CoordinateConstructor():
    assert c3(gp_Vec(1.0, 2.0, 3.0)) == (1.0, 2.0, 3.0)


def test_gp_VecTest_TwoPointConstructor():
    assert c3(gp_Vec(gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 6.0, 8.0))) == (3.0, 4.0, 5.0)


def test_gp_VecTest_DirConstructor():
    v = gp_Vec(gp_Dir(0.0, 0.0, 1.0))
    assert near(v.Magnitude(), 1.0) and near(v.Z(), 1.0)


def test_gp_VecTest_AddSubtract():
    v1, v2 = gp_Vec(1.0, 2.0, 3.0), gp_Vec(4.0, 5.0, 6.0)
    assert c3(v1 + v2) == (5.0, 7.0, 9.0)
    assert c3(v2 - v1) == (3.0, 3.0, 3.0)


def test_gp_VecTest_MultiplyDivide():
    v = gp_Vec(2.0, 4.0, 6.0)
    assert c3(v * 3.0) == (6.0, 12.0, 18.0)
    assert c3(v / 2.0) == (1.0, 2.0, 3.0)


def test_gp_VecTest_Dot():
    assert gp_Vec(1.0, 0.0, 0.0).Dot(gp_Vec(0.0, 1.0, 0.0)) == 0.0
    assert gp_Vec(1.0, 2.0, 3.0).Dot(gp_Vec(4.0, 5.0, 6.0)) == 32.0


def test_gp_VecTest_Cross():
    c = gp_Vec(1.0, 0.0, 0.0).Crossed(gp_Vec(0.0, 1.0, 0.0))
    assert near(c.X(), 0.0) and near(c.Y(), 0.0) and near(c.Z(), 1.0)


def test_gp_VecTest_CrossMagnitude():
    assert near(gp_Vec(1.0, 0.0, 0.0).CrossMagnitude(gp_Vec(0.0, 1.0, 0.0)), 1.0)


def test_gp_VecTest_DotCross_TripleScalarProduct():
    r = gp_Vec(1.0, 0.0, 0.0).DotCross(gp_Vec(0.0, 1.0, 0.0), gp_Vec(0.0, 0.0, 1.0))
    assert near(r, 1.0)


def test_gp_VecTest_Magnitude():
    v = gp_Vec(3.0, 4.0, 0.0)
    assert near(v.Magnitude(), 5.0) and near(v.SquareMagnitude(), 25.0)


def test_gp_VecTest_Normalize():
    n = gp_Vec(3.0, 4.0, 0.0).Normalized()
    assert near(n.Magnitude(), 1.0) and near(n.X(), 0.6) and near(n.Y(), 0.8)


def test_gp_VecTest_Angle():
    assert near(gp_Vec(1.0, 0.0, 0.0).Angle(gp_Vec(0.0, 1.0, 0.0)), math.pi / 2, ANG)


def test_gp_VecTest_IsParallel():
    assert gp_Vec(1.0, 0.0, 0.0).IsParallel(gp_Vec(5.0, 0.0, 0.0), ANG)


def test_gp_VecTest_IsNormal():
    assert gp_Vec(1.0, 0.0, 0.0).IsNormal(gp_Vec(0.0, 1.0, 0.0), ANG)


def test_gp_VecTest_IsOpposite():
    assert gp_Vec(1.0, 0.0, 0.0).IsOpposite(gp_Vec(-3.0, 0.0, 0.0), ANG)


def test_gp_VecTest_Reverse():
    assert c3(gp_Vec(1.0, 2.0, 3.0).Reversed()) == (-1.0, -2.0, -3.0)


def test_gp_VecTest_SetLinearForm():
    r = gp_Vec()
    r.SetLinearForm(2.0, gp_Vec(1.0, 0.0, 0.0), 3.0, gp_Vec(0.0, 1.0, 0.0))
    assert near(r.X(), 2.0) and near(r.Y(), 3.0) and near(r.Z(), 0.0)
