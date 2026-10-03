# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntPolyh_Point_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.IntPolyh import IntPolyh_Point


def _xyzuv(p):
    return (p.X(), p.Y(), p.Z(), p.U(), p.V())


def test_IntPolyh_Point_DefaultConstructor_AllZero():
    assert _xyzuv(IntPolyh_Point()) == (0.0, 0.0, 0.0, 0.0, 0.0)


def test_IntPolyh_Point_Divide_NormalDivisor_CorrectResult():
    res = IntPolyh_Point(10.0, 20.0, 30.0, 0.5, 0.8).Divide(2.0)
    assert _xyzuv(res) == (5.0, 10.0, 15.0, 0.25, 0.4)


def test_IntPolyh_Point_Divide_ZeroDivisor_ReturnsDefaultPoint():
    res = IntPolyh_Point(10.0, 20.0, 30.0, 0.5, 0.8).Divide(0.0)
    assert _xyzuv(res) == (0.0, 0.0, 0.0, 0.0, 0.0)


def test_IntPolyh_Point_Divide_NearZeroDivisor_ReturnsDefaultPoint():
    res = IntPolyh_Point(1.0, 2.0, 3.0, 0.1, 0.2).Divide(1.0e-20)
    assert (res.X(), res.Y(), res.Z()) == (0.0, 0.0, 0.0)


def test_IntPolyh_Point_Divide_NegativeDivisor_CorrectResult():
    res = IntPolyh_Point(6.0, -9.0, 12.0, 0.3, 0.6).Divide(-3.0)
    assert (res.X(), res.Y(), res.Z()) == (-2.0, 3.0, -4.0)


def test_IntPolyh_Point_Add_CorrectResult():
    res = IntPolyh_Point(1.0, 2.0, 3.0, 0.1, 0.2).Add(IntPolyh_Point(4.0, 5.0, 6.0, 0.3, 0.4))
    assert (res.X(), res.Y(), res.Z()) == (5.0, 7.0, 9.0)


def test_IntPolyh_Point_Sub_CorrectResult():
    res = IntPolyh_Point(5.0, 7.0, 9.0, 0.5, 0.8).Sub(IntPolyh_Point(1.0, 2.0, 3.0, 0.1, 0.2))
    assert (res.X(), res.Y(), res.Z()) == (4.0, 5.0, 6.0)


def test_IntPolyh_Point_SquareModulus_CorrectResult():
    assert IntPolyh_Point(1.0, 2.0, 3.0, 0.0, 0.0).SquareModulus() == 14.0


def test_IntPolyh_Point_SquareDistance_SamePoint_Zero():
    p = IntPolyh_Point(3.0, 4.0, 5.0, 0.0, 0.0)
    assert p.SquareDistance(p) == 0.0


def test_IntPolyh_Point_Dot_OrthogonalVectors_Zero():
    assert IntPolyh_Point(1.0, 0.0, 0.0, 0.0, 0.0).Dot(IntPolyh_Point(0.0, 1.0, 0.0, 0.0, 0.0)) == 0.0
