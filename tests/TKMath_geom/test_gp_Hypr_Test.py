# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Hypr_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.gp import gp_Hypr
from nanocct.Standard import RealLast


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_gp_HyprTest_DefaultConstructor():
    hypr = gp_Hypr()
    assert hypr.MajorRadius() == _eq(RealLast())
    assert hypr.MinorRadius() == _eq(RealLast())


def test_gp_HyprTest_DefaultConstructorConjugateBranches():
    hypr = gp_Hypr()
    for branch in (hypr.ConjugateBranch1(), hypr.ConjugateBranch2()):
        assert branch.MajorRadius() == _eq(RealLast())
        assert branch.MinorRadius() == _eq(RealLast())
