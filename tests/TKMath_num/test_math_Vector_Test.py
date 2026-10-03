# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Vector_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.gp import gp_XY, gp_XYZ
from nanocct.math import math_Matrix, math_Vector

CONF = 1e-7


def check_vectors_equal(v1, v2, tol=CONF):
    assert v1.Length() == v2.Length()
    assert v1.Lower() == v2.Lower()
    assert v1.Upper() == v2.Upper()
    for i in range(v1.Lower(), v1.Upper() + 1):
        assert abs(v1(i) - v2(i)) <= tol


def vec(lo, values):
    v = math_Vector(lo, lo + len(values) - 1)
    for k, x in enumerate(values):
        v[lo + k] = x
    return v


def mat_2x3():
    m = math_Matrix(1, 2, 1, 3)
    m[1, 1] = 1.0
    m[1, 2] = 2.0
    m[1, 3] = 3.0
    m[2, 1] = 4.0
    m[2, 2] = 5.0
    m[2, 3] = 6.0
    return m


def test_MathVectorTest_Constructors():
    v1 = math_Vector(1, 5)
    assert v1.Length() == 5
    assert v1.Lower() == 1
    assert v1.Upper() == 5

    v2 = math_Vector(-2, 3, 2.5)
    assert v2.Length() == 6
    assert v2.Lower() == -2
    assert v2.Upper() == 3
    for i in range(-2, 4):
        assert v2(i) == 2.5

    # (the external-array constructor math_Vector(double*, lo, hi) is not bound)

    v4 = math_Vector(v2)
    check_vectors_equal(v2, v4)


def test_MathVectorTest_GeometryConstructors():
    vxy = math_Vector(gp_XY(3.5, 4.5))
    assert vxy.Length() == 2
    assert vxy.Lower() == 1
    assert vxy.Upper() == 2
    assert vxy(1) == pytest.approx(3.5)
    assert vxy(2) == pytest.approx(4.5)

    vxyz = math_Vector(gp_XYZ(1.1, 2.2, 3.3))
    assert vxyz.Length() == 3
    assert vxyz.Lower() == 1
    assert vxyz.Upper() == 3
    assert vxyz(1) == pytest.approx(1.1)
    assert vxyz(2) == pytest.approx(2.2)
    assert vxyz(3) == pytest.approx(3.3)


def test_MathVectorTest_InitAndAccess():
    v = math_Vector(1, 4)
    v.Init(7.0)
    for i in range(1, 5):
        assert v(i) == 7.0

    v[2] = 15.0
    assert v(2) == 15.0

    v.SetValue(3, 25.0)
    assert v(3) == 25.0
    assert v.Value(3) == 25.0


def test_MathVectorTest_VectorProperties():
    v = vec(1, [3.0, 4.0, 0.0, -2.0])
    assert abs(v.Norm() - math.sqrt(29.0)) <= CONF
    assert abs(v.Norm2() - 29.0) <= CONF
    assert v.Max() == 2
    assert v.Min() == 4


def test_MathVectorTest_Normalization():
    v = vec(1, [3.0, 4.0, 0.0])
    assert abs(v.Norm() - 5.0) <= CONF

    n = v.Normalized()
    assert abs(n.Norm() - 1.0) <= CONF
    assert abs(n(1) - 3.0 / 5.0) <= CONF
    assert abs(n(2) - 4.0 / 5.0) <= CONF
    assert abs(n(3) - 0.0) <= CONF

    assert abs(v.Norm() - 5.0) <= CONF

    v.Normalize()
    assert abs(v.Norm() - 1.0) <= CONF
    check_vectors_equal(v, n)


def test_MathVectorTest_ZeroVectorHandling():
    z = math_Vector(1, 3, 0.0)
    assert z.Norm() == pytest.approx(0.0)

    nz = vec(1, [1.0, 0.0, 0.0])
    assert nz.Norm() == pytest.approx(1.0)
    nz.Normalize()
    assert nz.Norm() == pytest.approx(1.0)


def test_MathVectorTest_Inversion():
    v = vec(1, [1.0, 2.0, 3.0, 4.0, 5.0])
    inv = v.Inverse()
    assert inv(1) == 5.0
    assert inv(2) == 4.0
    assert inv(3) == 3.0
    assert inv(4) == 2.0
    assert inv(5) == 1.0

    assert v(1) == 1.0
    assert v(5) == 5.0

    v.Invert()
    check_vectors_equal(v, inv)


def test_MathVectorTest_ScalarOperations():
    v = vec(1, [2.0, 4.0, 6.0])

    mul = v.Multiplied(2.5)
    assert mul(1) == 5.0
    assert mul(2) == 10.0
    assert mul(3) == 15.0

    tmul = v.TMultiplied(2.5)
    check_vectors_equal(mul, tmul)

    v.Multiply(0.5)
    assert (v(1), v(2), v(3)) == (1.0, 2.0, 3.0)

    v *= 3.0
    assert (v(1), v(2), v(3)) == (3.0, 6.0, 9.0)

    div = v.Divided(3.0)
    assert (div(1), div(2), div(3)) == (1.0, 2.0, 3.0)

    v.Divide(3.0)
    check_vectors_equal(v, div)

    v *= 6.0
    v /= 2.0
    assert (v(1), v(2), v(3)) == (3.0, 6.0, 9.0)


def test_MathVectorTest_DivisionOperations():
    v = math_Vector(1, 3, 2.0)
    v.Divide(2.0)
    assert v(1) == pytest.approx(1.0)

    v2 = math_Vector(1, 3, 4.0)
    r = v2.Divided(2.0)
    assert r(1) == pytest.approx(2.0)


def test_MathVectorTest_VectorAdditionSubtraction():
    v1 = vec(1, [1.0, 2.0, 3.0])
    v2 = vec(1, [4.0, 5.0, 6.0])

    add = v1.Added(v2)
    assert (add(1), add(2), add(3)) == (5.0, 7.0, 9.0)
    check_vectors_equal(add, v1 + v2)

    sub = v1.Subtracted(v2)
    assert (sub(1), sub(2), sub(3)) == (-3.0, -3.0, -3.0)
    check_vectors_equal(sub, v1 - v2)

    c1 = math_Vector(v1)
    c1.Add(v2)
    check_vectors_equal(c1, add)

    c2 = math_Vector(v1)
    c2 += v2
    check_vectors_equal(c2, add)

    c3 = math_Vector(v1)
    c3.Subtract(v2)
    check_vectors_equal(c3, sub)

    c4 = math_Vector(v1)
    c4 -= v2
    check_vectors_equal(c4, sub)


def test_MathVectorTest_VectorOperationsDifferentBounds():
    v1 = vec(0, [1.0, 2.0, 3.0])
    v2 = vec(-1, [4.0, 5.0, 6.0])
    add = v1.Added(v2)
    assert add(0) == 5.0
    assert add(1) == 7.0
    assert add(2) == 9.0


def test_MathVectorTest_DotProduct():
    v1 = vec(1, [1.0, 2.0, 3.0])
    v2 = vec(1, [4.0, 5.0, 6.0])
    dot = v1.Multiplied(v2)
    assert dot == 32.0
    assert v1 * v2 == dot


def test_MathVectorTest_SetOperation():
    v = math_Vector(1, 6)
    v.Init(0.0)
    sub = vec(1, [10.0, 20.0, 30.0])
    v.Set(2, 4, sub)
    assert [v(i) for i in range(1, 7)] == [0.0, 10.0, 20.0, 30.0, 0.0, 0.0]


def test_MathVectorTest_SliceOperation():
    v = vec(1, [10.0, 20.0, 30.0, 40.0, 50.0, 60.0])

    s1 = v.Slice(2, 4)
    assert s1.Length() == 3
    assert s1.Lower() == 2
    assert s1.Upper() == 4
    assert (s1(2), s1(3), s1(4)) == (20.0, 30.0, 40.0)

    s2 = v.Slice(4, 2)
    assert s2.Length() == 3
    assert s2.Lower() == 2
    assert s2.Upper() == 4
    assert (s2(2), s2(3), s2(4)) == (20.0, 30.0, 40.0)


def test_MathVectorTest_VectorMatrixOperations():
    m = mat_2x3()
    v1 = vec(1, [2.0, 3.0])
    v2 = vec(1, [1.0, 2.0, 3.0])

    r1 = v1.Multiplied(m)
    assert r1.Length() == 3
    assert (r1(1), r1(2), r1(3)) == (14.0, 19.0, 24.0)

    r2 = math_Vector(1, 3)
    r2.Multiply(v1, m)
    check_vectors_equal(r1, r2)

    r3 = math_Vector(1, 2)
    r3.Multiply(m, v2)
    assert (r3(1), r3(2)) == (14.0, 32.0)


def test_MathVectorTest_TransposeMatrixOperations():
    m = mat_2x3()
    v1 = vec(1, [2.0, 3.0])
    v2 = vec(1, [1.0, 2.0, 3.0])

    r1 = math_Vector(1, 3)
    r1.TMultiply(m, v1)
    assert (r1(1), r1(2), r1(3)) == (14.0, 19.0, 24.0)

    r2 = math_Vector(1, 2)
    r2.TMultiply(v2, m)
    assert (r2(1), r2(2)) == (14.0, 32.0)


def test_MathVectorTest_ThreeOperandOperations():
    v1 = vec(1, [1.0, 2.0, 3.0])
    v2 = vec(1, [4.0, 5.0, 6.0])
    r = math_Vector(1, 3)

    r.Add(v1, v2)
    assert (r(1), r(2), r(3)) == (5.0, 7.0, 9.0)

    r.Subtract(v1, v2)
    assert (r(1), r(2), r(3)) == (-3.0, -3.0, -3.0)

    r.Multiply(2.5, v1)
    assert (r(1), r(2), r(3)) == (2.5, 5.0, 7.5)


def test_MathVectorTest_OppositeOperation():
    v = vec(1, [1.0, -2.0, 3.0])
    o = v.Opposite()
    assert (o(1), o(2), o(3)) == (-1.0, 2.0, -3.0)
    check_vectors_equal(o, -v)


def test_MathVectorTest_AssignmentOperations():
    v1 = vec(1, [1.0, 2.0, 3.0])
    v2 = math_Vector(1, 3)
    v2.Init(0.0)
    v2.Initialized(v1)
    check_vectors_equal(v1, v2)
    # (operator= has no Python equivalent beyond Initialized)


def test_MathVectorTest_FriendOperators():
    v = vec(1, [2.0, 4.0, 6.0])

    r1 = 3.0 * v
    assert (r1(1), r1(2), r1(3)) == (6.0, 12.0, 18.0)

    r2 = v * 2.5
    assert (r2(1), r2(2), r2(3)) == (5.0, 10.0, 15.0)

    r3 = v / 2.0
    assert (r3(1), r3(2), r3(3)) == (1.0, 2.0, 3.0)


def test_MathVectorTest_EdgeCases():
    s = math_Vector(5, 5, 42.0)
    assert s.Length() == 1
    assert s(5) == 42.0
    assert s.Max() == 5
    assert s.Min() == 5

    n = vec(-2, [10.0, 20.0, 30.0, 40.0])
    assert n.Length() == 4
    assert n.Lower() == -2
    assert n.Upper() == 1
    assert n.Max() == 1
    assert n.Min() == -2


def _resize_case(lo, n_init, new_size, value=lambda i: float(i)):
    v = math_Vector(lo, lo + n_init - 1)
    for i in range(lo, lo + n_init):
        v[i] = value(i)
    v.Resize(new_size)
    assert v.Length() == new_size
    assert v.Lower() == lo
    assert v.Upper() == lo + new_size - 1
    for i in range(lo, lo + min(n_init, new_size)):
        assert v(i) == pytest.approx(value(i))


def test_MathVectorTest_Resize_StackToStack_SameSize():
    _resize_case(1, 10, 10)


def test_MathVectorTest_Resize_StackToStack_Grow():
    _resize_case(1, 5, 20, lambda i: float(i * 10))


def test_MathVectorTest_Resize_StackToStack_Shrink():
    _resize_case(1, 20, 10)


def test_MathVectorTest_Resize_StackToHeap():
    _resize_case(1, 20, 50)


def test_MathVectorTest_Resize_HeapToStack():
    _resize_case(1, 50, 20)


def test_MathVectorTest_Resize_HeapToHeap():
    _resize_case(1, 50, 100)


def test_MathVectorTest_Resize_NegativeLowerBound():
    _resize_case(-5, 11, 8)


def test_MathVectorTest_Multiply_RowVectorByMatrix_AllComponentsEqual():
    v = math_Vector(1, 6, 5.0)
    m = math_Matrix(1, 6, 1, 6, 4.0)
    r = math_Vector(1, 6)
    r.Multiply(v, m)
    for i in range(1, 7):
        assert r(i) == pytest.approx(120.0)


def test_MathVectorTest_TMultiply_RowVectorByTransposedMatrix_ModifiedComponent():
    v = math_Vector(1, 6, 5.0)
    m = math_Matrix(1, 6, 1, 6, 4.0)
    r = math_Vector(1, 6)
    m[2, 1] += 1.0
    r.TMultiply(v, m)
    assert r(1) == pytest.approx(120.0)
    assert r(2) == pytest.approx(125.0)
    for i in range(3, 7):
        assert r(i) == pytest.approx(120.0)
