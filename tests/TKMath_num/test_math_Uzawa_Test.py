# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Uzawa_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.math import math_Matrix, math_Uzawa, math_Vector

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


C_PM = [[1, 1], [1, -1]]


def test_math_Uzawa_SimpleEqualityConstraints():
    s = math_Uzawa(mat([[2, 1], [1, 2]]), vec([5, 4]), vec([0, 0]))
    assert s.IsDone()
    sol = s.Value()
    assert abs(sol(1) - 2.0) <= TOLERANCE
    assert abs(sol(2) - 1.0) <= TOLERANCE


def test_math_Uzawa_OverdeterminedSystem():
    s = math_Uzawa(mat(C_PM), vec([3, 1]), vec([0, 0]))
    assert s.IsDone()
    sol = s.Value()
    assert abs(sol(1) - 2.0) <= TOLERANCE
    assert abs(sol(2) - 1.0) <= TOLERANCE


def test_math_Uzawa_WithInequalityConstraints():
    s = math_Uzawa(mat([[1, 1]]), vec([2]), vec([1, 1]), 0, 1)
    assert s.IsDone()
    sol = s.Value()
    assert abs(sol(1) + sol(2) - 2.0) <= TOLERANCE


def test_math_Uzawa_CustomTolerances():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([0, 0]), 1.0e-8, 1.0e-8)
    assert s.IsDone()
    sol = s.Value()
    assert abs(sol(1) - 1.0) <= 1e-6
    assert abs(sol(2) - 1.0) <= 1e-6


def test_math_Uzawa_CustomIterations():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([10, 10]), 1.0e-6, 1.0e-6, 50)
    assert s.IsDone()
    assert s.NbIterations() <= 50


def test_math_Uzawa_InitialError():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([5, 3]))
    assert s.IsDone()
    e = s.InitialError()
    assert abs(e(1) - 6.0) <= TOLERANCE
    assert abs(e(2) - 2.0) <= TOLERANCE


def test_math_Uzawa_ErrorVector():
    x0 = vec([0, 0])
    s = math_Uzawa(mat(C_PM), vec([2, 0]), x0)
    assert s.IsDone()
    err = s.Error()
    sol = s.Value()
    assert abs(err(1) - (sol(1) - x0(1))) <= TOLERANCE
    assert abs(err(2) - (sol(2) - x0(2))) <= TOLERANCE


def test_math_Uzawa_DualVariables():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([0, 0]))
    assert s.IsDone()
    d = math_Vector(1, 2)
    s.Duale(d)
    assert math.isfinite(d(1)) and math.isfinite(d(2))


def test_math_Uzawa_InverseMatrix():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([0, 0]))
    assert s.IsDone()
    inv = s.InverseCont()
    assert inv.RowNumber() == 2
    assert inv.ColNumber() == 2
    for i in (1, 2):
        for j in (1, 2):
            assert math.isfinite(inv(i, j))


def test_math_Uzawa_LargeSystem():
    n = 4
    c = mat([[2.0 if i == j else 0.5 for j in range(1, n + 1)] for i in range(1, n + 1)])
    s = math_Uzawa(c, vec([float(i) for i in range(1, n + 1)]), vec([0.0] * n))
    assert s.IsDone()
    sol = s.Value()
    for i in range(1, n + 1):
        assert math.isfinite(sol(i))


def test_math_Uzawa_StartingPointNearSolution():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([1.001, 0.999]))
    assert s.IsDone()
    assert s.NbIterations() <= 10
    sol = s.Value()
    assert abs(sol(1) - 1.0) <= TOLERANCE
    assert abs(sol(2) - 1.0) <= TOLERANCE


def test_math_Uzawa_ConsistentSystem():
    s = math_Uzawa(mat([[1, 2], [2, 1]]), vec([5, 7]), vec([0, 0]))
    assert s.IsDone()
    sol = s.Value()
    assert abs(sol(1) + 2.0 * sol(2) - 5.0) <= TOLERANCE
    assert abs(2.0 * sol(1) + sol(2) - 7.0) <= TOLERANCE


def test_math_Uzawa_SingleVariable():
    s = math_Uzawa(mat([[2]]), vec([4]), vec([0]))
    assert s.IsDone()
    assert abs(s.Value()(1) - 2.0) <= TOLERANCE


def test_math_Uzawa_IterationCount():
    s = math_Uzawa(mat(C_PM), vec([2, 0]), vec([0, 0]))
    assert s.IsDone()
    assert 0 < s.NbIterations() <= 500
