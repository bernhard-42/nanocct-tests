# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathLin_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
import random

from nanocct import MathLin, MathUtils
from nanocct.math import (
    math_GaussLeastSquare,
    math_Householder,
    math_Jacobi,
    math_Matrix,
    math_SVD,
    math_Vector,
)

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


def create_identity(n):
    m = math_Matrix(1, n, 1, n, 0.0)
    for i in range(1, n + 1):
        m[i, i] = 1.0
    return m


def create_spd(n):
    m = math_Matrix(1, n, 1, n, 0.0)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            m[i, j] = 1.0 / (i + j - 1)
        m[i, i] = m(i, i) + float(n)
    return m


def create_random(m_rows, n_cols, seed=42):
    rng = random.Random(seed)
    m = math_Matrix(1, m_rows, 1, n_cols)
    for i in range(1, m_rows + 1):
        for j in range(1, n_cols + 1):
            m[i, j] = rng.random() * 2.0 - 1.0
    return m


def vector_norm(v):
    return math.sqrt(sum(v(i) * v(i) for i in range(v.Lower(), v.Upper() + 1)))


def matmul(a, b):
    am, an, ak = a.RowNumber(), b.ColNumber(), a.ColNumber()
    r = math_Matrix(1, am, 1, an, 0.0)
    for i in range(1, am + 1):
        for j in range(1, an + 1):
            r[i, j] = sum(a(i, k) * b(k, j) for k in range(1, ak + 1))
    return r


def transpose(m):
    rm, rn = m.RowNumber(), m.ColNumber()
    r = math_Matrix(1, rn, 1, rm)
    for i in range(1, rm + 1):
        for j in range(1, rn + 1):
            r[j, i] = m(i, j)
    return r


def assert_matrix_near(a, b, rows, cols, tol):
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            assert near(a(i, j), b(i, j), tol), (i, j, a(i, j), b(i, j))


# SVD tests


def test_MathLin_SVD_Test_BasicDecomposition_2x2():
    a = mat([[3.0, 2.0], [2.0, 3.0]])
    res = MathLin.SVD(a)
    assert res.IsDone()
    assert res.Rank == 2
    u, s, v = res.U, res.SingularValues, res.V
    sigma = math_Matrix(1, 2, 1, 2, 0.0)
    sigma[1, 1] = s(1)
    sigma[2, 2] = s(2)
    rec = matmul(matmul(u, sigma), transpose(v))
    assert_matrix_near(rec, a, 2, 2, THE_TOLERANCE)


def test_MathLin_SVD_Test_SingularValues():
    a = mat([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    res = MathLin.SVD(a)
    assert res.IsDone()
    s = res.SingularValues
    for i in range(s.Lower(), s.Upper()):
        assert s(i) >= 0.0
        assert s(i) >= s(i + 1)
    assert res.Rank <= 2


def test_MathLin_SVD_Test_SolveSystem():
    a = mat([[3, 1], [1, 2]])
    b = vec([9, 8])
    res = MathLin.SolveSVD(a, b)
    assert res.IsDone()
    x = res.Solution
    assert near(a(1, 1) * x(1) + a(1, 2) * x(2), b(1), THE_TOLERANCE)
    assert near(a(2, 1) * x(1) + a(2, 2) * x(2), b(2), THE_TOLERANCE)


def test_MathLin_SVD_Test_PseudoInverse():
    a = mat([[1, 2], [3, 4]])
    pinv = MathLin.PseudoInverse(a)
    assert pinv.IsDone()
    check = matmul(matmul(a, pinv.Inverse), a)
    assert_matrix_near(check, a, 2, 2, THE_TOLERANCE)


def test_MathLin_SVD_Test_ConditionNumber():
    assert near(MathLin.ConditionNumber(create_identity(3)), 1.0, THE_TOLERANCE)
    hilbert = math_Matrix(1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            hilbert[i, j] = 1.0 / (i + j - 1)
    assert MathLin.ConditionNumber(hilbert) > 100.0


# Multi-RHS linear solve tests


def test_MathLin_Gauss_Test_SolveMultiple_ReturnsFullMatrix():
    a = mat([[4, 1, 2], [0, 3, 1], [2, 1, 5]])
    x_exp = mat([[1.0, -2.0], [2.0, 0.5], [-1.0, 3.0]])
    b = matmul(a, x_exp)
    res = MathLin.SolveMultiple(a, b)
    assert res.IsDone()
    assert res.Solutions is not None
    x = res.Solutions
    assert_matrix_near(x, x_exp, 3, 2, THE_TOLERANCE)
    assert_matrix_near(matmul(a, x), b, 3, 2, THE_TOLERANCE)


def test_MathLin_Gauss_Test_SolveMultiple_DimensionMismatch():
    a = create_identity(3)
    b_wrong = math_Matrix(1, 2, 1, 1, 0.0)
    res = MathLin.SolveMultiple(a, b_wrong)
    assert res.Status == MathUtils.Status.InvalidInput


def test_MathLin_Householder_Test_SolveQRMultiple_ReturnsFullMatrix():
    a = mat([[1, 2], [3, 1], [-1, 1]])
    x_exp = mat([[2.0, -0.5], [-1.0, 3.0]])
    b = matmul(a, x_exp)
    res = MathLin.SolveQRMultiple(a, b)
    assert res.IsDone()
    assert res.Solutions is not None
    x = res.Solutions
    assert_matrix_near(x, x_exp, 2, 2, THE_TOLERANCE)
    assert_matrix_near(matmul(a, x), b, 3, 2, THE_TOLERANCE)


def test_MathLin_Householder_Test_SolveQRMultiple_DimensionMismatch():
    a = math_Matrix(1, 3, 1, 2, 0.0)
    a[1, 1] = 1.0
    a[2, 2] = 1.0
    b_wrong = math_Matrix(1, 2, 1, 2, 0.0)
    res = MathLin.SolveQRMultiple(a, b_wrong)
    assert res.Status == MathUtils.Status.InvalidInput


# Householder QR tests


def test_MathLin_Householder_Test_BasicQR_2x2():
    a = mat([[1, 2], [3, 4]])
    res = MathLin.QR(a)
    assert res.IsDone()
    q, r = res.Q, res.R
    assert_matrix_near(matmul(q, transpose(q)), create_identity(2), 2, 2, THE_TOLERANCE)
    assert near(r(2, 1), 0.0, THE_TOLERANCE)
    assert_matrix_near(matmul(q, r), a, 2, 2, THE_TOLERANCE)


def test_MathLin_Householder_Test_SolveSystem():
    a = mat([[3, 1], [1, 2]])
    b = vec([9, 8])
    res = MathLin.SolveQR(a, b)
    assert res.IsDone()
    x = res.Solution
    assert near(a(1, 1) * x(1) + a(1, 2) * x(2), b(1), THE_TOLERANCE)
    assert near(a(2, 1) * x(1) + a(2, 2) * x(2), b(2), THE_TOLERANCE)


def test_MathLin_Householder_Test_Overdetermined():
    a = mat([[1, 1], [1, 2], [1, 3]])
    b = vec([1, 2, 3])
    res = MathLin.SolveQR(a, b)
    assert res.IsDone()
    assert res.Solution.Length() == 2


# Jacobi eigenvalue tests


def test_MathLin_Jacobi_Test_Eigenvalues_Diagonal():
    a = math_Matrix(1, 3, 1, 3, 0.0)
    a[1, 1] = 3.0
    a[2, 2] = 1.0
    a[3, 3] = 2.0
    res = MathLin.Jacobi(a, True)
    assert res.IsDone()
    ev = res.EigenValues
    assert near(ev(1), 3.0, THE_TOLERANCE)
    assert near(ev(2), 2.0, THE_TOLERANCE)
    assert near(ev(3), 1.0, THE_TOLERANCE)


def test_MathLin_Jacobi_Test_Eigenvalues_Symmetric():
    a = mat([[3, 1], [1, 3]])
    res = MathLin.Jacobi(a, True)
    assert res.IsDone()
    ev = res.EigenValues
    assert near(ev(1), 4.0, THE_TOLERANCE)
    assert near(ev(2), 2.0, THE_TOLERANCE)


def test_MathLin_Jacobi_Test_EigenvectorsOrthogonal():
    a = create_spd(3)
    res = MathLin.Jacobi(a, False)
    assert res.IsDone()
    v = res.EigenVectors
    assert_matrix_near(matmul(transpose(v), v), create_identity(3), 3, 3, 1.0e-8)


def test_MathLin_Jacobi_Test_SpectralDecomposition():
    a = create_spd(3)
    res = MathLin.SpectralDecomposition(a)
    assert res.IsDone()
    d, v = res.EigenValues, res.EigenVectors
    diag = math_Matrix(1, 3, 1, 3, 0.0)
    for i in range(1, 4):
        diag[i, i] = d(i)
    rec = matmul(matmul(v, diag), transpose(v))
    assert_matrix_near(rec, a, 3, 3, 1.0e-8)


def test_MathLin_Jacobi_Test_MatrixSqrt():
    a = create_spd(2)
    sq = MathLin.MatrixSqrt(a)
    assert sq is not None
    assert_matrix_near(matmul(sq, sq), a, 2, 2, 1.0e-8)


# Least squares tests


def test_MathLin_LeastSquares_Test_SquareSystem():
    a = mat([[3, 1], [1, 2]])
    b = vec([9, 8])
    res = MathLin.LeastSquares(a, b, MathLin.LeastSquaresMethod.QR)
    assert res.IsDone()
    assert res.Residual < THE_TOLERANCE


def test_MathLin_LeastSquares_Test_Overdetermined():
    a = mat([[1, 1], [1, 2], [1, 3], [1, 4]])
    b = vec([2, 3, 4, 5])
    res = MathLin.LeastSquares(a, b, MathLin.LeastSquaresMethod.QR)
    assert res.IsDone()
    x = res.Solution
    assert near(x(1), 1.0, THE_TOLERANCE)
    assert near(x(2), 1.0, THE_TOLERANCE)
    assert res.Residual < THE_TOLERANCE


def test_MathLin_LeastSquares_Test_MethodComparison():
    # C++ uses srand(42)/rand(); any random matrix serves the comparison
    a = create_random(5, 3)
    b = vec([1, 2, 3, 4, 5])
    ne = MathLin.LeastSquares(a, b, MathLin.LeastSquaresMethod.NormalEquations)
    qr = MathLin.LeastSquares(a, b, MathLin.LeastSquaresMethod.QR)
    svd = MathLin.LeastSquares(a, b, MathLin.LeastSquaresMethod.SVD)
    assert ne.IsDone()
    assert qr.IsDone()
    assert svd.IsDone()
    for i in range(1, 4):
        assert near(ne.Solution(i), qr.Solution(i), 1.0e-6)
        assert near(qr.Solution(i), svd.Solution(i), 1.0e-6)


def test_MathLin_LeastSquares_Test_WeightedLeastSquares():
    a = mat([[1, 1], [1, 2], [1, 3]])
    b = vec([2.0, 3.0, 4.5])
    w1 = math_Vector(1, 3, 1.0)
    res1 = MathLin.WeightedLeastSquares(a, b, w1)
    w2 = vec([10.0, 10.0, 0.1])
    res2 = MathLin.WeightedLeastSquares(a, b, w2)
    assert res1.IsDone()
    assert res2.IsDone()
    assert res1.Solution(1) != res2.Solution(1)


def test_MathLin_LeastSquares_Test_RegularizedLeastSquares():
    a = math_Matrix(1, 3, 1, 3)
    for i in range(1, 4):
        for j in range(1, 4):
            a[i, j] = 1.0 / (i + j - 1)
    b = vec([1.0, 0.5, 0.333])
    no_reg = MathLin.LeastSquares(a, b)
    reg = MathLin.RegularizedLeastSquares(a, b, 0.01)
    assert no_reg.IsDone()
    assert reg.IsDone()
    assert vector_norm(reg.Solution) < vector_norm(no_reg.Solution)


# Comparison with old API tests


def test_MathLin_Test_CompareWithOldAPI_SVD():
    a = mat([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
    b = vec([1, 2, 3])
    old_svd = math_SVD(a)
    old_sol = math_Vector(1, 3)
    old_svd.Solve(b, old_sol)
    new = MathLin.SolveSVD(a, b)
    assert old_svd.IsDone()
    assert new.IsDone()
    for i in range(1, 4):
        assert near(old_sol(i), new.Solution(i), 1.0e-8)


def test_MathLin_Test_CompareWithOldAPI_Householder():
    a = mat([[1, 1], [1, 2], [1, 3]])
    b = vec([2, 3, 4])
    b_mat = mat([[2], [3], [4]])
    old_hh = math_Householder(a, b_mat)
    new = MathLin.SolveQR(a, b)
    assert old_hh.IsDone()
    assert new.IsDone()
    old_sol = math_Vector(1, 2)
    old_hh.Value(old_sol, 1)
    for i in range(1, 3):
        assert near(old_sol(i), new.Solution(i), 1.0e-8)


def test_MathLin_Test_CompareWithOldAPI_Jacobi():
    a = mat([[3, 1, 0], [1, 3, 1], [0, 1, 3]])
    old = math_Jacobi(a)
    new = MathLin.Jacobi(a, True)
    assert old.IsDone()
    assert new.IsDone()
    ev = new.EigenValues
    for i in range(1, 4):
        assert near(old.Value(i), ev(i), 1.0e-8)


def test_MathLin_Test_CompareWithOldAPI_GaussLeastSquare():
    a = mat([[1, 1], [1, 2], [1, 3], [1, 4]])
    b = vec([2, 3, 4, 5])
    old = math_GaussLeastSquare(a)
    old_sol = math_Vector(1, 2)
    old.Solve(b, old_sol)
    new = MathLin.LeastSquares(a, b)
    assert old.IsDone()
    assert new.IsDone()
    for i in range(1, 3):
        assert near(old_sol(i), new.Solution(i), 1.0e-8)
