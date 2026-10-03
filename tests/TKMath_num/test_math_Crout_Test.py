# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Crout_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_Crout, math_Matrix, math_Vector


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


SING = [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
IDENT = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_MathCroutTest_SimpleSymmetricMatrix():
    c = math_Crout(mat([[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]]))
    assert c.IsDone()
    x = math_Vector(1, 3)
    c.Solve(vec([7, 5.5, 3.5]), x)
    for i in (1, 2, 3):
        assert abs(x(i) - 1.0) <= 1e-10


def test_MathCroutTest_IdentityMatrix():
    c = math_Crout(mat(IDENT))
    assert c.IsDone()
    x = math_Vector(1, 3)
    c.Solve(vec([5, 7, 9]), x)
    for i, e in zip((1, 2, 3), (5.0, 7.0, 9.0)):
        assert abs(x(i) - e) <= 1e-12
    inv = c.Inverse()
    for i in (1, 2, 3):
        assert abs(inv(i, i) - 1.0) <= 1e-12


def test_MathCroutTest_DiagonalMatrix():
    c = math_Crout(mat([[2, 0, 0], [0, 3, 0], [0, 0, 4]]))
    assert c.IsDone()
    x = math_Vector(1, 3)
    c.Solve(vec([4, 9, 12]), x)
    for i, e in zip((1, 2, 3), (2.0, 3.0, 3.0)):
        assert abs(x(i) - e) <= 1e-12


def test_MathCroutTest_LowerTriangularInput():
    c = math_Crout(mat([[4, 0, 0], [2, 3, 0], [1, 0.5, 2]]))
    assert c.IsDone()


def test_MathCroutTest_CustomMinPivot():
    a = mat([[1.0e-15, 1], [1, 1]])
    assert not math_Crout(a, 1.0e-10).IsDone()
    assert math_Crout(a, 1.0e-20).IsDone()


def test_MathCroutTest_SingularMatrix():
    assert not math_Crout(mat(SING)).IsDone()


def test_MathCroutTest_NonSquareMatrixCheck():
    a = mat([[1, 2, 3], [4, 5, 6]])
    assert a.RowNumber() != a.ColNumber()


def test_MathCroutTest_DimensionCompatibilityInSolve():
    c = math_Crout(mat(IDENT))
    assert c.IsDone()
    x = math_Vector(1, 3)
    c.Solve(vec([1, 2, 3]), x)
    assert x.Length() == 3


def test_MathCroutTest_SingularMatrixState():
    assert not math_Crout(mat(SING)).IsDone()


def test_MathCroutTest_LargerMatrix():
    a = mat([[10, 1, 2, 3], [1, 10, 1, 4], [2, 1, 10, 1], [3, 4, 1, 10]])
    c = math_Crout(a)
    assert c.IsDone()
    b = vec([16, 16, 14, 18])
    x = math_Vector(1, 4)
    c.Solve(b, x)
    norm = 0.0
    for i in range(1, 5):
        r = sum(a(i, j) * x(j) for j in range(1, 5)) - b(i)
        norm += r * r
    assert norm < 1.0e-20


def test_MathCroutTest_CustomBounds():
    c = math_Crout(mat([[4, 2, 1], [2, 3, 0.5], [1, 0.5, 2]], lo_r=2, lo_c=3))
    assert c.IsDone()
    x = math_Vector(3, 5)
    c.Solve(vec([7, 5.5, 3.5], lo=2), x)
    assert x(3) > 0.0
    assert x(4) > 0.0
    assert x(5) > 0.0
