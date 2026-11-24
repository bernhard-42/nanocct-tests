# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_BissecNewton_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: QuadraticRootFinding, QuadraticSecondRoot, CubicRootFinding, SineFunctionRoot, CustomTolerance,
# IterationLimit, InvalidBounds, ZeroDerivativeHandling, MultipleCalls, HighPrecisionRequirement, EdgeCaseBounds: they
# solve the test's own C++ subclasses of math_FunctionWithDerivative; a Python subclass would need a trampoline, and
# nanocct generates none (docs/Excluded.md).
from nanocct.math import math_BissecNewton


def test_MathBissecNewtonTest_NotDoneState():
    solver = math_BissecNewton(1.0e-10)

    assert not solver.IsDone()
