# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_XYZ_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_XYZ
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def c3(v):
    return (v.X(), v.Y(), v.Z())


def test_gp_XYZTest_DefaultConstructor():
    assert c3(gp_XYZ()) == (0.0, 0.0, 0.0)


def test_gp_XYZTest_CoordinateConstructor():
    assert c3(gp_XYZ(1.0, 2.0, 3.0)) == (1.0, 2.0, 3.0)


def test_gp_XYZTest_SetCoord():
    v = gp_XYZ()
    v.SetCoord(7.0, 8.0, 9.0)
    assert c3(v) == (7.0, 8.0, 9.0)


def test_gp_XYZTest_Accessors():
    v = gp_XYZ(1.0, 2.0, 3.0)
    assert (v.Coord(1), v.Coord(2), v.Coord(3)) == (1.0, 2.0, 3.0)


def test_gp_XYZTest_Add():
    assert c3(gp_XYZ(1.0, 2.0, 3.0) + gp_XYZ(4.0, 5.0, 6.0)) == (5.0, 7.0, 9.0)


def test_gp_XYZTest_Subtract():
    assert c3(gp_XYZ(4.0, 5.0, 6.0) - gp_XYZ(1.0, 2.0, 3.0)) == (3.0, 3.0, 3.0)


def test_gp_XYZTest_Multiply():
    assert c3(gp_XYZ(1.0, 2.0, 3.0) * 2.0) == (2.0, 4.0, 6.0)


def test_gp_XYZTest_Divide():
    assert c3(gp_XYZ(4.0, 6.0, 8.0) / 2.0) == (2.0, 3.0, 4.0)


def test_gp_XYZTest_Cross():
    c = gp_XYZ(1.0, 0.0, 0.0).Crossed(gp_XYZ(0.0, 1.0, 0.0))
    assert abs(c.X()) <= CONF and abs(c.Y()) <= CONF and abs(c.Z() - 1.0) <= CONF


def test_gp_XYZTest_Dot():
    assert gp_XYZ(1.0, 2.0, 3.0).Dot(gp_XYZ(4.0, 5.0, 6.0)) == 32.0


def test_gp_XYZTest_CrossMagnitude():
    assert abs(gp_XYZ(1.0, 0.0, 0.0).CrossMagnitude(gp_XYZ(0.0, 1.0, 0.0)) - 1.0) <= CONF


def test_gp_XYZTest_CrossSquareMagnitude():
    assert abs(gp_XYZ(1.0, 0.0, 0.0).CrossSquareMagnitude(gp_XYZ(0.0, 1.0, 0.0)) - 1.0) <= CONF


def test_gp_XYZTest_DotCross():
    r = gp_XYZ(1.0, 0.0, 0.0).DotCross(gp_XYZ(0.0, 1.0, 0.0), gp_XYZ(0.0, 0.0, 1.0))
    assert abs(r - 1.0) <= CONF


def test_gp_XYZTest_Modulus():
    assert abs(gp_XYZ(3.0, 4.0, 0.0).Modulus() - 5.0) <= CONF


def test_gp_XYZTest_SquareModulus():
    assert abs(gp_XYZ(3.0, 4.0, 0.0).SquareModulus() - 25.0) <= CONF


def test_gp_XYZTest_SetLinearForm():
    r = gp_XYZ()
    r.SetLinearForm(2.0, gp_XYZ(1.0, 0.0, 0.0), 3.0, gp_XYZ(0.0, 1.0, 0.0))
    assert abs(r.X() - 2.0) <= CONF and abs(r.Y() - 3.0) <= CONF and abs(r.Z()) <= CONF


def test_gp_XYZTest_IsEqual():
    a = gp_XYZ(1.0, 2.0, 3.0)
    assert a.IsEqual(gp_XYZ(1.0, 2.0, 3.0), CONF)
    assert not a.IsEqual(gp_XYZ(1.0, 2.0, 4.0), CONF)
