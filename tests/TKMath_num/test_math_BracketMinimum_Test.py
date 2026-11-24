# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_BracketMinimum_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: QuadraticMinimumBracketing, ConstructorWithPrecomputedValues, ConstructorWithOnePrecomputedValue,
# QuarticFunctionBracketing, CosineFunction, SetLimits, SetPrecomputedValues, NoMinimumFunction, MultipleLocalMinima,
# VeryNarrowInitialBounds, ReverseOrderInitialPoints, RestrictiveLimits: they bracket the test's own C++ subclasses of
# math_Function; a Python subclass would need a trampoline, and nanocct generates none (docs/Excluded.md).
from nanocct.math import math_BracketMinimum


def test_MathBracketMinimumTest_UnperformedState():
    bracketer = math_BracketMinimum(0.0, 1.0)

    assert not bracketer.IsDone()
