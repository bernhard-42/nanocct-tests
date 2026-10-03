# Translated from OCCT src/FoundationClasses/TKernel/GTests/Quantity_Date_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Quantity import Quantity_Date, Quantity_Period


def test_Quantity_DateTest_BasicConstruction():
    mm, dd, yy, hh, mn, ss, mis, mics = Quantity_Date().Values()
    assert (mm, dd, yy, hh, mn, ss) == (1, 1, 1979, 0, 0, 0)
    assert Quantity_Date(6, 15, 2025, 14, 30, 45, 123, 456).Values() == (6, 15, 2025, 14, 30, 45, 123, 456)


def test_Quantity_DateTest_ConstexprComparisons():
    d1 = Quantity_Date(1, 1, 2020, 0, 0, 0, 0, 0)
    d2 = Quantity_Date(1, 1, 2020, 0, 0, 0, 0, 0)
    d3 = Quantity_Date(1, 2, 2020, 0, 0, 0, 0, 0)
    assert d1.IsEqual(d2)
    assert not d1.IsEqual(d3)
    assert d1.IsEarlier(d3)
    assert not d3.IsEarlier(d1)
    assert not d1.IsEarlier(d2)
    assert d3.IsLater(d1)
    assert not d1.IsLater(d3)
    assert not d1.IsLater(d2)


def test_Quantity_DateTest_LeapYearDetection():
    assert Quantity_Date.IsLeap_s(2000)
    assert Quantity_Date.IsLeap_s(2004)
    assert Quantity_Date.IsLeap_s(2020)
    assert not Quantity_Date.IsLeap_s(1900)
    assert not Quantity_Date.IsLeap_s(2001)
    assert not Quantity_Date.IsLeap_s(2100)


def test_Quantity_DateTest_ValidationWithLeapYear():
    assert Quantity_Date.IsValid_s(2, 29, 2020, 0, 0, 0, 0, 0)
    assert not Quantity_Date.IsValid_s(2, 29, 2019, 0, 0, 0, 0, 0)
    assert Quantity_Date.IsValid_s(2, 28, 2019, 0, 0, 0, 0, 0)
    assert Quantity_Date.IsValid_s(2, 28, 2020, 0, 0, 0, 0, 0)


def test_Quantity_DateTest_MonthBoundaries():
    assert Quantity_Date.IsValid_s(1, 31, 2020, 0, 0, 0, 0, 0)
    assert not Quantity_Date.IsValid_s(1, 32, 2020, 0, 0, 0, 0, 0)
    assert Quantity_Date.IsValid_s(4, 30, 2020, 0, 0, 0, 0, 0)
    assert not Quantity_Date.IsValid_s(4, 31, 2020, 0, 0, 0, 0, 0)
    assert Quantity_Date.IsValid_s(12, 31, 2020, 0, 0, 0, 0, 0)
    assert not Quantity_Date.IsValid_s(12, 32, 2020, 0, 0, 0, 0, 0)


def test_Quantity_DateTest_TimeValidation():
    v = Quantity_Date.IsValid_s
    assert v(1, 1, 2020, 23, 59, 59, 999, 999)
    assert v(1, 1, 2020, 0, 0, 0, 0, 0)
    assert not v(1, 1, 2020, 24, 0, 0, 0, 0)
    assert not v(1, 1, 2020, -1, 0, 0, 0, 0)
    assert not v(1, 1, 2020, 0, 60, 0, 0, 0)
    assert not v(1, 1, 2020, 0, -1, 0, 0, 0)
    assert not v(1, 1, 2020, 0, 0, 60, 0, 0)
    assert not v(1, 1, 2020, 0, 0, -1, 0, 0)
    assert not v(1, 1, 2020, 0, 0, 0, 1000, 0)
    assert not v(1, 1, 2020, 0, 0, 0, -1, 0)
    assert not v(1, 1, 2020, 0, 0, 0, 0, 1000)
    assert not v(1, 1, 2020, 0, 0, 0, 0, -1)


def test_Quantity_DateTest_SetValuesRoundTrip():
    d = Quantity_Date()
    d.SetValues(3, 15, 2021, 10, 25, 30, 500, 750)
    assert d.Values() == (3, 15, 2021, 10, 25, 30, 500, 750)


def test_Quantity_DateTest_IndividualGetters():
    d1 = Quantity_Date(1, 2, 1979, 0, 0, 0, 0, 0)
    assert (d1.Month(), d1.Day(), d1.Year()) == (1, 2, 1979)
    d2 = Quantity_Date(7, 20, 2024, 0, 0, 0, 0, 0)
    assert (d2.Month(), d2.Day(), d2.Year()) == (7, 20, 2024)
    d3 = Quantity_Date(7, 20, 2024, 15, 45, 30, 123, 456)
    assert (d3.Month(), d3.Day(), d3.Year()) == (7, 20, 2024)
    assert (d3.Hour(), d3.Minute(), d3.Second(), d3.MilliSecond(), d3.MicroSecond()) == (15, 45, 30, 123, 456)


def test_Quantity_DateTest_DateDifference():
    d1 = Quantity_Date(1, 1, 2020, 0, 0, 0, 0, 0)
    d2 = Quantity_Date(1, 1, 2020, 1, 0, 0, 0, 0)
    assert d2.Difference(d1).Values__int__int() == (3600, 0)


def test_Quantity_DateTest_AddPeriod():
    nd = Quantity_Date(1, 1, 2020, 0, 0, 0, 0, 0).Add(Quantity_Period(1, 0, 0, 0, 0, 0))
    assert nd.Values()[:3] == (1, 2, 2020)


def test_Quantity_DateTest_SubtractPeriod():
    nd = Quantity_Date(1, 2, 2020, 0, 0, 0, 0, 0).Subtract(Quantity_Period(1, 0, 0, 0, 0, 0))
    assert nd.Values()[:3] == (1, 1, 2020)


def test_Quantity_DateTest_YearBoundary():
    nd = Quantity_Date(12, 31, 2020, 23, 59, 59, 0, 0).Add(Quantity_Period(0, 0, 0, 1, 0, 0))
    assert nd.Values()[:6] == (1, 1, 2021, 0, 0, 0)


def test_Quantity_DateTest_LeapYearBoundary():
    nd1 = Quantity_Date(2, 28, 2020, 0, 0, 0, 0, 0).Add(Quantity_Period(1, 0, 0, 0, 0, 0))
    assert nd1.Values()[:3] == (2, 29, 2020)
    nd2 = Quantity_Date(2, 28, 2021, 0, 0, 0, 0, 0).Add(Quantity_Period(1, 0, 0, 0, 0, 0))
    assert nd2.Values()[:3] == (3, 1, 2021)


def test_Quantity_DateTest_MicrosecondOverflow():
    nd = Quantity_Date(1, 1, 2020, 0, 0, 0, 999, 999).Add(Quantity_Period(0, 0, 0, 0, 0, 1))
    assert nd.Values() == (1, 1, 2020, 0, 0, 1, 0, 0)


def test_Quantity_DateTest_SpecificDateCalculations():
    d2 = Quantity_Date(1, 1, 2020, 0, 0, 0, 0, 0).Add(Quantity_Period(0, 24, 0, 0, 0, 0))
    assert d2.Values()[:4] == (1, 2, 2020, 0)


def test_Quantity_DateTest_MinimumDate():
    assert Quantity_Date.IsValid_s(1, 1, 1979, 0, 0, 0, 0, 0)
    assert not Quantity_Date.IsValid_s(12, 31, 1978, 23, 59, 59, 999, 999)


def test_Quantity_DateTest_MultipleLeapYearChecks():
    for year in range(2000, 2025):
        for month in range(1, 13):
            if month == 2:
                if Quantity_Date.IsLeap_s(year):
                    max_day = 29
                else:
                    max_day = 28
            elif month in (4, 6, 9, 11):
                max_day = 30
            else:
                max_day = 31
            assert Quantity_Date.IsValid_s(month, max_day, year, 0, 0, 0, 0, 0)
            assert not Quantity_Date.IsValid_s(month, max_day + 1, year, 0, 0, 0, 0, 0)


def test_Quantity_DateTest_DifferenceFromEpoch():
    p = Quantity_Date().Difference(Quantity_Date(1, 2, 1979, 0, 0, 0, 0, 0))
    assert p.Values__int__int() == (86400, 0)


def test_Quantity_DateTest_DifferenceWithMicrosecondUnderflow():
    d1 = Quantity_Date(1, 1, 2020, 0, 0, 1, 200, 0)
    d2 = Quantity_Date(1, 1, 2020, 0, 0, 0, 500, 0)
    assert d1.Difference(d2).Values__int__int() == (0, 700000)


def test_Quantity_DateTest_DifferenceReversed():
    d1 = Quantity_Date(1, 1, 2020, 1, 0, 0, 0, 0)
    d2 = Quantity_Date(1, 1, 2020, 3, 0, 0, 0, 0)
    assert d1.Difference(d2).Values__int__int() == (7200, 0)
