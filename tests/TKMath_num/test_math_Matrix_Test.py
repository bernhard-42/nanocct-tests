# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_Matrix_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_Matrix, math_Vector

CONF = 1e-7


def check_matrices_equal(m1, m2, tol=CONF):
    assert m1.RowNumber() == m2.RowNumber()
    assert m1.ColNumber() == m2.ColNumber()
    assert m1.LowerRow() == m2.LowerRow()
    assert m1.LowerCol() == m2.LowerCol()
    for i in range(m1.LowerRow(), m1.UpperRow() + 1):
        for j in range(m1.LowerCol(), m1.UpperCol() + 1):
            assert abs(m1(i, j) - m2(i, j)) <= tol


def mat(rows):
    """1-based matrix from a list of rows."""
    m = math_Matrix(1, len(rows), 1, len(rows[0]))
    for i, row in enumerate(rows, start=1):
        for j, x in enumerate(row, start=1):
            m[i, j] = x
    return m


def all_equal(m, value):
    for i in range(m.LowerRow(), m.UpperRow() + 1):
        for j in range(m.LowerCol(), m.UpperCol() + 1):
            assert m(i, j) == value


def test_MathMatrixTest_Constructors():
    m1 = math_Matrix(1, 3, 1, 4)
    assert m1.RowNumber() == 3
    assert m1.ColNumber() == 4
    assert m1.LowerRow() == 1
    assert m1.UpperRow() == 3
    assert m1.LowerCol() == 1
    assert m1.UpperCol() == 4

    m2 = math_Matrix(2, 4, 3, 5, 2.5)
    assert m2.RowNumber() == 3
    assert m2.ColNumber() == 3
    for i in range(2, 5):
        for j in range(3, 6):
            assert m2(i, j) == 2.5

    m3 = math_Matrix(m2)
    check_matrices_equal(m2, m3)


def test_MathMatrixTest_InitAndAccess():
    m = math_Matrix(1, 3, 1, 3)
    m.Init(5.0)
    all_equal(m, 5.0)

    m[2, 2] = 10.0
    assert m(2, 2) == 10.0

    m.SetValue(3, 3, 15.0)
    assert m(3, 3) == 15.0


def test_MathMatrixTest_MatrixOperations():
    m1 = math_Matrix(1, 3, 1, 3)
    m2 = math_Matrix(1, 3, 1, 3)
    m1.Init(2.0)
    m2.Init(3.0)

    all_equal(m1.Added(m2), 5.0)
    all_equal(m1.Subtracted(m2), -1.0)
    all_equal(m1.Multiplied(2.5), 5.0)
    all_equal(m1.Divided(0.5), 4.0)

    a = math_Matrix(1, 3, 1, 3)
    a.Init(3.0)
    a.Multiply(2.0)
    all_equal(a, 6.0)

    b = math_Matrix(1, 3, 1, 3)
    b.Init(2.0)
    b *= 3.0
    all_equal(b, 6.0)


def test_MathMatrixTest_MatrixMultiplication():
    ident = math_Matrix(1, 3, 1, 3)
    ident.Init(0.0)
    ident[1, 1] = 1.0
    ident[2, 2] = 1.0
    ident[3, 3] = 1.0

    m = math_Matrix(1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            m[i, j] = i + j
    check_matrices_equal(m.Multiplied(ident), m)

    a = mat([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    b = mat([[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]])
    c = a.Multiplied(b)
    assert c(1, 1) == 1 * 7 + 2 * 9 + 3 * 11
    assert c(1, 2) == 1 * 8 + 2 * 10 + 3 * 12
    assert c(2, 1) == 4 * 7 + 5 * 9 + 6 * 11
    assert c(2, 2) == 4 * 8 + 5 * 10 + 6 * 12

    p1 = mat([[1.0, 2.0], [3.0, 4.0]])
    p2 = mat([[2.0, 0.0], [1.0, 3.0]])
    orig = math_Matrix(p1)
    p1.Multiply(p2)
    assert p1(1, 1) == 4
    assert p1(1, 2) == 6
    assert p1(2, 1) == 10
    assert p1(2, 2) == 12

    op = math_Matrix(orig)
    op *= p2
    assert op(1, 1) == 4
    assert op(1, 2) == 6
    assert op(2, 1) == 10
    assert op(2, 2) == 12


def test_MathMatrixTest_TransposeAndInverse():
    m = mat([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    t = m.Transposed()
    assert t.RowNumber() == m.ColNumber()
    assert t.ColNumber() == m.RowNumber()
    assert t(1, 1) == m(1, 1)
    assert t(2, 1) == m(1, 2)
    assert t(3, 1) == m(1, 3)
    assert t(1, 2) == m(2, 1)
    assert t(2, 2) == m(2, 2)
    assert t(3, 2) == m(2, 3)

    inv_able = mat([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 4.0]])
    inv = inv_able.Inverse()
    assert inv(1, 1) == 1.0
    assert inv(2, 2) == 0.5
    assert inv(3, 3) == 0.25

    ident = inv_able.Multiplied(inv)
    for i in range(1, 4):
        for j in range(1, 4):
            expected = 1.0 if i == j else 0.0
            assert abs(ident(i, j) - expected) <= CONF


def test_MathMatrixTest_Determinant():
    ident = math_Matrix(1, 3, 1, 3)
    ident.Init(0.0)
    ident[1, 1] = 1.0
    ident[2, 2] = 1.0
    ident[3, 3] = 1.0
    assert abs(ident.Determinant() - 1.0) <= CONF

    diag = math_Matrix(1, 3, 1, 3)
    diag.Init(0.0)
    diag[1, 1] = 2.0
    diag[2, 2] = 3.0
    diag[3, 3] = 4.0
    assert abs(diag.Determinant() - 24.0) <= CONF

    m = mat([[3.0, 8.0, 5.0], [6.0, 2.0, 7.0], [4.0, 1.0, 9.0]])
    assert abs(m.Determinant() - (-185.0)) <= CONF


def test_MathMatrixTest_RowAndColumnOperations():
    m = mat([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    row = m.Row(2)
    assert row.Length() == 3
    assert (row(1), row(2), row(3)) == (4.0, 5.0, 6.0)

    col = m.Col(3)
    assert col.Length() == 3
    assert (col(1), col(2), col(3)) == (3.0, 6.0, 9.0)

    new_row = math_Vector(1, 3)
    new_row[1] = 10.0
    new_row[2] = 11.0
    new_row[3] = 12.0
    m.SetRow(2, new_row)
    assert (m(2, 1), m(2, 2), m(2, 3)) == (10.0, 11.0, 12.0)

    new_col = math_Vector(1, 3)
    new_col[1] = 13.0
    new_col[2] = 14.0
    new_col[3] = 15.0
    m.SetCol(1, new_col)
    assert (m(1, 1), m(2, 1), m(3, 1)) == (13.0, 14.0, 15.0)

    m.SwapRow(1, 3)
    assert (m(1, 1), m(1, 2), m(1, 3)) == (15.0, 8.0, 9.0)
    assert (m(3, 1), m(3, 2), m(3, 3)) == (13.0, 2.0, 3.0)

    m.SwapCol(2, 3)
    assert (m(1, 2), m(1, 3)) == (9.0, 8.0)
    assert (m(2, 2), m(2, 3)) == (12.0, 11.0)
    assert (m(3, 2), m(3, 3)) == (3.0, 2.0)


def test_MathMatrixTest_SetDiag():
    m = math_Matrix(1, 3, 1, 3)
    m.Init(0.0)
    m.SetDiag(5.0)
    for i in range(1, 4):
        for j in range(1, 4):
            assert m(i, j) == (5.0 if i == j else 0.0)


def test_MathMatrixTest_VectorMatrixOperations():
    m = mat([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    v = math_Vector(1, 3)
    v[1] = 2
    v[2] = 3
    v[3] = 4

    r = m * v
    assert r.Length() == 3
    assert r(1) == 20
    assert r(2) == 47
    assert r(3) == 74

    v1 = math_Vector(1, 2)
    v2 = math_Vector(1, 3)
    v1[1] = 1
    v1[2] = 2
    v2[1] = 3
    v2[2] = 4
    v2[3] = 5
    outer = math_Matrix(1, 2, 1, 3)
    outer.Multiply(v1, v2)
    assert outer(1, 1) == 1 * 3
    assert outer(1, 2) == 1 * 4
    assert outer(1, 3) == 1 * 5
    assert outer(2, 1) == 2 * 3
    assert outer(2, 2) == 2 * 4
    assert outer(2, 3) == 2 * 5


def test_MathMatrixTest_InPlaceMatrixMultiplication():
    m = mat([[1.0, 2.0], [3.0, 4.0]])
    m_copy = math_Matrix(m)

    correct = m_copy.Multiplied(m_copy)
    assert correct(1, 1) == 7.0
    assert correct(1, 2) == 10.0
    assert correct(2, 1) == 15.0
    assert correct(2, 2) == 22.0

    m.Multiply(m)
    check_matrices_equal(m, correct)

    m_copy *= m_copy
    check_matrices_equal(m_copy, correct)

    a = mat([[1.0, 2.0], [3.0, 4.0]])
    b = mat([[5.0, 6.0], [7.0, 8.0]])
    a_copy = math_Matrix(a)
    b_copy = math_Matrix(b)

    expected = a_copy.Multiplied(b_copy)
    assert expected(1, 1) == 19.0
    assert expected(1, 2) == 22.0
    assert expected(2, 1) == 43.0
    assert expected(2, 2) == 50.0

    a.Multiply(b)
    check_matrices_equal(a, expected)

    a_copy *= b_copy
    check_matrices_equal(a_copy, expected)
