# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_SVD_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_Matrix, math_SVD, math_Vector

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


def check_solution(a, x, b, tol=1.0e-10):
    assert a.ColNumber() == x.Length()
    assert a.RowNumber() == b.Length()
    for i in range(a.LowerRow(), a.UpperRow() + 1):
        s = 0.0
        for j in range(a.LowerCol(), a.UpperCol() + 1):
            s += a(i, j) * x(j - a.LowerCol() + x.Lower())
        assert abs(s - b(i - a.LowerRow() + b.Lower())) <= tol


def well_conditioned():
    return mat([[2, 1, 0], [1, 2, 1], [0, 1, 2]])


def solve(a, b_values, ncols, lo_x=1, lo_b=1):
    svd = math_SVD(a)
    assert svd.IsDone()
    b = vec(b_values, lo_b)
    x = math_Vector(lo_x, lo_x + ncols - 1)
    svd.Solve(b, x)
    return b, x


def test_MathSVDTest_WellConditionedSquareMatrix():
    a = well_conditioned()
    b, x = solve(a, [6, 9, 8], 3)
    check_solution(a, x, b)


def test_MathSVDTest_IdentityMatrix():
    b, x = solve(mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), [5, 7, 9], 3)
    for i in (1, 2, 3):
        assert abs(x(i) - b(i)) <= CONFUSION


def test_MathSVDTest_DiagonalMatrix():
    b, x = solve(mat([[3, 0, 0], [0, 5, 0], [0, 0, 2]]), [12, 20, 8], 3)
    for i in (1, 2, 3):
        assert abs(x(i) - 4.0) <= CONFUSION


def test_MathSVDTest_OverdeterminedSystem():
    a = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]])
    b, x = solve(a, [2, 3, 4, 9], 3)
    check_solution(a, x, b, 1.0e-8)


def test_MathSVDTest_UnderdeterminedSystem():
    a = mat([[1, 2, 3], [4, 5, 6]])
    b, x = solve(a, [14, 32], 3)
    check_solution(a, x, b, 1.0e-8)


def test_MathSVDTest_RankDeficientMatrix():
    a = mat([[1, 2, 3], [2, 4, 6], [1, 1, 1]])
    b, x = solve(a, [6, 12, 3], 3)
    check_solution(a, x, b, 1.0e-6)


def test_MathSVDTest_SingleRowMatrix():
    a = mat([[2, 3, 4]])
    b, x = solve(a, [20], 3)
    check_solution(a, x, b)


def test_MathSVDTest_SingleColumnMatrix():
    _, x = solve(mat([[2], [3], [4]]), [4, 6, 8], 1)
    assert abs(x(1) - 2.0) <= 1e-10


def test_MathSVDTest_PseudoInverseMethod():
    a = well_conditioned()
    svd = math_SVD(a)
    assert svd.IsDone()
    pinv = math_Matrix(a.LowerCol(), a.UpperCol(), a.LowerRow(), a.UpperRow())
    svd.PseudoInverse(pinv)
    for i in range(1, 4):
        for j in range(1, 4):
            p = sum(pinv(i, k) * a(k, j) for k in range(1, 4))
            assert abs(p - (1.0 if i == j else 0.0)) <= 1e-10


def test_MathSVDTest_DimensionCompatibility():
    a = well_conditioned()
    b, x = solve(a, [1, 2, 3], 3)
    assert x.Length() == 3
    assert b.Length() == 3
    assert a.RowNumber() == 3
    assert a.ColNumber() == 3


def test_MathSVDTest_SingularValues():
    svd = math_SVD(mat([[3, 0], [0, 4]]))
    assert svd.IsDone()
    x1 = math_Vector(1, 2)
    svd.Solve(vec([6, 0]), x1)
    assert abs(x1(1) - 2.0) <= 1e-10
    assert abs(x1(2)) <= 1e-10
    x2 = math_Vector(1, 2)
    svd.Solve(vec([0, 12]), x2)
    assert abs(x2(1)) <= 1e-10
    assert abs(x2(2) - 3.0) <= 1e-10


def test_MathSVDTest_DifferentMatrixBounds():
    a = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], lo_r=2, lo_c=3)
    _, x = solve(a, [5, 7, 9], 3, lo_x=3, lo_b=2)
    assert abs(x(3) - 5.0) <= CONFUSION
    assert abs(x(4) - 7.0) <= CONFUSION
    assert abs(x(5) - 9.0) <= CONFUSION


def test_MathSVDTest_LargerMatrix():
    rows = [[10.0 if i == j else 1.0 / (abs(i - j) + 1.0) for j in range(1, 6)] for i in range(1, 6)]
    a = mat(rows)
    b, x = solve(a, [i * 2.0 for i in range(1, 6)], 5)
    check_solution(a, x, b, 1.0e-8)
