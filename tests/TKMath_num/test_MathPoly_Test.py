# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathPoly_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import MathPoly, MathUtils

THE_TOLERANCE = 1.0e-10


def near(a, b, tol=THE_TOLERANCE):
    return abs(a - b) <= tol


def eval_cubic(a, b, c, d, x):
    return a * x * x * x + b * x * x + c * x + d


def eval_quartic(a, b, c, d, e, x):
    x2 = x * x
    return a * x2 * x2 + b * x2 * x + c * x2 + d * x + e


def check_roots(res, expected):
    assert res.IsDone()
    assert res.NbRoots == len(expected)
    roots = res.Roots
    for i, r in enumerate(expected):
        assert near(roots[i], r), (i, roots[i], r)


# Linear


def test_MathPoly_LinearTest_SimpleLinear():
    check_roots(MathPoly.Linear(2.0, 4.0), [-2.0])


def test_MathPoly_LinearTest_ZeroCoefficient_InfiniteSolutions():
    assert MathPoly.Linear(0.0, 0.0).Status == MathUtils.Status.InfiniteSolutions


def test_MathPoly_LinearTest_ZeroCoefficient_NoSolution():
    assert MathPoly.Linear(0.0, 5.0).Status == MathUtils.Status.NoSolution


# Quadratic


def test_MathPoly_QuadraticTest_TwoDistinctRoots():
    check_roots(MathPoly.Quadratic(1.0, -5.0, 6.0), [2.0, 3.0])


def test_MathPoly_QuadraticTest_DoubleRoot():
    check_roots(MathPoly.Quadratic(1.0, -4.0, 4.0), [2.0])


def test_MathPoly_QuadraticTest_NoRealRoots():
    check_roots(MathPoly.Quadratic(1.0, 0.0, 1.0), [])


def test_MathPoly_QuadraticTest_NegativeRoots():
    check_roots(MathPoly.Quadratic(1.0, 5.0, 6.0), [-3.0, -2.0])


def test_MathPoly_QuadraticTest_MixedSignRoots():
    check_roots(MathPoly.Quadratic(1.0, 0.0, -1.0), [-1.0, 1.0])


def test_MathPoly_QuadraticTest_ReducesToLinear():
    check_roots(MathPoly.Quadratic(0.0, 2.0, 4.0), [-2.0])


def test_MathPoly_QuadraticTest_LargeCoefficients():
    check_roots(MathPoly.Quadratic(1.0e6, -2.0e6, 1.0e6), [1.0])


def test_MathPoly_QuadraticTest_SmallCoefficients():
    check_roots(MathPoly.Quadratic(1.0e-6, -5.0e-6, 6.0e-6), [2.0, 3.0])


def test_MathPoly_QuadraticTest_RootsAreSorted():
    res = MathPoly.Quadratic(2.0, 3.0, -2.0)
    assert res.IsDone()
    assert res.NbRoots == 2
    assert res.Roots[0] < res.Roots[1]


# Cubic


def test_MathPoly_CubicTest_ThreeDistinctRoots():
    check_roots(MathPoly.Cubic(1.0, -6.0, 11.0, -6.0), [1.0, 2.0, 3.0])


def test_MathPoly_CubicTest_OneRealRoot():
    res = MathPoly.Cubic(1.0, 0.0, 1.0, 1.0)
    assert res.IsDone()
    assert res.NbRoots == 1
    assert near(eval_cubic(1.0, 0.0, 1.0, 1.0, res.Roots[0]), 0.0)


def test_MathPoly_CubicTest_TripleRoot():
    res = MathPoly.Cubic(1.0, -3.0, 3.0, -1.0)
    assert res.IsDone()
    assert res.NbRoots >= 1
    assert near(res.Roots[0], 1.0)


def test_MathPoly_CubicTest_OneSimpleOneDouble():
    res = MathPoly.Cubic(1.0, -5.0, 8.0, -4.0)
    assert res.IsDone()
    assert res.NbRoots >= 2
    roots = res.Roots
    for i in range(res.NbRoots):
        assert near(eval_cubic(1.0, -5.0, 8.0, -4.0, roots[i]), 0.0)


def test_MathPoly_CubicTest_ReducesToQuadratic():
    check_roots(MathPoly.Cubic(0.0, 1.0, -5.0, 6.0), [2.0, 3.0])


def test_MathPoly_CubicTest_NegativeRoots():
    check_roots(MathPoly.Cubic(1.0, 6.0, 11.0, 6.0), [-3.0, -2.0, -1.0])


def test_MathPoly_CubicTest_DepressedCubic():
    check_roots(MathPoly.Cubic(1.0, 0.0, -7.0, 6.0), [-3.0, 1.0, 2.0])


def test_MathPoly_CubicTest_RootsAreSorted():
    res = MathPoly.Cubic(1.0, -6.0, 11.0, -6.0)
    assert res.IsDone()
    roots = res.Roots
    for i in range(1, res.NbRoots):
        assert roots[i - 1] <= roots[i]


# Quartic


def test_MathPoly_QuarticTest_FourDistinctRoots():
    check_roots(MathPoly.Quartic(1.0, -10.0, 35.0, -50.0, 24.0), [1.0, 2.0, 3.0, 4.0])


def test_MathPoly_QuarticTest_TwoRealRoots():
    check_roots(MathPoly.Quartic(1.0, 0.0, -5.0, 0.0, 4.0), [-2.0, -1.0, 1.0, 2.0])


def test_MathPoly_QuarticTest_NoRealRoots():
    check_roots(MathPoly.Quartic(1.0, 0.0, 0.0, 0.0, 1.0), [])


def test_MathPoly_QuarticTest_Biquadratic():
    res = MathPoly.Quartic(1.0, 0.0, -5.0, 0.0, 4.0)
    assert res.IsDone()
    assert res.NbRoots == 4
    roots = res.Roots
    for i in range(res.NbRoots):
        assert near(eval_quartic(1.0, 0.0, -5.0, 0.0, 4.0, roots[i]), 0.0)


def test_MathPoly_QuarticTest_ReducesToCubic():
    check_roots(MathPoly.Quartic(0.0, 1.0, -6.0, 11.0, -6.0), [1.0, 2.0, 3.0])


def test_MathPoly_QuarticTest_QuadrupleRoot():
    res = MathPoly.Quartic(1.0, -8.0, 24.0, -32.0, 16.0)
    assert res.IsDone()
    assert res.NbRoots >= 1
    assert near(res.Roots[0], 2.0)


def test_MathPoly_QuarticTest_TwoDoubleRoots():
    res = MathPoly.Quartic(1.0, -8.0, 22.0, -24.0, 9.0)
    assert res.IsDone()
    assert res.NbRoots >= 2
    roots = res.Roots
    for i in range(res.NbRoots):
        assert near(eval_quartic(1.0, -8.0, 22.0, -24.0, 9.0, roots[i]), 0.0)


def test_MathPoly_QuarticTest_RootsAreSorted():
    res = MathPoly.Quartic(1.0, -10.0, 35.0, -50.0, 24.0)
    assert res.IsDone()
    roots = res.Roots
    for i in range(1, res.NbRoots):
        assert roots[i - 1] <= roots[i]


def test_MathPoly_QuarticTest_VerifyRootsSatisfyEquation():
    res = MathPoly.Quartic(1.0, -10.0, 35.0, -50.0, 24.0)
    assert res.IsDone()
    roots = res.Roots
    for i in range(res.NbRoots):
        assert near(eval_quartic(1.0, -10.0, 35.0, -50.0, 24.0, roots[i]), 0.0)


# Boolean conversion


def test_MathPoly_BoolConversionTest_SuccessfulResultIsTrue():
    assert bool(MathPoly.Quadratic(1.0, -5.0, 6.0)) is True


def test_MathPoly_BoolConversionTest_NoSolutionResultIsFalse():
    assert bool(MathPoly.Linear(0.0, 5.0)) is False


# Indexing operator


def test_MathPoly_IndexingTest_BracketOperator():
    res = MathPoly.Quadratic(1.0, -5.0, 6.0)
    assert res.IsDone()
    assert res[0] == res.Roots[0]
    assert res[1] == res.Roots[1]
