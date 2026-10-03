# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Mat_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Mat


def test_gp_MatTest_OCC22595_DefaultConstructor():
    m = gp_Mat()
    for r in (1, 2, 3):
        for c in (1, 2, 3):
            assert m(r, c) == 0.0
            assert m.Value(r, c) == 0.0
