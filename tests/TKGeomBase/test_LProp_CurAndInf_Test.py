# Translated from OCCT src/ModelingData/TKGeomBase/GTests/LProp_CurAndInf_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.LProp import LProp_CurAndInf, LProp_Inflection, LProp_MaxCur, LProp_MinCur
from nanocct.Standard import Standard_OutOfRange


def test_LProp_CurAndInfTest_DefaultConstructor_IsEmpty():
    r = LProp_CurAndInf()
    assert r.IsEmpty()
    assert r.NbPoints() == 0


def test_LProp_CurAndInfTest_AddInflection():
    r = LProp_CurAndInf()
    r.AddInflection(1.5)
    assert not r.IsEmpty()
    assert r.NbPoints() == 1
    assert r.Parameter(1) == 1.5
    assert r.Type(1) == LProp_Inflection


def test_LProp_CurAndInfTest_AddExtCur_Minimum():
    r = LProp_CurAndInf()
    r.AddExtCur(2.0, True)
    assert r.NbPoints() == 1
    assert r.Parameter(1) == 2.0
    assert r.Type(1) == LProp_MinCur


def test_LProp_CurAndInfTest_AddExtCur_Maximum():
    r = LProp_CurAndInf()
    r.AddExtCur(3.0, False)
    assert r.NbPoints() == 1
    assert r.Parameter(1) == 3.0
    assert r.Type(1) == LProp_MaxCur


def test_LProp_CurAndInfTest_MultiplePoints_SortedByParameter():
    r = LProp_CurAndInf()
    r.AddInflection(5.0)
    r.AddExtCur(1.0, True)
    r.AddExtCur(3.0, False)
    r.AddInflection(7.0)
    assert r.NbPoints() == 4
    for i in range(1, r.NbPoints()):
        assert r.Parameter(i) <= r.Parameter(i + 1)


def test_LProp_CurAndInfTest_MultiplePoints_CorrectTypes():
    r = LProp_CurAndInf()
    r.AddExtCur(1.0, True)
    r.AddInflection(3.0)
    r.AddExtCur(5.0, False)
    assert r.NbPoints() == 3
    assert [r.Type(i) for i in (1, 2, 3)] == [LProp_MinCur, LProp_Inflection, LProp_MaxCur]


def test_LProp_CurAndInfTest_Clear():
    r = LProp_CurAndInf()
    r.AddInflection(1.0)
    r.AddExtCur(2.0, True)
    assert r.NbPoints() == 2
    r.Clear()
    assert r.IsEmpty()
    assert r.NbPoints() == 0


def test_LProp_CurAndInfTest_Clear_ThenRefill():
    r = LProp_CurAndInf()
    r.AddInflection(1.0)
    r.Clear()
    r.AddExtCur(5.0, False)
    assert r.NbPoints() == 1
    assert r.Parameter(1) == 5.0
    assert r.Type(1) == LProp_MaxCur


def test_LProp_CurAndInfTest_Parameter_OutOfRange_Throws():
    r = LProp_CurAndInf()
    r.AddInflection(1.0)
    with pytest.raises(Standard_OutOfRange):
        r.Parameter(0)
    with pytest.raises(Standard_OutOfRange):
        r.Parameter(2)


def test_LProp_CurAndInfTest_Type_OutOfRange_Throws():
    r = LProp_CurAndInf()
    r.AddInflection(1.0)
    with pytest.raises(Standard_OutOfRange):
        r.Type(0)
    with pytest.raises(Standard_OutOfRange):
        r.Type(2)
