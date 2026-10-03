# Translated from OCCT src/FoundationClasses/TKernel/GTests/Quantity_Period_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Quantity import Quantity_Period


def v6(p):
    return p.Values__int__int__int__int__int__int()


def v2(p):
    return p.Values__int__int()


def test_Quantity_PeriodTest_BasicConstruction():
    assert v6(Quantity_Period(1, 2, 3, 4, 5, 6)) == (1, 2, 3, 4, 5, 6)
    assert v2(Quantity_Period(3600, 500000)) == (3600, 500000)


def test_Quantity_PeriodTest_ConstexprComparisons():
    p1 = Quantity_Period(0, 0, 0, 100, 0, 0)
    p2 = Quantity_Period(0, 0, 0, 100, 0, 0)
    p3 = Quantity_Period(0, 0, 0, 200, 0, 0)
    assert p1.IsEqual(p2)
    assert not p1.IsEqual(p3)
    assert p1.IsShorter(p3)
    assert not p3.IsShorter(p1)
    assert not p1.IsShorter(p2)
    assert p3.IsLonger(p1)
    assert not p1.IsLonger(p3)
    assert not p1.IsLonger(p2)


def test_Quantity_PeriodTest_Validation():
    assert Quantity_Period.IsValid_s(1, 2, 3, 4, 5, 6)
    assert Quantity_Period.IsValid_s(0, 0, 0, 0, 0, 0)
    assert not Quantity_Period.IsValid_s(-1, 0, 0, 0, 0, 0)
    assert not Quantity_Period.IsValid_s(0, -1, 0, 0, 0, 0)
    assert not Quantity_Period.IsValid_s(0, 0, -1, 0, 0, 0)
    assert not Quantity_Period.IsValid_s(0, 0, 0, -1, 0, 0)
    assert not Quantity_Period.IsValid_s(0, 0, 0, 0, -1, 0)
    assert not Quantity_Period.IsValid_s(0, 0, 0, 0, 0, -1)
    assert Quantity_Period.IsValid_s(100, 500)
    assert not Quantity_Period.IsValid_s(-1, 500)
    assert not Quantity_Period.IsValid_s(100, -1)


def test_Quantity_PeriodTest_SetValuesRoundTrip():
    p = Quantity_Period(0, 0)
    p.SetValues(2, 3, 4, 5, 6, 7)
    assert v6(p) == (2, 3, 4, 5, 6, 7)


def test_Quantity_PeriodTest_FormatConversion():
    assert v2(Quantity_Period(1, 0, 0, 0, 0, 0))[0] == 86400
    assert v2(Quantity_Period(0, 1, 0, 0, 0, 0))[0] == 3600
    assert v2(Quantity_Period(0, 0, 1, 0, 0, 0))[0] == 60


def test_Quantity_PeriodTest_MillisecondConversion():
    assert v2(Quantity_Period(0, 0, 0, 0, 1, 0)) == (0, 1000)
    assert v2(Quantity_Period(0, 0, 0, 0, 5, 250)) == (0, 5250)


def test_Quantity_PeriodTest_MicrosecondOverflow():
    p = Quantity_Period(0, 0)
    p.SetValues(0, 1500000)
    assert v2(p) == (1, 500000)


def test_Quantity_PeriodTest_AddPeriods():
    r = Quantity_Period(0, 1, 0, 0, 0, 0).Add(Quantity_Period(0, 2, 0, 0, 0, 0))
    assert v2(r) == (10800, 0)


def test_Quantity_PeriodTest_AddWithMicrosecondOverflow():
    r = Quantity_Period(0, 0, 0, 0, 0, 600000).Add(Quantity_Period(0, 0, 0, 0, 0, 600000))
    assert v2(r) == (1, 200000)


def test_Quantity_PeriodTest_SubtractPeriods():
    r = Quantity_Period(0, 3, 0, 0, 0, 0).Subtract(Quantity_Period(0, 1, 0, 0, 0, 0))
    assert v2(r) == (7200, 0)


def test_Quantity_PeriodTest_SubtractWithMicrosecondUnderflow():
    r = Quantity_Period(0, 0, 0, 1, 0, 200000).Subtract(Quantity_Period(0, 0, 0, 0, 0, 500000))
    assert v2(r) == (0, 700000)


def test_Quantity_PeriodTest_SubtractNegative():
    r = Quantity_Period(0, 1, 0, 0, 0, 0).Subtract(Quantity_Period(0, 3, 0, 0, 0, 0))
    assert v2(r) == (7200, 0)


def test_Quantity_PeriodTest_ComplexCalculations():
    assert v2(Quantity_Period(1, 2, 30, 45, 500, 250)) == (95445, 500250)


def test_Quantity_PeriodTest_ComponentExtraction():
    assert v6(Quantity_Period(2, 3, 45, 30, 123, 456)) == (2, 3, 45, 30, 123, 456)


def test_Quantity_PeriodTest_ZeroPeriod():
    p = Quantity_Period(0, 0, 0, 0, 0, 0)
    assert v6(p) == (0, 0, 0, 0, 0, 0)
    assert p.IsEqual(Quantity_Period(0, 0, 0, 0, 0, 0))


def test_Quantity_PeriodTest_LargeValues():
    assert v2(Quantity_Period(100, 0, 0, 0, 0, 0)) == (8640000, 0)


def test_Quantity_PeriodTest_TimeConstantValues():
    assert v2(Quantity_Period(0, 24, 0, 0, 0, 0))[0] == v2(Quantity_Period(1, 0, 0, 0, 0, 0))[0]
    assert v2(Quantity_Period(0, 0, 0, 60, 0, 0))[0] == v2(Quantity_Period(0, 0, 1, 0, 0, 0))[0]
    assert v2(Quantity_Period(0, 0, 60, 0, 0, 0))[0] == v2(Quantity_Period(0, 1, 0, 0, 0, 0))[0]


def test_Quantity_PeriodTest_MillisecondToSecondConversion():
    assert v2(Quantity_Period(0, 0, 0, 0, 1000, 0)) == (1, 0)


def test_Quantity_PeriodTest_SubtractLargeMicrosecondUnderflow():
    r = Quantity_Period(0, 0, 0, 10, 0, 200000).Subtract(Quantity_Period(0, 0, 0, 0, 0, 2700000))
    assert v2(r) == (7, 500000)


def test_Quantity_PeriodTest_SubtractNegativeWithMicroseconds():
    r = Quantity_Period(0, 0, 0, 5, 0, 300000).Subtract(Quantity_Period(0, 0, 0, 8, 0, 100000))
    assert v2(r) == (2, 800000)
