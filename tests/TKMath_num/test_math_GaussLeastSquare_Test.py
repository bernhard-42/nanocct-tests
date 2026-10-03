# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_GaussLeastSquare_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.math import math_GaussLeastSquare, math_Matrix, math_Vector

TOLERANCE = 1.0e-6


def mat(rows):
    m = math_Matrix(1, len(rows), 1, len(rows[0]))
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            m[i + 1, j + 1] = v
    return m


def vec(values):
    v = math_Vector(1, len(values))
    for i, x in enumerate(values):
        v[i + 1] = x
    return v


def solve(rows, b, *args):
    solver = math_GaussLeastSquare(mat(rows), *args)
    assert solver.IsDone()
    x = math_Vector(1, len(rows[0]))
    solver.Solve(vec(b), x)
    return x


def test_math_GaussLeastSquare_SimpleLinearSystem():
    x = solve([[2, 1], [1, 2]], [5, 4])
    assert abs(x(1) - 2.0) <= TOLERANCE
    assert abs(x(2) - 1.0) <= TOLERANCE


def test_math_GaussLeastSquare_OverdeterminedSystem():
    x = solve([[1, 1], [2, -1], [1, 2]], [3, 1, 5])
    assert math.isfinite(x(1)) and math.isfinite(x(2))
    assert abs(x(1) - 1.4) <= 0.2
    assert abs(x(2) - 1.8) <= 0.2


def test_math_GaussLeastSquare_SingleVariable():
    x = solve([[2]], [4])
    assert abs(x(1) - 2.0) <= TOLERANCE


def test_math_GaussLeastSquare_ThreeByThreeSystem():
    x = solve([[2, 1, 1], [1, 2, 1], [1, 1, 2]], [8, 7, 6])
    assert abs(x(1) - 2.75) <= 0.1
    assert abs(x(2) - 1.75) <= 0.1
    assert abs(x(3) - 0.75) <= 0.1


def test_math_GaussLeastSquare_IdentityMatrix():
    x = solve([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [5, 3, 7])
    for i, e in zip((1, 2, 3), (5.0, 3.0, 7.0)):
        assert abs(x(i) - e) <= TOLERANCE


def test_math_GaussLeastSquare_CustomMinPivot():
    x = solve([[1, 0], [0, 1]], [2, 3], 1.0e-15)
    assert abs(x(1) - 2.0) <= TOLERANCE
    assert abs(x(2) - 3.0) <= TOLERANCE


def test_math_GaussLeastSquare_LargeDiagonalValues():
    x = solve([[100, 1], [1, 100]], [101, 102])
    assert abs(x(1) - 1.0) <= 0.02
    assert abs(x(2) - 1.01) <= 0.02


def test_math_GaussLeastSquare_ScaledSystem():
    x = solve([[0.001, 0.002], [0.003, 0.004]], [0.005, 0.007])
    assert math.isfinite(x(1)) and math.isfinite(x(2))


def test_math_GaussLeastSquare_RectangularMatrix():
    x = solve([[1, 1], [1, 2], [2, 1], [2, 2]], [3, 4, 4, 5])
    assert math.isfinite(x(1)) and math.isfinite(x(2))
    assert x(1) > 0.0
    assert x(2) > 0.0


def test_math_GaussLeastSquare_PolynomialFitting():
    x = solve([[1, 0, 0], [1, 1, 1], [1, 2, 4], [1, 3, 9]], [1, 4, 9, 16])
    for i in (1, 2, 3):
        assert math.isfinite(x(i))
    assert x(3) > 0.5


def test_math_GaussLeastSquare_LinearFitting():
    x = solve([[1, 1], [1, 2], [1, 3]], [2, 4, 6])
    assert abs(x(1)) <= TOLERANCE
    assert abs(x(2) - 2.0) <= TOLERANCE


def test_math_GaussLeastSquare_NoisyData():
    x = solve([[1, 1], [1, 2], [1, 3], [1, 4], [1, 5]], [2.1, 2.9, 4.1, 4.9, 6.1])
    assert abs(x(1) - 1.0) <= 0.2
    assert abs(x(2) - 1.0) <= 0.2


def test_math_GaussLeastSquare_ZeroRightHandSide():
    x = solve([[1, 0], [0, 1]], [0, 0])
    assert abs(x(1)) <= TOLERANCE
    assert abs(x(2)) <= TOLERANCE


def test_math_GaussLeastSquare_MultipleRightHandSides():
    solver = math_GaussLeastSquare(mat([[2, 1], [1, 2]]))
    assert solver.IsDone()
    x1 = math_Vector(1, 2)
    solver.Solve(vec([3, 3]), x1)
    assert abs(x1(1) - 1.0) <= TOLERANCE
    assert abs(x1(2) - 1.0) <= TOLERANCE
    x2 = math_Vector(1, 2)
    solver.Solve(vec([5, 4]), x2)
    assert abs(x2(1) - 2.0) <= TOLERANCE
    assert abs(x2(2) - 1.0) <= TOLERANCE
