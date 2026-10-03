# Translated from OCCT src/FoundationClasses/TKMath/GTests/BSplSLib_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BSplSLib import BSplSLib


def test_BSplSLibTest_UnitWeights_SmallSurface_ReturnsNonOwning():
    nu, nv = 4, 5
    w = BSplSLib.UnitWeights_s(nu, nv)
    assert w.ColLength() == nu
    assert w.RowLength() == nv
    assert w.Size() == nu * nv
    assert w.IsDeletable() is False
    for i in range(1, nu + 1):
        for j in range(1, nv + 1):
            assert w[i, j] == 1.0


def test_BSplSLibTest_UnitWeights_MaxBezierSize_ReturnsNonOwning():
    nu, nv = 26, 26
    w = BSplSLib.UnitWeights_s(nu, nv)
    assert w.Size() == nu * nv
    assert w.IsDeletable() is False
    assert w[1, 1] == 1.0
    assert w[nu, nv] == 1.0


def test_BSplSLibTest_UnitWeights_AtMaxLimit_ReturnsNonOwning():
    nu, nv = 3, 683
    w = BSplSLib.UnitWeights_s(nu, nv)
    assert w.Size() == nu * nv
    assert w.IsDeletable() is False
    assert w[1, 1] == 1.0
    assert w[nu, nv] == 1.0


def test_BSplSLibTest_UnitWeights_OverMaxLimit_ReturnsOwning():
    nu, nv = 50, 50
    w = BSplSLib.UnitWeights_s(nu, nv)
    assert w.ColLength() == nu
    assert w.RowLength() == nv
    assert w.Size() == nu * nv
    assert w.IsDeletable() is True
    for i in range(1, nu + 1):
        for j in range(1, nv + 1):
            assert w[i, j] == 1.0


def test_BSplSLibTest_UnitWeights_SingleElement():
    w = BSplSLib.UnitWeights_s(1, 1)
    assert w.Size() == 1
    assert w.IsDeletable() is False
    assert w[1, 1] == 1.0
