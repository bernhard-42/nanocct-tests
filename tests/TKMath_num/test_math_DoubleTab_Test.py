# Translated from OCCT src/FoundationClasses/TKMath/GTests/math_DoubleTab_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.math import math_DoubleTab


def test_MathDoubleTabTest_DefaultConstructor():
    t = math_DoubleTab(1, 3, 1, 3)
    t.Init(5.0)
    for i in range(1, 4):
        for j in range(1, 4):
            assert t.Value(i, j) == pytest.approx(5.0)
            assert t(i, j) == pytest.approx(5.0)


def test_MathDoubleTabTest_CopyConstructor():
    orig = math_DoubleTab(1, 3, 1, 3)
    orig.Init(10.0)
    orig.SetValue(1, 1, 1.5)
    orig.SetValue(2, 2, 2.5)
    orig.SetValue(3, 3, 3.5)

    copy = math_DoubleTab(orig)
    assert copy.Value(1, 1) == pytest.approx(1.5)
    assert copy.Value(2, 2) == pytest.approx(2.5)
    assert copy.Value(3, 3) == pytest.approx(3.5)
    assert copy.Value(1, 2) == pytest.approx(10.0)


def test_MathDoubleTabTest_InitOperation():
    t = math_DoubleTab(0, 2, 0, 2)
    t.Init(7.5)
    for i in range(0, 3):
        for j in range(0, 3):
            assert t.Value(i, j) == pytest.approx(7.5)


def test_MathDoubleTabTest_ValueAccess():
    t = math_DoubleTab(1, 2, 1, 2)
    t.SetValue(1, 1, 11.0)
    t.SetValue(1, 2, 12.0)
    t.SetValue(2, 1, 21.0)
    t.SetValue(2, 2, 22.0)
    assert t(1, 1) == pytest.approx(11.0)
    assert t(1, 2) == pytest.approx(12.0)
    assert t(2, 1) == pytest.approx(21.0)
    assert t(2, 2) == pytest.approx(22.0)


def test_MathDoubleTabTest_OperatorAccess():
    t = math_DoubleTab(-1, 1, -1, 1)
    values = {
        (-1, -1): -11.0, (-1, 0): -10.0, (-1, 1): -9.0,
        (0, -1): -1.0, (0, 0): 0.0, (0, 1): 1.0,
        (1, -1): 9.0, (1, 0): 10.0, (1, 1): 11.0,
    }
    for key, x in values.items():
        t[key] = x
    for (i, j), x in values.items():
        assert t.Value(i, j) == pytest.approx(x)


def test_MathDoubleTabTest_CopyMethod():
    src = math_DoubleTab(1, 2, 1, 2)
    src.SetValue(1, 1, 100.0)
    src.SetValue(1, 2, 200.0)
    src.SetValue(2, 1, 300.0)
    src.SetValue(2, 2, 400.0)

    dst = math_DoubleTab(1, 2, 1, 2)
    dst.Init(0.0)
    src.Copy(dst)
    assert dst.Value(1, 1) == pytest.approx(100.0)
    assert dst.Value(1, 2) == pytest.approx(200.0)
    assert dst.Value(2, 1) == pytest.approx(300.0)
    assert dst.Value(2, 2) == pytest.approx(400.0)


def test_MathDoubleTabTest_SmallArrayOptimization():
    t = math_DoubleTab(1, 4, 1, 4)
    t.Init(42.0)
    t.SetValue(2, 3, 123.45)
    assert t.Value(2, 3) == pytest.approx(123.45)
    assert t.Value(1, 1) == pytest.approx(42.0)


def test_MathDoubleTabTest_LargeArrayAllocation():
    t = math_DoubleTab(1, 5, 1, 5)
    t.Init(99.99)
    t.SetValue(3, 4, 987.65)
    assert t.Value(3, 4) == pytest.approx(987.65)
    assert t.Value(1, 1) == pytest.approx(99.99)


def test_MathDoubleTabTest_SingleElement():
    t = math_DoubleTab(5, 5, 10, 10)
    t.SetValue(5, 10, 777.0)
    assert t.Value(5, 10) == pytest.approx(777.0)
    assert t(5, 10) == pytest.approx(777.0)


def test_MathDoubleTabTest_NegativeIndices():
    t = math_DoubleTab(-5, -1, -3, -1)
    t.Init(-1.0)
    t.SetValue(-3, -2, -999.0)
    assert t.Value(-3, -2) == pytest.approx(-999.0)
    assert t.Value(-5, -3) == pytest.approx(-1.0)
