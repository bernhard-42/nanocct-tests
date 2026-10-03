# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Gauss_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_Gauss, math_Matrix, math_Vector

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


def check_ax_b(a, x, b, n, tol):
    for i in range(1, n + 1):
        s = sum(a(i, j) * x(j) for j in range(1, n + 1))
        assert abs(s - b(i)) <= tol


def test_MathGaussTest_WellConditionedMatrix():
    a = mat([[2, 1, 1], [1, 3, 2], [1, 2, 3]])
    g = math_Gauss(a)
    assert g.IsDone()
    b = vec([1, 2, 3])
    x = math_Vector(1, 3)
    g.Solve(b, x)
    check_ax_b(a, x, b, 3, 1e-10)


def test_MathGaussTest_IdentityMatrix():
    g = math_Gauss(mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
    assert g.IsDone()
    x = math_Vector(1, 3)
    g.Solve(vec([5, 7, 9]), x)
    for i, e in zip((1, 2, 3), (5.0, 7.0, 9.0)):
        assert abs(x(i) - e) <= CONFUSION


def test_MathGaussTest_DiagonalMatrix():
    g = math_Gauss(mat([[2, 0, 0], [0, 3, 0], [0, 0, 4]]))
    assert g.IsDone()
    x = math_Vector(1, 3)
    g.Solve(vec([8, 15, 20]), x)
    for i, e in zip((1, 2, 3), (4.0, 5.0, 5.0)):
        assert abs(x(i) - e) <= CONFUSION


def test_MathGaussTest_InPlaceSolve():
    g = math_Gauss(mat([[1, 2, 3], [2, 5, 8], [3, 8, 14]]))
    assert g.IsDone()
    b = vec([14, 31, 53])
    g.Solve(b)
    for i, e in zip((1, 2, 3), (13.0, -7.0, 5.0)):
        assert abs(b(i) - e) <= 1e-10


def test_MathGaussTest_Determinant():
    g = math_Gauss(mat([[1, 2, 3], [0, 1, 4], [5, 6, 0]]))
    assert g.IsDone()
    assert abs(g.Determinant() - 1.0) <= 1e-12


def test_MathGaussTest_MatrixInversion():
    a = mat([[4, 7], [2, 6]])
    g = math_Gauss(a)
    assert g.IsDone()
    inv = math_Matrix(1, 2, 1, 2)
    g.Invert(inv)
    assert abs(inv(1, 1) - 0.6) <= 1e-12
    assert abs(inv(1, 2) + 0.7) <= 1e-12
    assert abs(inv(2, 1) + 0.2) <= 1e-12
    assert abs(inv(2, 2) - 0.4) <= 1e-12
    for i in (1, 2):
        for j in (1, 2):
            p = sum(a(i, k) * inv(k, j) for k in (1, 2))
            assert abs(p - (1.0 if i == j else 0.0)) <= 1e-12


def test_MathGaussTest_SingularMatrix():
    g = math_Gauss(mat([[1, 2, 3], [2, 4, 6], [3, 6, 9]]))
    if g.IsDone():
        assert abs(g.Determinant()) <= 1e-12


def test_MathGaussTest_CustomMinPivot():
    g1 = math_Gauss(mat([[1.0e-15, 1], [1, 1]]))
    assert g1.IsDone()
    g2 = math_Gauss(mat([[0, 0], [0, 0]]))
    assert not g2.IsDone()


def test_MathGaussTest_LargerMatrix():
    a = mat([[1, 2, 1, 1], [2, 1, 3, 1], [1, 3, 1, 2], [1, 1, 2, 3]])
    g = math_Gauss(a)
    assert g.IsDone()
    b = vec([1, 2, 3, 4])
    x = math_Vector(1, 4)
    g.Solve(b, x)
    check_ax_b(a, x, b, 4, 1e-10)


def test_MathGaussTest_DimensionCompatibility():
    g = math_Gauss(mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
    assert g.IsDone()
    x = math_Vector(1, 3)
    g.Solve(vec([1, 2, 3]), x)
    assert x.Length() == 3
    inv = math_Matrix(1, 3, 1, 3)
    g.Invert(inv)
    assert inv.RowNumber() == 3
    assert inv.ColNumber() == 3


def test_MathGaussTest_SingularMatrixState():
    g = math_Gauss(mat([[1, 2], [2, 4]]))
    assert not g.IsDone()


def test_MathGaussTest_CustomBounds():
    a = mat([[2, 1, 1], [1, 3, 2], [1, 2, 3]], lo_r=2, lo_c=3)
    g = math_Gauss(a)
    assert g.IsDone()
    x = math_Vector(3, 5)
    g.Solve(vec([6, 11, 13], lo=2), x)
    assert abs(x(3) - 0.75) <= 1e-10
    assert abs(x(4) - 1.25) <= 1e-10
    assert abs(x(5) - 3.25) <= 1e-10
