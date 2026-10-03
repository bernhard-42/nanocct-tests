# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathRoot_Trig_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import MathRoot

THE_TOL = 1.0e-10
THE_PI = math.pi
THE_2PI = 2.0 * THE_PI


def evaluate_equation(a, b, c, d, e, x):
    cs = math.cos(x)
    sn = math.sin(x)
    return a * cs * cs + 2.0 * b * cs * sn + c * cs + d * sn + e


def verify_roots(res, a, b, c, d, e, tol=1.0e-10):
    roots = res.Roots
    for i in range(res.NbRoots):
        val = evaluate_equation(a, b, c, d, e, roots[i])
        assert abs(val) <= tol, f"Root {i} = {roots[i]} gives f(x) = {val}"


# Basic linear equations: d*sin(x) + e = 0


def test_MathRoot_TrigTest_LinearSin_ZeroConstant():
    r = MathRoot.TrigonometricLinear(1.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, 0.0)


def test_MathRoot_TrigTest_LinearSin_HalfValue():
    r = MathRoot.TrigonometricLinear(1.0, -0.5)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, -0.5)


def test_MathRoot_TrigTest_LinearSin_NegativeHalf():
    r = MathRoot.TrigonometricLinear(1.0, 0.5)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, 0.5)


def test_MathRoot_TrigTest_LinearSin_NoSolution():
    r = MathRoot.TrigonometricLinear(1.0, -2.0)
    assert r.IsDone()
    assert r.NbRoots == 0


def test_MathRoot_TrigTest_LinearSin_BoundaryValue():
    r = MathRoot.TrigonometricLinear(1.0, -1.0)
    assert r.IsDone()
    assert r.NbRoots >= 1
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, -1.0)


# Basic equations: c*cos(x) + e = 0


def test_MathRoot_TrigTest_LinearCos_ZeroConstant():
    r = MathRoot.Trigonometric(0.0, 0.0, 1.0, 0.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 1.0, 0.0, 0.0)


def test_MathRoot_TrigTest_LinearCos_HalfValue():
    r = MathRoot.Trigonometric(0.0, 0.0, 1.0, 0.0, -0.5)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 1.0, 0.0, -0.5)


def test_MathRoot_TrigTest_LinearCos_NoSolution():
    r = MathRoot.Trigonometric(0.0, 0.0, 1.0, 0.0, -2.0)
    assert r.IsDone()
    assert r.NbRoots == 0


# Linear combination: c*cos(x) + d*sin(x) + e = 0


def test_MathRoot_TrigTest_CDE_CosPlusSin():
    r = MathRoot.TrigonometricCDE(1.0, 1.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 1.0, 1.0, 0.0)


def test_MathRoot_TrigTest_CDE_CosPlusSinEqualsSqrt2():
    r = MathRoot.TrigonometricCDE(1.0, 1.0, -math.sqrt(2.0))
    assert r.IsDone()
    assert r.NbRoots >= 1
    verify_roots(r, 0.0, 0.0, 1.0, 1.0, -math.sqrt(2.0), 1.0e-9)


def test_MathRoot_TrigTest_CDE_CosMinusSin():
    r = MathRoot.TrigonometricCDE(1.0, -1.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 0.0, 0.0, 1.0, -1.0, 0.0)


def test_MathRoot_TrigTest_CDE_Harmonic():
    r = MathRoot.TrigonometricCDE(3.0, 4.0, -5.0)
    assert r.IsDone()
    assert r.NbRoots >= 1
    verify_roots(r, 0.0, 0.0, 3.0, 4.0, -5.0)


def test_MathRoot_TrigTest_CDE_NoSolution():
    r = MathRoot.TrigonometricCDE(1.0, 1.0, -2.0)
    assert r.IsDone()
    assert r.NbRoots == 0


# Quadratic in cos: a*cos^2(x) + c*cos(x) + e = 0


def test_MathRoot_TrigTest_QuadraticCos_TwoSolutions():
    r = MathRoot.Trigonometric(1.0, 0.0, 0.0, 0.0, -1.0)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 1.0, 0.0, 0.0, 0.0, -1.0)


def test_MathRoot_TrigTest_QuadraticCos_FourSolutions():
    r = MathRoot.Trigonometric(1.0, 0.0, 0.0, 0.0, -0.25)
    assert r.IsDone()
    assert r.NbRoots == 4
    verify_roots(r, 1.0, 0.0, 0.0, 0.0, -0.25)


# Mixed terms


def test_MathRoot_TrigTest_CosSinProduct_AE_Zero():
    r = MathRoot.Trigonometric(0.0, 1.0, 0.0, 0.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots == 4
    verify_roots(r, 0.0, 1.0, 0.0, 0.0, 0.0)


def test_MathRoot_TrigTest_Mixed_SinTimesCos():
    r = MathRoot.Trigonometric(0.0, 0.5, 0.0, 1.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 0.0, 0.5, 0.0, 1.0, 0.0)


# General quartic cases


def test_MathRoot_TrigTest_General_FourRoots():
    r = MathRoot.Trigonometric(1.0, 0.0, 1.0, 0.0, -0.5)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 1.0, 0.0, 1.0, 0.0, -0.5)


def test_MathRoot_TrigTest_General_AllCoefficients():
    r = MathRoot.Trigonometric(1.0, 0.5, 0.3, 0.4, -0.2)
    assert r.IsDone()
    verify_roots(r, 1.0, 0.5, 0.3, 0.4, -0.2, 1.0e-8)


# Bound constraint tests


def test_MathRoot_TrigTest_Bounds_FirstQuadrant():
    r = MathRoot.TrigonometricLinear(1.0, -0.5, 0.0, THE_PI / 2.0)
    assert r.IsDone()
    assert r.NbRoots == 1
    assert r.Roots[0] >= 0.0 - THE_TOL
    assert r.Roots[0] <= THE_PI / 2.0 + THE_TOL
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, -0.5)


def test_MathRoot_TrigTest_Bounds_SecondQuadrant():
    r = MathRoot.TrigonometricLinear(1.0, -0.5, THE_PI / 2.0, THE_PI)
    assert r.IsDone()
    assert r.NbRoots == 1
    assert r.Roots[0] >= THE_PI / 2.0 - THE_TOL
    assert r.Roots[0] <= THE_PI + THE_TOL
    verify_roots(r, 0.0, 0.0, 0.0, 1.0, -0.5)


def test_MathRoot_TrigTest_Bounds_NarrowRange():
    r = MathRoot.Trigonometric(0.0, 0.0, 1.0, 0.0, 0.0, THE_PI / 2.0 - 0.1, THE_PI / 2.0 + 0.1)
    assert r.IsDone()
    assert r.NbRoots == 1
    assert abs(r.Roots[0] - THE_PI / 2.0) <= THE_TOL


def test_MathRoot_TrigTest_Bounds_RootOutsideRange():
    r = MathRoot.TrigonometricLinear(1.0, -0.5, THE_PI, THE_2PI)
    assert r.IsDone()
    assert r.NbRoots == 0


def test_MathRoot_TrigTest_Bounds_FullCircle():
    r = MathRoot.TrigonometricLinear(1.0, 0.0, 0.0, THE_2PI)
    assert r.IsDone()
    assert r.NbRoots == 2


def test_MathRoot_TrigTest_Bounds_MultipleCircles():
    r = MathRoot.TrigonometricLinear(1.0, 0.0, 0.0, 4.0 * THE_PI)
    assert r.IsDone()
    assert r.NbRoots == 2


# Degenerate cases


def test_MathRoot_TrigTest_Degenerate_AllZero():
    r = MathRoot.Trigonometric(0.0, 0.0, 0.0, 0.0, 0.0)
    assert r.InfiniteRoots is True


def test_MathRoot_TrigTest_Degenerate_ConstantNonZero():
    r = MathRoot.Trigonometric(0.0, 0.0, 0.0, 0.0, 1.0)
    assert r.IsDone()
    assert r.NbRoots == 0


def test_MathRoot_TrigTest_Degenerate_NearZeroCoefficients():
    r = MathRoot.Trigonometric(1.0e-14, 1.0e-14, 1.0, 0.0, -0.5)
    assert r.IsDone()
    assert r.NbRoots == 2
    verify_roots(r, 1.0e-14, 1.0e-14, 1.0, 0.0, -0.5, 1.0e-6)


# Special case: PI as root


def test_MathRoot_TrigTest_SpecialCase_PiRoot():
    r = MathRoot.Trigonometric(1.0, 0.0, -1.0, 0.0, 0.0)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 1.0, 0.0, -1.0, 0.0, 0.0)


def test_MathRoot_TrigTest_SpecialCase_PiRootCheck():
    r = MathRoot.Trigonometric(1.0, 0.0, 0.0, 0.0, -1.0)
    assert r.IsDone()
    roots = r.Roots
    found_pi = any(abs(roots[i] - THE_PI) < THE_TOL for i in range(r.NbRoots))
    assert found_pi, "PI should be a root of cos^2(x) - 1 = 0"
    verify_roots(r, 1.0, 0.0, 0.0, 0.0, -1.0)


# Numerical stability tests


def test_MathRoot_TrigTest_Stability_LargeCoefficients():
    r = MathRoot.Trigonometric(1000.0, 500.0, 300.0, 400.0, -200.0)
    assert r.IsDone()
    verify_roots(r, 1000.0, 500.0, 300.0, 400.0, -200.0, 1.0e-6)


def test_MathRoot_TrigTest_Stability_SmallCoefficients():
    r = MathRoot.Trigonometric(1.0e-6, 0.5e-6, 0.3e-6, 0.4e-6, -0.2e-6)
    assert r.IsDone()
    if r.NbRoots > 0:
        verify_roots(r, 1.0e-6, 0.5e-6, 0.3e-6, 0.4e-6, -0.2e-6, 1.0e-4)


def test_MathRoot_TrigTest_Stability_MixedMagnitude():
    r = MathRoot.Trigonometric(1.0, 0.0, 1.0e6, 0.0, -0.5e6)
    assert r.IsDone()
    verify_roots(r, 1.0, 0.0, 1.0e6, 0.0, -0.5e6, 1.0e-4)


# Root ordering and uniqueness tests


def test_MathRoot_TrigTest_RootOrdering_Sorted():
    r = MathRoot.TrigonometricLinear(1.0, 0.0)
    assert r.IsDone()
    roots = r.Roots
    for i in range(1, r.NbRoots):
        assert roots[i - 1] <= roots[i], "Roots should be in ascending order"


def test_MathRoot_TrigTest_RootUniqueness_NoDuplicates():
    r = MathRoot.Trigonometric(1.0, 0.0, 0.0, 0.0, -0.25)
    assert r.IsDone()
    roots = r.Roots
    for i in range(r.NbRoots):
        for j in range(i + 1, r.NbRoots):
            assert abs(roots[i] - roots[j]) > 1.0e-10, f"Roots {i} and {j} are duplicates"


# Wrapper function tests


def test_MathRoot_TrigTest_Wrapper_TrigonometricLinear():
    r1 = MathRoot.TrigonometricLinear(2.0, -1.0)
    r2 = MathRoot.Trigonometric(0.0, 0.0, 0.0, 2.0, -1.0)
    assert r1.NbRoots == r2.NbRoots
    for i in range(r1.NbRoots):
        assert abs(r1.Roots[i] - r2.Roots[i]) <= THE_TOL


def test_MathRoot_TrigTest_Wrapper_TrigonometricCDE():
    r1 = MathRoot.TrigonometricCDE(1.0, 2.0, -0.5)
    r2 = MathRoot.Trigonometric(0.0, 0.0, 1.0, 2.0, -0.5)
    assert r1.NbRoots == r2.NbRoots
    for i in range(r1.NbRoots):
        assert abs(r1.Roots[i] - r2.Roots[i]) <= THE_TOL


# Result structure tests


def test_MathRoot_TrigTest_Result_BoolConversion():
    r = MathRoot.TrigonometricLinear(1.0, 0.0)
    assert bool(r) is True
    assert r.IsDone()


def test_MathRoot_TrigTest_Result_InfiniteRoots():
    r = MathRoot.Trigonometric(0.0, 0.0, 0.0, 0.0, 0.0)
    assert r.InfiniteRoots is True


# Ellipse-related equation tests


def test_MathRoot_TrigTest_Ellipse_PointOnMajorAxis():
    b2_minus_a2_over2 = (100.0 - 400.0) / 2.0
    ax = 20.0 * 30.0
    by = 0.0
    r = MathRoot.Trigonometric(0.0, b2_minus_a2_over2, -by, ax, 0.0, 0.0, THE_2PI)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 0.0, b2_minus_a2_over2, -by, ax, 0.0)


def test_MathRoot_TrigTest_Ellipse_GeneralPoint():
    b2_minus_a2_over2 = (100.0 - 400.0) / 2.0
    ax = 20.0 * 15.0
    by = 10.0 * 8.0
    r = MathRoot.Trigonometric(0.0, b2_minus_a2_over2, -by, ax, 0.0, 0.0, THE_2PI)
    assert r.IsDone()
    verify_roots(r, 0.0, b2_minus_a2_over2, -by, ax, 0.0)


# Negative parameter range tests


def test_MathRoot_TrigTest_NegativeBounds_Basic():
    r = MathRoot.TrigonometricLinear(1.0, 0.0, -THE_PI, 0.0)
    assert r.IsDone()
    assert r.NbRoots >= 1
    roots = r.Roots
    for i in range(r.NbRoots):
        assert roots[i] >= -THE_PI - THE_TOL
        assert roots[i] <= THE_TOL


def test_MathRoot_TrigTest_NegativeBounds_CosEquation():
    r = MathRoot.Trigonometric(0.0, 0.0, 1.0, 0.0, -0.5, -THE_PI, THE_PI)
    assert r.IsDone()
    assert r.NbRoots >= 2
    verify_roots(r, 0.0, 0.0, 1.0, 0.0, -0.5)
