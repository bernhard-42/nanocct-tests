# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathPoly_Comparison_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import MathPoly
from nanocct.math import math_DirectPolynomialRoots

THE_TOLERANCE = 1.0e-9


def old_roots(solver):
    roots = []
    if solver.IsDone():
        roots = [solver.Value(i) for i in range(1, solver.NbSolutions() + 1)]
    return sorted(roots)


def new_roots(res):
    roots = []
    if res.IsDone():
        all_roots = res.Roots
        roots = [all_roots[i] for i in range(res.NbRoots)]
    return sorted(roots)


def compare_roots(old, new, tol=THE_TOLERANCE):
    assert len(old) == len(new), "Different number of roots"
    for o, n in zip(old, new):
        assert abs(o - n) <= tol, (o, n)


def solve_both(*coeffs):
    old = math_DirectPolynomialRoots(*[float(c) for c in coeffs])
    solver = {3: MathPoly.Quadratic, 4: MathPoly.Cubic, 5: MathPoly.Quartic}[len(coeffs)]
    return old, solver(*coeffs)


def check_same(*coeffs, tol=THE_TOLERANCE):
    old, new = solve_both(*coeffs)
    assert old.IsDone()
    assert new.IsDone()
    compare_roots(old_roots(old), new_roots(new), tol)
    return old, new


def check_all_near(coeffs, value, tol):
    old, new = solve_both(*coeffs)
    assert old.IsDone()
    assert new.IsDone()
    for r in old_roots(old):
        assert abs(r - value) <= tol
    for r in new_roots(new):
        assert abs(r - value) <= tol


# Quadratic


def test_MathPoly_ComparisonTest_Quadratic_TwoDistinctRoots():
    check_same(1.0, -5.0, 6.0)


def test_MathPoly_ComparisonTest_Quadratic_DoubleRoot():
    check_all_near((1.0, -4.0, 4.0), 2.0, THE_TOLERANCE)


def test_MathPoly_ComparisonTest_Quadratic_NoRealRoots():
    old, new = solve_both(1.0, 0.0, 1.0)
    assert old.NbSolutions() == 0
    assert new.NbRoots == 0


def test_MathPoly_ComparisonTest_Quadratic_NegativeRoots():
    check_same(1.0, 5.0, 6.0)


def test_MathPoly_ComparisonTest_Quadratic_LargeCoefficients():
    check_same(1000.0, -3000.0, 2000.0)


# Cubic


def test_MathPoly_ComparisonTest_Cubic_ThreeDistinctRoots():
    check_same(1.0, -6.0, 11.0, -6.0)


def test_MathPoly_ComparisonTest_Cubic_OneRealRoot():
    old, new = solve_both(1.0, 0.0, 1.0, 2.0)
    assert old.IsDone()
    assert new.IsDone()
    assert old.NbSolutions() == new.NbRoots
    if old.NbSolutions() > 0 and new.NbRoots > 0:
        compare_roots(old_roots(old), new_roots(new))


def test_MathPoly_ComparisonTest_Cubic_TripleRoot():
    check_all_near((1.0, -3.0, 3.0, -1.0), 1.0, 1.0e-6)


def test_MathPoly_ComparisonTest_Cubic_NegativeLeadingCoeff():
    check_same(-1.0, 6.0, -11.0, 6.0)


# Quartic


def test_MathPoly_ComparisonTest_Quartic_FourDistinctRoots():
    check_same(1.0, -10.0, 35.0, -50.0, 24.0)


def test_MathPoly_ComparisonTest_Quartic_TwoRealRoots():
    old, new = solve_both(1.0, 0.0, 0.0, 0.0, -1.0)
    assert old.IsDone()
    assert new.IsDone()
    assert old.NbSolutions() == 2
    assert new.NbRoots == 2
    compare_roots(old_roots(old), new_roots(new))


def test_MathPoly_ComparisonTest_Quartic_Biquadratic():
    check_same(1.0, 0.0, -5.0, 0.0, 4.0)


def test_MathPoly_ComparisonTest_Quartic_NoRealRoots():
    old, new = solve_both(1.0, 0.0, 0.0, 0.0, 1.0)
    assert old.NbSolutions() == 0
    assert new.NbRoots == 0


def test_MathPoly_ComparisonTest_Quartic_QuadrupleRoot():
    check_all_near((1.0, -8.0, 24.0, -32.0, 16.0), 2.0, 1.0e-5)


# Edge cases


def test_MathPoly_ComparisonTest_Quadratic_SmallDiscriminant():
    old, new = solve_both(1.0, -2.0, 0.9999)
    assert old.IsDone()
    assert new.IsDone()
    assert old.NbSolutions() == 2
    assert new.NbRoots == 2
    compare_roots(old_roots(old), new_roots(new), 1.0e-4)


def test_MathPoly_ComparisonTest_Cubic_SmallCoefficients():
    check_same(0.001, -0.006, 0.011, -0.006, tol=1.0e-6)


# Numerical stability


def test_MathPoly_ComparisonTest_Quadratic_NumericallyChallengingCase():
    old, new = solve_both(1.0, -1.0e8, 1.0)
    assert old.IsDone()
    assert new.IsDone()
    assert old.NbSolutions() == 2
    assert new.NbRoots == 2
    o, n = old_roots(old), new_roots(new)
    assert abs(o[0] - n[0]) <= 1.0e-14
    assert abs(o[1] / n[1] - 1.0) <= 1.0e-8


def test_MathPoly_ComparisonTest_Quartic_SymmetricRoots():
    old, new = check_same(1.0, 0.0, -5.0, 0.0, 4.0)
    n = new_roots(new)
    assert len(n) == 4
    for r, e in zip(n, [-2.0, -1.0, 1.0, 2.0]):
        assert abs(r - e) <= THE_TOLERANCE
