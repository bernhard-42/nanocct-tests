# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathLin_Comparison_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import MathLin
from nanocct.math import math_Gauss, math_Matrix, math_Vector

THE_TOLERANCE = 1.0e-10


def near(a, b, tol):
    return abs(a - b) <= tol


def mat(rows):
    m = math_Matrix(1, len(rows), 1, len(rows[0]))
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row, 1):
            m[i, j] = float(v)
    return m


def vec(values):
    v = math_Vector(1, len(values))
    for i, x in enumerate(values, 1):
        v[i] = float(x)
    return v


def gauss_solve(a, b, n):
    g = math_Gauss(a)
    assert g.IsDone()
    x = math_Vector(1, n)
    g.Solve(b, x)
    return x


def test_MathLin_ComparisonTest_Solve_3x3System():
    a = mat([[3.0, 2.0, -1.0], [2.0, -2.0, 4.0], [-1.0, 0.5, -1.0]])
    b = vec([1.0, -2.0, 0.0])
    new = MathLin.Solve(a, b)
    assert new.IsDone()
    assert new.Solution is not None
    old_x = gauss_solve(a, b, 3)
    for i in range(1, 4):
        assert near(new.Solution(i), old_x(i), THE_TOLERANCE)


def test_MathLin_ComparisonTest_Solve_5x5System():
    a = math_Matrix(1, 5, 1, 5, 0.0)
    for i in range(1, 6):
        a[i, i] = 10.0
        if i > 1:
            a[i, i - 1] = -2.0
        if i < 5:
            a[i, i + 1] = -3.0
    b = vec([1, 2, 3, 4, 5])
    new = MathLin.Solve(a, b)
    assert new.IsDone()
    old_x = gauss_solve(a, b, 5)
    for i in range(1, 6):
        assert near(new.Solution(i), old_x(i), THE_TOLERANCE)


def test_MathLin_ComparisonTest_Determinant_3x3Matrix():
    a = mat([[6, 1, 1], [4, -2, 5], [2, 8, 7]])
    new = MathLin.Determinant(a)
    assert new.IsDone()
    assert new.Determinant is not None
    g = math_Gauss(a)
    assert g.IsDone()
    assert near(new.Determinant, g.Determinant(), THE_TOLERANCE)
    assert near(new.Determinant, -306.0, THE_TOLERANCE)


def test_MathLin_ComparisonTest_Determinant_IdentityMatrix():
    a = math_Matrix(1, 4, 1, 4, 0.0)
    for i in range(1, 5):
        a[i, i] = 1.0
    new = MathLin.Determinant(a)
    assert new.IsDone()
    g = math_Gauss(a)
    assert g.IsDone()
    assert near(new.Determinant, 1.0, THE_TOLERANCE)
    assert near(g.Determinant(), 1.0, THE_TOLERANCE)


def test_MathLin_ComparisonTest_Invert_3x3Matrix():
    a = mat([[1, 2, 3], [0, 1, 4], [5, 6, 0]])
    new = MathLin.Invert(a)
    assert new.IsDone()
    assert new.Inverse is not None
    g = math_Gauss(a)
    assert g.IsDone()
    old_inv = math_Matrix(1, 3, 1, 3)
    g.Invert(old_inv)
    for i in range(1, 4):
        for j in range(1, 4):
            assert near(new.Inverse(i, j), old_inv(i, j), THE_TOLERANCE)


def test_MathLin_ComparisonTest_Invert_VerifyByMultiplication():
    a = mat([[2, 1, 1], [1, 3, 2], [1, 2, 2]])
    new = MathLin.Invert(a)
    assert new.IsDone()
    prod = a * new.Inverse
    for i in range(1, 4):
        for j in range(1, 4):
            assert near(prod(i, j), 1.0 if i == j else 0.0, THE_TOLERANCE)


def test_MathLin_ComparisonTest_LU_Decomposition():
    a = mat([[2, 1, 1], [4, 3, 3], [8, 7, 9]])
    lu = MathLin.LU(a)
    assert lu.IsDone()
    assert lu.LU is not None
    assert lu.Pivot is not None
    assert lu.Determinant is not None
    b = vec([1, 2, 3])
    sol = MathLin.Solve(a, b)
    assert sol.IsDone()
    residual = a * sol.Solution
    for i in range(1, 4):
        assert near(residual(i) - b(i), 0.0, THE_TOLERANCE)


def test_MathLin_ComparisonTest_SingularMatrix_Detection():
    a = mat([[1, 2, 3], [4, 5, 6], [1, 2, 3]])
    assert not MathLin.LU(a).IsDone()
    assert not math_Gauss(a).IsDone()


def test_MathLin_ComparisonTest_IllConditioned_HilbertMatrix():
    n = 4
    h = math_Matrix(1, n, 1, n)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            h[i, j] = 1.0 / float(i + j - 1)
    b = math_Vector(1, n, 1.0)
    new = MathLin.Solve(h, b)
    assert new.IsDone()
    old_x = gauss_solve(h, b, n)
    for i in range(1, n + 1):
        assert near(new.Solution(i), old_x(i), 1.0e-6)


def test_MathLin_ComparisonTest_Determinant_MultipleMatrices():
    cases = [
        (1.0, 0.0, 0.0, 1.0, 1.0),
        (2.0, 0.0, 0.0, 3.0, 6.0),
        (1.0, 2.0, 3.0, 4.0, -2.0),
        (0.0, 1.0, 1.0, 0.0, -1.0),
    ]
    for a11, a12, a21, a22, expected in cases:
        a = mat([[a11, a12], [a21, a22]])
        new = MathLin.Determinant(a)
        assert new.IsDone()
        g = math_Gauss(a)
        assert g.IsDone()
        assert near(new.Determinant, g.Determinant(), THE_TOLERANCE)
        assert near(new.Determinant, expected, THE_TOLERANCE)


def test_MathLin_ComparisonTest_Solve_KnownSolution():
    a = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    x_exp = vec([1, 2, 3])
    b = a * x_exp
    new = MathLin.Solve(a, b)
    assert new.IsDone()
    for i in range(1, 4):
        assert near(new.Solution(i), x_exp(i), THE_TOLERANCE)


def test_MathLin_ComparisonTest_Solve_ComplexKnownSolution():
    a = mat([[5, 7, 6, 5], [7, 10, 8, 7], [6, 8, 10, 9], [5, 7, 9, 10]])
    x_exp = vec([1, -1, 2, -2])
    b = a * x_exp
    new = MathLin.Solve(a, b)
    assert new.IsDone()
    old_x = gauss_solve(a, b, 4)
    for i in range(1, 5):
        assert near(new.Solution(i), x_exp(i), THE_TOLERANCE)
        assert near(old_x(i), x_exp(i), THE_TOLERANCE)
        assert near(new.Solution(i), old_x(i), THE_TOLERANCE)
