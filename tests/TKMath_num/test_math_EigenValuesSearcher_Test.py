# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_EigenValuesSearcher_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
import sys

from nanocct.math import math_EigenValuesSearcher
from nanocct.NCollection import NCollection_Array1

CONFUSION = 1e-7
EPS = sys.float_info.epsilon


def arr(values):
    a = NCollection_Array1[float](1, len(values))
    for i, v in enumerate(values):
        a.SetValue(i + 1, float(v))
    return a


def tridiag(diag, sub):
    n = len(diag)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        m[i][i] = diag[i]
    for i in range(1, n):
        m[i][i - 1] = sub[i]
        m[i - 1][i] = sub[i]
    return m


def search(diag, sub):
    return math_EigenValuesSearcher(arr(diag), arr(sub))


def comps(v):
    return [v(i) for i in range(1, v.Length() + 1)]


def verify_pair(m, lam, v, tol=1e-12):
    x = comps(v)
    n = len(m)
    for i in range(n):
        s = sum(m[i][j] * x[j] for j in range(n))
        if abs(s - lam * x[i]) > tol:
            return False
    return True


def orthogonal(a, b, tol=1e-12):
    return abs(sum(p * q for p, q in zip(comps(a), comps(b)))) < tol


def norm(v):
    return math.sqrt(sum(x * x for x in comps(v)))


def check_pairs(diag, sub, tol, norm_tol=None, ortho_tol=None):
    s = search(diag, sub)
    assert s.IsDone()
    m = tridiag(diag, sub)
    n = len(diag)
    for i in range(1, n + 1):
        v = s.EigenVector(i)
        assert verify_pair(m, s.EigenValue(i), v, tol)
        if norm_tol is not None:
            assert abs(norm(v) - 1.0) <= norm_tol
    if ortho_tol is not None:
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                assert orthogonal(s.EigenVector(i), s.EigenVector(j), ortho_tol)
    return s


def sorted_values(s, n):
    return sorted(s.EigenValue(i) for i in range(1, n + 1))


def test_math_EigenValuesSearcherTest_ConstructorDimensionMismatch():
    assert not search([1, 2, 3], [0.5, 1.5]).IsDone()


def test_math_EigenValuesSearcherTest_OneByOneMatrix():
    s = search([5.0], [0.0])
    assert s.IsDone()
    assert s.Dimension() == 1
    assert abs(s.EigenValue(1) - 5.0) <= CONFUSION
    v = s.EigenVector(1)
    assert v.Length() == 1
    assert abs(v(1) - 1.0) <= CONFUSION


def test_math_EigenValuesSearcherTest_TwoByTwoMatrix():
    s = check_pairs([2, 3], [0, 1], 1e-10, 1e-10, 1e-10)
    assert s.Dimension() == 2
    ev = sorted_values(s, 2)
    assert abs(ev[0] - (2.5 - 0.5 * math.sqrt(5.0))) <= 1e-10
    assert abs(ev[1] - (2.5 + 0.5 * math.sqrt(5.0))) <= 1e-10


def test_math_EigenValuesSearcherTest_ThreeByThreeMatrix():
    s = check_pairs([4, 4, 4], [0, 1, 1], 1e-10, 1e-10, 1e-10)
    assert s.Dimension() == 3


def test_math_EigenValuesSearcherTest_DiagonalMatrix():
    s = search([1, 2, 3, 4], [0, 0, 0, 0])
    assert s.IsDone()
    assert s.Dimension() == 4
    for got, exp in zip(sorted_values(s, 4), (1.0, 2.0, 3.0, 4.0)):
        assert abs(got - exp) <= CONFUSION


def test_math_EigenValuesSearcherTest_IdentityMatrix():
    s = search([1, 1, 1], [0, 0, 0])
    assert s.IsDone()
    assert s.Dimension() == 3
    for i in (1, 2, 3):
        assert abs(s.EigenValue(i) - 1.0) <= CONFUSION


def test_math_EigenValuesSearcherTest_NegativeEigenvalues():
    s = check_pairs([-1, -1], [0, 2], 1e-10)
    ev = sorted_values(s, 2)
    assert abs(ev[0] + 3.0) <= 1e-10
    assert abs(ev[1] - 1.0) <= 1e-10


def test_math_EigenValuesSearcherTest_FiveByFiveMatrix():
    s = check_pairs([2.0] * 5, [0, -1, -1, -1, -1], 1e-9, 1e-9)
    assert s.Dimension() == 5
    for i in range(1, 6):
        assert 0.0 <= s.EigenValue(i) <= 4.0


def test_math_EigenValuesSearcherTest_SmallSubdiagonalElements():
    s = search([1, 2, 3], [0, 1e-14, 1e-14])
    assert s.IsDone()
    for got, exp in zip(sorted_values(s, 3), (1.0, 2.0, 3.0)):
        assert abs(got - exp) <= 1e-10


def test_math_EigenValuesSearcherTest_ZeroDiagonalElements():
    s = search([0, 0, 0], [0, 1, 1])
    assert s.IsDone()
    assert s.Dimension() == 3
    for got, exp in zip(sorted_values(s, 3), (-math.sqrt(2.0), 0.0, math.sqrt(2.0))):
        assert abs(got - exp) <= 1e-10


def test_math_EigenValuesSearcherTest_LargeDiagonalElements():
    check_pairs([1e6, 2e6, 3e6], [0, 1e3, 2e3], 1e-6, 1e-10)


def test_math_EigenValuesSearcherTest_AlternatingPattern():
    check_pairs([1, -1, 1, -1], [0, 0.5, -0.5, 0.5], 1e-10)


def test_math_EigenValuesSearcherTest_RepeatedEigenvalues():
    s = search([2, 2, 2, 2], [0, 0, 0, 0])
    assert s.IsDone()
    for i in range(1, 5):
        assert abs(s.EigenValue(i) - 2.0) <= CONFUSION


def test_math_EigenValuesSearcherTest_VerySmallElements():
    check_pairs([1e-10, 2e-10, 3e-10], [0, 1e-11, 2e-11], 1e-18, 1e-12)


def test_math_EigenValuesSearcherTest_AntisymmetricSubdiagonal():
    check_pairs([1, 2, 3, 4, 5], [0, 1, -2, 1, -2], 1e-9, None, 1e-9)


def test_math_EigenValuesSearcherTest_WilkinsonMatrix():
    n = 5
    m = (n - 1) // 2
    check_pairs([abs(i - 1 - m) for i in range(1, n + 1)], [0.0] + [1.0] * (n - 1), 1e-9, 1e-9)


def test_math_EigenValuesSearcherTest_MixedSignDiagonal():
    diag = [-2, 1, -1, 3]
    s = check_pairs(diag, [0, 1.5, 0.8, -0.6], 1e-9)
    assert abs(sum(s.EigenValue(i) for i in range(1, 5)) - sum(diag)) <= 1e-9


def test_math_EigenValuesSearcherTest_LargerMatrix():
    n = 8
    diag = [float(i * i) for i in range(1, n + 1)]
    sub = [0.0] + [(-1.0 if i % 3 == 0 else 1.0) * math.sqrt(i) for i in range(2, n + 1)]
    check_pairs(diag, sub, 1e-8, 1e-8, 1e-8)


def test_math_EigenValuesSearcherTest_RationalNumberPattern():
    check_pairs([1.0 / 3.0, 2.0 / 3.0, 1.0, 4.0 / 3.0], [0, 1.0 / 6.0, 1.0 / 4.0, 1.0 / 5.0], 1e-12, 1e-12)


def test_math_EigenValuesSearcherTest_NearDegenerateEigenvalues():
    diag = [1.0, 1.0 + 1e-8, 1.0 + 2e-8]
    s = check_pairs(diag, [0, 1e-10, 1e-10], 1e-9)
    for got, exp in zip(sorted_values(s, 3), diag):
        assert abs(got - exp) <= 1e-7


def test_math_EigenValuesSearcherTest_DeflationConditionPrecision():
    s = check_pairs([1e6, 2e6, 3e6, 4e6], [0, 1e-15, 2e-15, 3e-15], 1e-9)
    for got, exp in zip(sorted_values(s, 4), (1e6, 2e6, 3e6, 4e6)):
        assert abs(got - exp) <= 1e3


def test_math_EigenValuesSearcherTest_ExactZeroSubdiagonal():
    check_pairs([1, 4, 9, 16, 25], [0, 1, 0, 2, 0], 1e-12)


def test_math_EigenValuesSearcherTest_ConvergenceBehavior():
    check_pairs([i * 0.1 for i in range(1, 7)], [0.0] + [0.99] * 5, 1e-9)


def test_math_EigenValuesSearcherTest_NumericalStability():
    s = search([1e-100, 1e100, 1e-50], [0, 1e-75, 1e75])
    assert s.IsDone()
    for i in (1, 2, 3):
        lam = s.EigenValue(i)
        assert math.isfinite(lam)
        v = s.EigenVector(i)
        for j in (1, 2, 3):
            assert math.isfinite(v(j))


def test_math_EigenValuesSearcherTest_WilkinsonShiftAccuracy():
    check_pairs([1.0, 2.0, 1.0000001], [0, 1.0, 0.0000001], 1e-10)


def test_math_EigenValuesSearcherTest_ZeroRadiusHandling():
    check_pairs([0, 0, 1, 1], [0, 1e-16, 1e-16, 0], 1e-12)


def test_math_EigenValuesSearcherTest_PathologicalEqualElements():
    check_pairs([42.0] * 5, [0.0] + [42.0] * 4, 1e-9)


def test_math_EigenValuesSearcherTest_IncreasingSubdiagonal():
    check_pairs([1.0] * 6, [0.0] + [(i - 1) * 0.1 for i in range(2, 7)], 1e-10, 1e-10, 1e-10)


def test_math_EigenValuesSearcherTest_DeflationConditionSemantics():
    d1, d2 = 1e8, 2e8
    meps = d1 * EPS
    diag_sum = abs(d1) + abs(d2)
    assert meps + diag_sum == diag_sum
    check_pairs([d1, d2, 3e8], [0, meps, meps * 0.5], 1e-6)


def test_math_EigenValuesSearcherTest_DeflationBoundaryCondition():
    diag = [1.0, 1000.0, 1e-6, 1e6]
    sub = [0.0] + [(abs(diag[i - 1]) + abs(diag[i])) * EPS * 0.1 for i in (1, 2, 3)]
    s = check_pairs(diag, sub, 1e-9)
    for i in range(1, 5):
        assert math.isfinite(s.EigenValue(i))
