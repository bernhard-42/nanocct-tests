# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathLin_EigenSearch_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
import random

from nanocct import MathLin
from nanocct.math import math_EigenValuesSearcher, math_Matrix, math_Vector
from nanocct.NCollection import NCollection_Array1

THE_EIGEN_TOL = 1.0e-10
THE_RESIDUAL_TOL = 1.0e-10
THE_ORTHOGONAL_TOL = 1.0e-10
THE_NORMALIZED_TOL = 1.0e-10
THE_RANDOM_NB_CASES = 120


def build_symmetric_tridiagonal(diag, subdiag):
    n = diag.Length()
    m = math_Matrix(1, n, 1, n, 0.0)
    for i in range(1, n + 1):
        m[i, i] = diag(diag.Lower() + i - 1)
    for i in range(2, n + 1):
        e = subdiag(subdiag.Lower() + i - 1)
        m[i, i - 1] = e
        m[i - 1, i] = e
    return m


def build_legacy_arrays(diag, subdiag):
    n = diag.Length()
    d = NCollection_Array1[float](1, n)
    s = NCollection_Array1[float](1, n)
    for i in range(1, n + 1):
        d[i] = diag(diag.Lower() + i - 1)
        s[i] = subdiag(subdiag.Lower() + i - 1)
    return d, s


def sorted_legacy(legacy):
    return sorted(legacy.EigenValue(i) for i in range(1, legacy.Dimension() + 1))


def sorted_modern(modern):
    eig = modern.EigenValues
    if eig is None:
        return []
    return sorted(eig(i) for i in range(eig.Lower(), eig.Upper() + 1))


def vector_norm2(v):
    return math.sqrt(sum(v(i) * v(i) for i in range(v.Lower(), v.Upper() + 1)))


def pair_residual_infinity(m, lam, v):
    n = m.RowNumber()
    worst = 0.0
    for i in range(1, n + 1):
        ax = sum(m(i, j) * v(j) for j in range(1, n + 1))
        worst = max(worst, abs(ax - lam * v(i)))
    return worst


def dot(v1, v2):
    return sum(v1(i) * v2(i) for i in range(1, v1.Length() + 1))


def test_MathLin_EigenSearch_Test_BasicParityWithLegacy_3x3():
    diag = math_Vector(1, 3)
    sub = math_Vector(1, 3)
    for i, (d, s) in enumerate([(4.0, 0.0), (4.0, 1.0), (4.0, 1.0)], 1):
        diag[i] = d
        sub[i] = s
    d_leg, s_leg = build_legacy_arrays(diag, sub)
    legacy = math_EigenValuesSearcher(d_leg, s_leg)
    modern = MathLin.EigenTridiagonal(diag, sub)
    assert legacy.IsDone()
    assert modern.IsDone()
    assert modern.EigenValues is not None
    assert modern.EigenVectors is not None
    ls, ms = sorted_legacy(legacy), sorted_modern(modern)
    assert len(ls) == len(ms)
    for a, b in zip(ls, ms):
        assert abs(a - b) <= THE_EIGEN_TOL
    a = build_symmetric_tridiagonal(diag, sub)
    vals = modern.EigenValues
    for i in range(1, 4):
        v = MathLin.GetEigenVector(modern, i)
        assert abs(vector_norm2(v) - 1.0) <= THE_NORMALIZED_TOL
        assert pair_residual_infinity(a, vals(i), v) <= THE_RESIDUAL_TOL


def test_MathLin_EigenSearch_Test_HandlesNonOneLowerBounds():
    diag = math_Vector(-2, 2)
    sub = math_Vector(-2, 2)
    values = {-2: (1.0, 0.0), -1: (3.0, 0.3), 0: (-2.0, -0.2), 1: (5.0, 0.7), 2: (4.0, -1.1)}
    d_leg = NCollection_Array1[float](-2, 2)
    s_leg = NCollection_Array1[float](-2, 2)
    for i, (d, s) in values.items():
        diag[i] = d
        sub[i] = s
        d_leg[i] = d
        s_leg[i] = s
    legacy = math_EigenValuesSearcher(d_leg, s_leg)
    modern = MathLin.EigenTridiagonal(diag, sub)
    assert legacy.IsDone() == modern.IsDone()
    assert legacy.IsDone()
    ls, ms = sorted_legacy(legacy), sorted_modern(modern)
    assert len(ls) == len(ms)
    for a, b in zip(ls, ms):
        assert abs(a - b) <= THE_EIGEN_TOL


def test_MathLin_EigenSearch_Test_RandomParityAndOrthogonality():
    # C++ draws from std::mt19937(123456u); the draws differ here, the checks are the same
    rng = random.Random(123456)
    for case in range(THE_RANDOM_NB_CASES):
        n = rng.randint(2, 32)
        diag = math_Vector(1, n)
        sub = math_Vector(1, n)
        for i in range(1, n + 1):
            diag[i] = rng.uniform(-100.0, 100.0)
            sub[i] = 0.0 if i == 1 else rng.uniform(-100.0, 100.0)
        d_leg, s_leg = build_legacy_arrays(diag, sub)
        legacy = math_EigenValuesSearcher(d_leg, s_leg)
        modern = MathLin.EigenTridiagonal(diag, sub)
        assert legacy.IsDone() == modern.IsDone(), case
        if not legacy.IsDone():
            continue
        assert modern.EigenValues is not None, case
        assert modern.EigenVectors is not None, case
        ls, ms = sorted_legacy(legacy), sorted_modern(modern)
        assert len(ls) == len(ms), case
        for a, b in zip(ls, ms):
            assert abs(a - b) <= THE_EIGEN_TOL, case
        a = build_symmetric_tridiagonal(diag, sub)
        vals = modern.EigenValues
        vecs = [MathLin.GetEigenVector(modern, i) for i in range(1, n + 1)]
        for i in range(1, n + 1):
            v = vecs[i - 1]
            assert abs(vector_norm2(v) - 1.0) <= THE_NORMALIZED_TOL, case
            assert pair_residual_infinity(a, vals(i), v) <= THE_RESIDUAL_TOL, case
        for i in range(n):
            for j in range(i + 1, n):
                assert abs(dot(vecs[i], vecs[j])) <= THE_ORTHOGONAL_TOL, case
