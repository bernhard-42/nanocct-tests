# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_ComputeKronrodPointsAndWeights_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.math import math_ComputeKronrodPointsAndWeights


def test_math_ComputeKronrodPointsAndWeights_Test_OCC33048_ComputeWithOrder125():
    calc = math_ComputeKronrodPointsAndWeights(125)
    assert calc.IsDone()
