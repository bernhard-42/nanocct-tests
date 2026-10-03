# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Jacobi_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest
from nanocct.math import math_Jacobi, math_Matrix, math_Vector
from nanocct.StdFail import StdFail_NotDone


def mat(rows, lo_r=1, lo_c=1):
    m = math_Matrix(lo_r, lo_r + len(rows) - 1, lo_c, lo_c + len(rows[0]) - 1)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            m[lo_r + i, lo_c + j] = v
    return m


def test_MathJacobiTest_IdentityMatrix():
    j = math_Jacobi(mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
    assert j.IsDone()
    vals = j.Values()
    assert vals.Length() == 3
    for i in (1, 2, 3):
        assert abs(vals(i) - 1.0) <= 1e-10
        assert abs(j.Value(i) - 1.0) <= 1e-10


def test_MathJacobiTest_DiagonalMatrix():
    j = math_Jacobi(mat([[5, 0, 0], [0, 3, 0], [0, 0, 7]]))
    assert j.IsDone()
    vals = j.Values()
    ev = sorted(vals(i) for i in (1, 2, 3))
    for got, exp in zip(ev, (3.0, 5.0, 7.0)):
        assert abs(got - exp) <= 1e-10


def test_MathJacobiTest_SimpleSymmetricMatrix():
    j = math_Jacobi(mat([[3, 1], [1, 3]]))
    assert j.IsDone()
    vals = j.Values()
    ev = sorted(vals(i) for i in (1, 2))
    assert abs(ev[0] - 2.0) <= 1e-10
    assert abs(ev[1] - 4.0) <= 1e-10


def test_MathJacobiTest_EigenvectorVerification():
    a = mat([[4, 2], [2, 1]])
    j = math_Jacobi(a)
    assert j.IsDone()
    for i in (1, 2):
        v = math_Vector(1, 2)
        j.Vector(i, v)
        lam = j.Value(i)
        av1 = a(1, 1) * v(1) + a(1, 2) * v(2)
        av2 = a(2, 1) * v(1) + a(2, 2) * v(2)
        assert abs(av1 - lam * v(1)) <= 1e-10
        assert abs(av2 - lam * v(2)) <= 1e-10


def test_MathJacobiTest_LargerSymmetricMatrix():
    a = mat([[4, 1, 0.5, 0.2], [1, 5, 1.5, 0.3], [0.5, 1.5, 6, 2], [0.2, 0.3, 2, 3]])
    j = math_Jacobi(a)
    assert j.IsDone()
    vals = j.Values()
    assert vals.Length() == 4
    for i in range(1, 5):
        assert j.Value(i) > 0.0
    trace = a(1, 1) + a(2, 2) + a(3, 3) + a(4, 4)
    assert abs(sum(vals(i) for i in range(1, 5)) - trace) <= 1e-10


def test_MathJacobiTest_SingleElementMatrix():
    j = math_Jacobi(mat([[42.0]]))
    assert j.IsDone()
    vals = j.Values()
    assert vals.Length() == 1
    assert abs(vals(1) - 42.0) <= 1e-12
    v = math_Vector(1, 1)
    j.Vector(1, v)
    assert abs(v(1) - 1.0) <= 1e-12


def test_MathJacobiTest_SquareMatrixRequirement():
    ns = mat([[1, 2, 3], [4, 5, 6]])
    assert ns.RowNumber() != ns.ColNumber()
    assert math_Jacobi(mat([[1, 0.5], [0.5, 2]])).IsDone()


def test_MathJacobiTest_NotDoneExceptions():
    j = math_Jacobi(mat([[1, 0], [0, 1]]))
    if not j.IsDone():
        with pytest.raises(StdFail_NotDone):
            j.Values()
        with pytest.raises(StdFail_NotDone):
            j.Value(1)
        with pytest.raises(StdFail_NotDone):
            j.Vectors()
        with pytest.raises(StdFail_NotDone):
            j.Vector(1, math_Vector(1, 2))


def test_MathJacobiTest_OrthogonalityOfEigenvectors():
    j = math_Jacobi(mat([[6, 2, 1], [2, 3, 1], [1, 1, 1]]))
    assert j.IsDone()
    vs = []
    for i in (1, 2, 3):
        v = math_Vector(1, 3)
        j.Vector(i, v)
        vs.append(v)
    vals = j.Values()

    def dot(a, b):
        return sum(a(k) * b(k) for k in (1, 2, 3))

    for p, q in ((1, 2), (1, 3), (2, 3)):
        if abs(vals(p) - vals(q)) > 1e-10:
            assert abs(dot(vs[p - 1], vs[q - 1])) <= 1e-10


def test_MathJacobiTest_NormalizationOfEigenvectors():
    j = math_Jacobi(mat([[2, 1, 0], [1, 2, 1], [0, 1, 2]]))
    assert j.IsDone()
    for i in (1, 2, 3):
        v = math_Vector(1, 3)
        j.Vector(i, v)
        assert abs(math.sqrt(v(1) ** 2 + v(2) ** 2 + v(3) ** 2) - 1.0) <= 1e-10


def test_MathJacobiTest_CustomBounds():
    j = math_Jacobi(mat([[5, 1], [1, 3]], lo_r=2, lo_c=2))
    assert j.IsDone()
    vals = j.Values()
    assert vals.Length() == 2
    assert vals(1) > 0.0
    assert vals(2) > 0.0
