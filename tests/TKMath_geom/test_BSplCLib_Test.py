# Translated from OCCT src/FoundationClasses/TKMath/GTests/BSplCLib_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BSplCLib import BSplCLib


def test_BSplCLibTest_UnitWeights_SmallSize_ReturnsNonOwning():
    n = 10
    w = BSplCLib.UnitWeights_s(n)
    assert w.Lower() == 1
    assert w.Upper() == n
    assert w.Length() == n
    assert w.IsDeletable() is False
    for i in range(1, n + 1):
        assert w[i] == 1.0


def test_BSplCLibTest_UnitWeights_MaxSize_ReturnsNonOwning():
    n = BSplCLib.MaxUnitWeightsSize_s()
    w = BSplCLib.UnitWeights_s(n)
    assert w.Length() == n
    assert w.IsDeletable() is False
    assert w[1] == 1.0
    assert w[n] == 1.0


def test_BSplCLibTest_UnitWeights_OverMaxSize_ReturnsOwning():
    n = BSplCLib.MaxUnitWeightsSize_s() + 1
    w = BSplCLib.UnitWeights_s(n)
    assert w.Lower() == 1
    assert w.Upper() == n
    assert w.Length() == n
    assert w.IsDeletable() is True
    for i in range(1, n + 1):
        assert w[i] == 1.0


def test_BSplCLibTest_UnitWeights_SingleElement():
    w = BSplCLib.UnitWeights_s(1)
    assert w.Length() == 1
    assert w.IsDeletable() is False
    assert w[1] == 1.0


def test_BSplCLibTest_MaxUnitWeightsSize_IsPositive():
    assert BSplCLib.MaxUnitWeightsSize_s() > 0
    assert BSplCLib.MaxUnitWeightsSize_s() == 2049
