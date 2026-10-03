# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_TrigonometricFunctionRoots_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.math import math_TrigonometricFunctionRoots

PI = math.pi
TOLERANCE = 1.0e-6


def solver(*args):
    s = math_TrigonometricFunctionRoots(*[float(a) for a in args])
    assert s.IsDone()
    return s


def values(s):
    return [s.Value(i) for i in range(1, s.NbSolutions() + 1)]


def test_math_TrigonometricFunctionRoots_FullEquationBasic():
    s = solver(1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() > 0


def test_math_TrigonometricFunctionRoots_LinearSineOnly():
    s = solver(1.0, -0.5, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() > 0
    assert abs(math.sin(s.Value(1)) - 0.5) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_LinearCosineAndSine():
    s = solver(1.0, 1.0, 0.0, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() > 0
    x = s.Value(1)
    assert abs(math.cos(x) + math.sin(x)) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_PureCosineEquation():
    s = solver(1.0, 0.0, 0.0, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 1
    assert abs(math.cos(s.Value(1))) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_PureSineEquation():
    s = solver(1.0, 0.0, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 2
    assert abs(math.sin(s.Value(1))) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_NoSolution():
    s = solver(1.0, 2.0, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() == 0


def test_math_TrigonometricFunctionRoots_InfiniteSolutions():
    s = solver(0.0, 0.0, 0.0, 2.0 * PI)
    assert s.InfiniteRoots()


def test_math_TrigonometricFunctionRoots_CustomBounds():
    s = solver(1.0, 0.0, PI / 2.0, 3.0 * PI / 2.0)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 1
    for x in values(s):
        assert PI / 2.0 <= x <= 3.0 * PI / 2.0
        assert abs(math.sin(x)) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_NarrowBounds():
    s = solver(1.0, 0.0, 0.0, 0.0, PI / 4.0)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() == 0


def test_math_TrigonometricFunctionRoots_QuadraticTerms():
    s = solver(1.0, 0.0, 0.0, 0.0, -0.5, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 2
    assert abs(math.cos(s.Value(1)) ** 2 - 0.5) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_MixedTerms():
    s = solver(1.0, 1.0, -math.sqrt(2.0), 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 1
    x = s.Value(1)
    assert abs(math.cos(x) + math.sin(x) - math.sqrt(2.0)) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_AllCoefficients():
    a, b, c, d, e = 1.0, 0.5, 0.5, 0.5, -0.25
    s = solver(a, b, c, d, e, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    for x in values(s):
        r = a * math.cos(x) ** 2 + 2.0 * b * math.cos(x) * math.sin(x) + c * math.cos(x) + d * math.sin(x) + e
        assert abs(r) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_LargeBounds():
    s = solver(1.0, 0.0, 0.0, 4.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 2


def test_math_TrigonometricFunctionRoots_NegativeBounds():
    s = solver(1.0, 0.0, 0.0, -PI, PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 1
    for x in values(s):
        assert -PI <= x <= PI
        assert abs(math.cos(x)) <= TOLERANCE


def test_math_TrigonometricFunctionRoots_HighFrequencyTest():
    s = solver(1.0, -0.5, 0.0, 2.0 * PI)
    assert not s.InfiniteRoots()
    assert s.NbSolutions() >= 2
    sols = values(s)
    first = any(abs(x - PI / 6.0) < 0.1 for x in sols)
    second = any(abs(x - 5.0 * PI / 6.0) < 0.1 for x in sols)
    assert first or second


def test_math_TrigonometricFunctionRoots_EdgeCaseSmallCoefficients():
    s = solver(1.0e-10, 1.0, 0.0, 0.0, 2.0 * PI)
    if not s.InfiniteRoots():
        assert s.NbSolutions() >= 2
