# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_DirectPolynomialRoots_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_DirectPolynomialRoots

TOL = 1.0e-10


def poly(coeffs, x):
    # coefficients in descending degree order
    r = 0.0
    for c in coeffs:
        r = r * x + c
    return r


def verify_root(root, coeffs, tol=1.0e-10):
    assert abs(poly(coeffs, root)) <= tol


def roots_of(r):
    return [r.Value(i) for i in range(1, r.NbSolutions() + 1)]


def check_ordered(coeffs, expected, tol, verify_tol=None):
    r = math_DirectPolynomialRoots(*coeffs)
    assert r.IsDone()
    assert r.NbSolutions() == len(expected)
    got = roots_of(r)
    for g, e in zip(got, expected):
        assert abs(g - e) <= tol
    if verify_tol is not None:
        for g in got:
            verify_root(g, coeffs, verify_tol)
    return r


def test_math_DirectPolynomialRootsTest_QuadraticRoots():
    check_ordered([1.0, -5.0, 6.0], [3.0, 2.0], TOL, 1e-10)


def test_math_DirectPolynomialRootsTest_QuadraticNoRealRoots():
    r = math_DirectPolynomialRoots(1.0, 1.0, 1.0)
    assert r.IsDone()
    assert r.NbSolutions() == 0


def test_math_DirectPolynomialRootsTest_QuadraticDoubleRoot():
    check_ordered([1.0, -2.0, 1.0], [1.0, 1.0], TOL, 1e-10)


def test_math_DirectPolynomialRootsTest_CubicRoots():
    check_ordered([1.0, -6.0, 11.0, -6.0], [3.0, 2.0, 1.0], TOL, 1e-10)


def test_math_DirectPolynomialRootsTest_CubicOneRealRoot():
    r = math_DirectPolynomialRoots(1.0, 0.0, 1.0, 1.0)
    assert r.IsDone()
    assert r.NbSolutions() == 1
    verify_root(r.Value(1), [1.0, 0.0, 1.0, 1.0])


def test_math_DirectPolynomialRootsTest_QuarticRoots():
    check_ordered([1.0, 0.0, -5.0, 0.0, 4.0], [-2.0, -1.0, 2.0, 1.0], TOL, 1e-10)


def test_math_DirectPolynomialRootsTest_LinearCase():
    check_ordered([2.0, -6.0], [3.0], TOL, 1e-10)


def test_math_DirectPolynomialRootsTest_DegenerateLinearCase():
    r = math_DirectPolynomialRoots(0.0, 5.0)
    assert r.IsDone()
    assert r.NbSolutions() == 0


def test_math_DirectPolynomialRootsTest_PolynomialEvaluation():
    r = math_DirectPolynomialRoots(1.0, -3.0, 2.0)
    assert r.IsDone()
    assert r.NbSolutions() == 2
    for x in roots_of(r):
        verify_root(x, [1.0, -3.0, 2.0])


def test_math_DirectPolynomialRootsTest_NearZeroCoefficients():
    r = math_DirectPolynomialRoots(1.0e-15, 1.0, -2.0)
    assert r.IsDone()
    assert r.NbSolutions() == 2
    assert any(abs(x - 2.0) < 1.0e-6 for x in roots_of(r))


def test_math_DirectPolynomialRootsTest_BiQuadraticPolynomial():
    check_ordered([1.0, 0.0, -10.0, 0.0, 9.0], [-3.0, -1.0, 3.0, 1.0], 1e-8, 1e-8)


def test_math_DirectPolynomialRootsTest_RepeatedRoots():
    check_ordered([1.0, -3.0, 3.0, -1.0], [1.0, 1.0, 1.0], 1e-8, 1e-8)


def test_math_DirectPolynomialRootsTest_ProblematicQuarticCaseDetailed():
    c = [1.0000000000000004, -2.2737367544323211e-13, -17361733.368892364, 28.998342463569099, 75357446168894.516]
    r = check_ordered(c, [-2946.425490, -2946.236617, 2946.394276, 2946.267830], 1.0e-3)
    assert not r.InfiniteRoots()
    for x in roots_of(r):
        res = c[0] * x**4 + c[1] * x**3 + c[2] * x**2 + c[3] * x + c[4]
        assert abs(res) < 1.0


def test_math_DirectPolynomialRootsTest_ModernImplementationBiquadraticDetection():
    check_ordered([1.0, 0.0, -5.0, 0.0, 4.0], [-2.0, -1.0, 2.0, 1.0], 1e-12)


def test_math_DirectPolynomialRootsTest_FullFerrariMethodRequired():
    check_ordered([1.0, 1.0, -4.0, -4.0, 0.0], [-2.0, -1.0, 2.0, 0.0], 1e-10)


def test_math_DirectPolynomialRootsTest_AggressiveRefinementEffectiveness():
    c = [1.0, 0.0, -1000000.0, 0.0, 999999.0]
    r = math_DirectPolynomialRoots(*c)
    assert r.IsDone()
    for x in roots_of(r):
        res = c[0] * x**4 + c[1] * x**3 + c[2] * x**2 + c[3] * x + c[4]
        assert abs(res) < 1.0e-3


def test_math_DirectPolynomialRootsTest_CubicWithAggressiveRefinement():
    r = check_ordered([1.0, -6.0, 11.0, -6.0], [3.0, 2.0, 1.0], 1e-12)
    for x in roots_of(r):
        assert abs(x * x * x - 6.0 * x * x + 11.0 * x - 6.0) < 1.0e-12


def test_math_DirectPolynomialRootsTest_ExtremeCoefficientsStability():
    c = [1.0, 1.0e-15, -1.0e8, 1.0e-10, 1.0e15]
    r = math_DirectPolynomialRoots(*c)
    assert r.IsDone()
    for x in roots_of(r):
        res = c[0] * x**4 + c[1] * x**3 + c[2] * x**2 + c[3] * x + c[4]
        assert abs(res) < 1.0e6


def test_math_DirectPolynomialRootsTest_CloseToZeroCoefficients():
    eps = 1.0e-14
    check_ordered([1.0, eps, eps, eps, -16.0], [2.0, -2.0], 1e-10)
