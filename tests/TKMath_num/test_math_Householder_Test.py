# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Householder_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_Householder, math_Matrix, math_Vector

CONFUSION = 1e-7


def mat(rows, lo_r=1, lo_c=1):
    m = math_Matrix(lo_r, lo_r + len(rows) - 1, lo_c, lo_c + len(rows[0]) - 1)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            m[lo_r + i, lo_c + j] = v
    return m


def vec(values, lo=1):
    v = math_Vector(lo, lo + len(values) - 1)
    for i, x in enumerate(values):
        v[lo + i] = x
    return v


def test_MathHouseholderTest_ExactlyDeterminedSystem():
    a = mat([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
    b = vec([14, 32, 55])
    h = math_Householder(a, b)
    assert h.IsDone()
    sol = math_Vector(1, 3)
    h.Value(sol, 1)
    for i in range(1, 4):
        s = sum(a(i, j) * sol(j) for j in range(1, 4))
        assert abs(s - b(i)) <= 1e-10


def test_MathHouseholderTest_OverdeterminedSystem():
    h = math_Householder(mat([[1, 1], [1, 2], [2, 1], [1, 3]]), vec([2, 3, 3, 4]))
    assert h.IsDone()
    sol = math_Vector(1, 2)
    h.Value(sol, 1)
    assert abs(sol(1) - 1.0) <= 1e-6
    assert abs(sol(2) - 1.0) <= 1e-6


def test_MathHouseholderTest_MultipleRightHandSides():
    h = math_Householder(mat([[1, 0], [0, 1], [1, 1]]), mat([[1, 2], [3, 4], [4, 6]]))
    assert h.IsDone()
    sol1 = math_Vector(1, 2)
    h.Value(sol1, 1)
    sol2 = math_Vector(1, 2)
    h.Value(sol2, 2)
    assert abs(sol1(1) - 1.0) <= 1e-6
    assert abs(sol1(2) - 3.0) <= 1e-6
    assert abs(sol2(1) - 2.0) <= 1e-6
    assert abs(sol2(2) - 4.0) <= 1e-6


def test_MathHouseholderTest_NearSingularMatrix():
    a = mat([[1, 2, 3], [2, 4, 6.0 + 1.0e-15], [3, 6, 9.0 + 2.0e-15]])
    h = math_Householder(a, vec([1, 2, 3]))
    assert not h.IsDone()


def test_MathHouseholderTest_CustomEpsilon():
    a = mat([[1.0e-3, 1], [2.0e-3, 2]])
    b = vec([1, 2])
    assert math_Householder(a, b).IsDone()
    assert not math_Householder(a, b, 1.0e-2).IsDone()


def test_MathHouseholderTest_IdentityMatrix():
    h = math_Householder(mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), vec([5, 7, 9]))
    assert h.IsDone()
    sol = math_Vector(1, 3)
    h.Value(sol, 1)
    for i, e in zip((1, 2, 3), (5.0, 7.0, 9.0)):
        assert abs(sol(i) - e) <= CONFUSION


def test_MathHouseholderTest_DimensionCompatibility():
    a = mat([[1, 2], [3, 4], [5, 6]])
    assert math_Householder(a, vec([1, 2, 3])).IsDone()
    assert math_Householder(a, mat([[1, 4], [2, 5], [3, 6]])).IsDone()


def test_MathHouseholderTest_NearZeroMatrixState():
    h = math_Householder(mat([[1.0e-25, 0], [0, 1.0e-25]]), vec([1, 2]), 1.0e-10)
    assert not h.IsDone()


def test_MathHouseholderTest_ValidIndexRange():
    b = mat([[1, 2], [3, 4]])
    h = math_Householder(mat([[1, 0], [0, 1]]), b)
    assert h.IsDone()
    sol = math_Vector(1, 2)
    h.Value(sol, 1)
    assert sol.Length() == 2
    h.Value(sol, 2)
    assert sol.Length() == 2
    assert b.ColNumber() == 2


def test_MathHouseholderTest_RegressionTest():
    h = math_Householder(mat([[2, 1], [1, 1], [1, 2]]), vec([5, 3, 4]))
    assert h.IsDone()
    sol = math_Vector(1, 2)
    h.Value(sol, 1)
    assert abs(sol(1) - 2.0) <= 1e-10
    assert abs(sol(2) - 1.0) <= 1e-10
