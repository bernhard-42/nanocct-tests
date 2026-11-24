# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_BrentMinimum_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: QuadraticMinimumFinding, QuarticMinimumFinding, CosineMinimumFinding, ConstructorWithKnownValue,
# CustomTolerance, CustomIterationLimit, InvalidBracketingTriplet, FlatFunction, MonotonicFunction, CustomZEPS,
# ReversedBracketOrder, HighPrecisionRequirement, VeryNarrowBracket, MultipleCalls, EdgeCaseAtBoundary: they minimise
# the test's own C++ subclasses of math_Function; a Python subclass would need a trampoline, and nanocct generates
# none (docs/Excluded.md).
from nanocct.math import math_BrentMinimum


def test_MathBrentMinimumTest_UnperformedState():
    solver = math_BrentMinimum(1.0e-10)

    # Before Perform() is called, the solver reports not done
    assert not solver.IsDone()

    # The state stays consistent when not done
    if not solver.IsDone():
        assert not solver.IsDone()
