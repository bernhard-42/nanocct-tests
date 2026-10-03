# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_Range_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct.Bnd import Bnd_Range
from nanocct.NCollection import NCollection_List
from nanocct.Standard import Standard_ConstructionError

OUT = Bnd_Range.IntersectStatus_Out
IN = Bnd_Range.IntersectStatus_In
BOUNDARY = Bnd_Range.IntersectStatus_Boundary


def bounds(r):
    ok, aMin, aMax = r.GetBounds()
    assert ok is True
    return aMin, aMax


def test_Bnd_RangeTest_DefaultConstructor_IsVoid():
    aRange = Bnd_Range()
    assert aRange.IsVoid() is True
    assert aRange.Delta() < 0.0


def test_Bnd_RangeTest_ParameterizedConstructor():
    aRange = Bnd_Range(3.0, 15.0)
    assert aRange.IsVoid() is False
    assert aRange.Delta() == 12.0


def test_Bnd_RangeTest_ParameterizedConstructor_InvalidRange():
    with pytest.raises(Standard_ConstructionError):
        Bnd_Range(10.0, 5.0)


def test_Bnd_RangeTest_ParameterizedConstructor_PointRange():
    aRange = Bnd_Range(5.0, 5.0)
    assert aRange.IsVoid() is False
    assert aRange.Delta() == 0.0


def test_Bnd_RangeTest_GetMin_GetMax_GetBounds():
    aRange = Bnd_Range(2.0, 8.0)
    assert aRange.GetMin() == (True, 2.0)
    assert aRange.GetMax() == (True, 8.0)
    assert aRange.GetBounds() == (True, 2.0, 8.0)


def test_Bnd_RangeTest_GetMin_GetMax_Void():
    aRange = Bnd_Range()
    assert aRange.GetMin()[0] is False
    assert aRange.GetMax()[0] is False
    assert aRange.GetBounds()[0] is False


def test_Bnd_RangeTest_GetIntermediatePoint():
    aRange = Bnd_Range(10.0, 20.0)
    assert aRange.GetIntermediatePoint(0.0) == (True, 10.0)
    assert aRange.GetIntermediatePoint(0.5) == (True, 15.0)
    assert aRange.GetIntermediatePoint(1.0) == (True, 20.0)


def test_Bnd_RangeTest_GetIntermediatePoint_Void():
    assert Bnd_Range().GetIntermediatePoint(0.5)[0] is False


def test_Bnd_RangeTest_SetVoid():
    aRange = Bnd_Range(1.0, 5.0)
    assert aRange.IsVoid() is False
    aRange.SetVoid()
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_Add_Double_ToVoid():
    aRange = Bnd_Range()
    aRange.Add(5.0)
    assert aRange.IsVoid() is False
    assert bounds(aRange) == (5.0, 5.0)


def test_Bnd_RangeTest_Add_Double_Extends():
    aRange = Bnd_Range(3.0, 7.0)
    aRange.Add(1.0)
    aRange.Add(10.0)
    assert bounds(aRange) == (1.0, 10.0)


def test_Bnd_RangeTest_Add_Range_ToVoid():
    aRange = Bnd_Range()
    aRange.Add(Bnd_Range(3.0, 7.0))
    assert bounds(aRange) == (3.0, 7.0)


def test_Bnd_RangeTest_Add_VoidRange():
    aRange = Bnd_Range(3.0, 7.0)
    aRange.Add(Bnd_Range())
    assert bounds(aRange) == (3.0, 7.0)


def test_Bnd_RangeTest_Add_Range_VoidToVoid():
    aRange = Bnd_Range()
    aRange.Add(Bnd_Range())
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_Add_Range_Extends():
    aRange = Bnd_Range(3.0, 7.0)
    aRange.Add(Bnd_Range(1.0, 10.0))
    assert bounds(aRange) == (1.0, 10.0)


def test_Bnd_RangeTest_Common_Overlapping():
    aRange = Bnd_Range(1.0, 10.0)
    aRange.Common(Bnd_Range(5.0, 15.0))
    assert bounds(aRange) == (5.0, 10.0)


def test_Bnd_RangeTest_Common_NoOverlap():
    aRange = Bnd_Range(1.0, 5.0)
    aRange.Common(Bnd_Range(7.0, 10.0))
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_Common_WithVoid():
    aRange = Bnd_Range(1.0, 5.0)
    aRange.Common(Bnd_Range())
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_Union_Overlapping():
    aRange = Bnd_Range(1.0, 7.0)
    assert aRange.Union(Bnd_Range(5.0, 15.0)) is True
    assert bounds(aRange) == (1.0, 15.0)


def test_Bnd_RangeTest_Union_Separated():
    aRange = Bnd_Range(1.0, 5.0)
    assert aRange.Union(Bnd_Range(7.0, 10.0)) is False
    assert bounds(aRange) == (1.0, 5.0)


def test_Bnd_RangeTest_Union_WithVoid():
    assert Bnd_Range(1.0, 5.0).Union(Bnd_Range()) is False


def test_Bnd_RangeTest_IsIntersected_Void():
    assert Bnd_Range().IsIntersected(5.0) == OUT


def test_Bnd_RangeTest_IsIntersected_Contains():
    assert Bnd_Range(3.0, 15.0).IsIntersected(5.0) == IN


def test_Bnd_RangeTest_IsIntersected_Outside():
    aRange = Bnd_Range(3.0, 15.0)
    assert aRange.IsIntersected(20.0) == OUT
    assert aRange.IsIntersected(1.0) == OUT


def test_Bnd_RangeTest_IsIntersected_OnBoundary():
    aRange = Bnd_Range(3.0, 15.0)
    assert aRange.IsIntersected(3.0) == BOUNDARY
    assert aRange.IsIntersected(15.0) == BOUNDARY


def test_Bnd_RangeTest_IsIntersected_PointRange():
    aRange = Bnd_Range(5.0, 5.0)
    assert aRange.IsIntersected(5.0) == BOUNDARY
    assert aRange.IsIntersected(3.0) == OUT


def test_Bnd_RangeTest_IsIntersected_Periodic_Contains():
    assert Bnd_Range(3.0, 15.0).IsIntersected(1.0, 4.0) == IN


def test_Bnd_RangeTest_IsIntersected_Periodic_OnBoundary():
    assert Bnd_Range(3.0, 15.0).IsIntersected(3.0, 4.0) == BOUNDARY


def test_Bnd_RangeTest_IsIntersected_Periodic_Outside():
    assert Bnd_Range(3.5, 3.9).IsIntersected(0.0, 4.0) == OUT


def test_Bnd_RangeTest_Split_NoIntersection():
    aList = NCollection_List[Bnd_Range]()
    Bnd_Range(3.0, 15.0).Split(20.0, aList)
    assert aList.Size() == 1
    assert bounds(aList.First()) == (3.0, 15.0)


def test_Bnd_RangeTest_Split_AtInteriorPoint():
    aList = NCollection_List[Bnd_Range]()
    Bnd_Range(3.0, 15.0).Split(5.0, aList)
    assert aList.Size() == 2
    assert bounds(aList.First()) == (3.0, 5.0)
    assert bounds(aList.Last()) == (5.0, 15.0)


def test_Bnd_RangeTest_Split_Periodic():
    aList = NCollection_List[Bnd_Range]()
    Bnd_Range(3.0, 15.0).Split(5.0, aList, 4.0)
    assert aList.Size() == 4


def test_Bnd_RangeTest_Enlarge():
    aRange = Bnd_Range(5.0, 10.0)
    aRange.Enlarge(2.0)
    assert bounds(aRange) == (3.0, 12.0)


def test_Bnd_RangeTest_Enlarge_Void():
    aRange = Bnd_Range()
    aRange.Enlarge(2.0)
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_Shifted():
    aRange = Bnd_Range(3.0, 7.0)
    aShifted = aRange.Shifted(10.0)
    assert bounds(aShifted) == (13.0, 17.0)
    assert bounds(aRange) == (3.0, 7.0)


def test_Bnd_RangeTest_Shifted_Void():
    assert Bnd_Range().Shifted(10.0).IsVoid() is True


def test_Bnd_RangeTest_Shift():
    aRange = Bnd_Range(3.0, 7.0)
    aRange.Shift(10.0)
    assert bounds(aRange) == (13.0, 17.0)


def test_Bnd_RangeTest_TrimFrom():
    aRange = Bnd_Range(3.0, 10.0)
    aRange.TrimFrom(5.0)
    assert bounds(aRange) == (5.0, 10.0)


def test_Bnd_RangeTest_TrimFrom_MakesVoid():
    aRange = Bnd_Range(3.0, 10.0)
    aRange.TrimFrom(15.0)
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_TrimTo():
    aRange = Bnd_Range(3.0, 10.0)
    aRange.TrimTo(7.0)
    assert bounds(aRange) == (3.0, 7.0)


def test_Bnd_RangeTest_TrimTo_MakesVoid():
    aRange = Bnd_Range(3.0, 10.0)
    aRange.TrimTo(1.0)
    assert aRange.IsVoid() is True


def test_Bnd_RangeTest_IsOut_Value():
    aRange = Bnd_Range(3.0, 10.0)
    assert aRange.IsOut(5.0) is False
    assert aRange.IsOut(3.0) is False
    assert aRange.IsOut(10.0) is False
    assert aRange.IsOut(1.0) is True
    assert aRange.IsOut(15.0) is True


def test_Bnd_RangeTest_IsOut_Void():
    assert Bnd_Range().IsOut(5.0) is True


def test_Bnd_RangeTest_IsOut_Range():
    aRange = Bnd_Range(3.0, 10.0)
    assert aRange.IsOut(Bnd_Range(5.0, 8.0)) is False
    assert aRange.IsOut(Bnd_Range(1.0, 5.0)) is False
    assert aRange.IsOut(Bnd_Range(11.0, 15.0)) is True


def test_Bnd_RangeTest_IsOut_Range_Void():
    aRange = Bnd_Range(3.0, 10.0)
    aVoid = Bnd_Range()
    assert aRange.IsOut(aVoid) is True
    assert aVoid.IsOut(aRange) is True


def test_Bnd_RangeTest_Equality():
    aRange1 = Bnd_Range(3.0, 10.0)
    aRange2 = Bnd_Range(3.0, 10.0)
    aRange3 = Bnd_Range(3.0, 11.0)
    assert (aRange1 == aRange2) is True
    assert (aRange1 == aRange3) is False


def test_Bnd_RangeTest_Contains_Value():
    aRange = Bnd_Range(3.0, 10.0)
    assert aRange.Contains(5.0) is True
    assert aRange.Contains(3.0) is True
    assert aRange.Contains(10.0) is True
    assert aRange.Contains(2.0) is False
    assert aRange.Contains(11.0) is False
    assert Bnd_Range().Contains(5.0) is False


def test_Bnd_RangeTest_Intersects_Range():
    aRange1 = Bnd_Range(3.0, 10.0)
    assert aRange1.Intersects(Bnd_Range(5.0, 15.0)) is True
    assert aRange1.Intersects(Bnd_Range(11.0, 20.0)) is False
    assert aRange1.Intersects(Bnd_Range()) is False


def test_Bnd_RangeTest_Min_Max_DirectAccess():
    aRange = Bnd_Range(3.0, 10.0)
    assert aRange.Min() == 3.0
    assert aRange.Max() == 10.0


def test_Bnd_RangeTest_Min_Max_NulloptOnVoid():
    aVoid = Bnd_Range()
    assert aVoid.Min() is None
    assert aVoid.Max() is None


def test_Bnd_RangeTest_Get_StructuredBindings():
    aBounds = Bnd_Range(3.0, 10.0).Get()
    assert aBounds is not None
    assert aBounds.Min == 3.0
    assert aBounds.Max == 10.0


def test_Bnd_RangeTest_Get_NulloptOnVoid():
    assert Bnd_Range().Get() is None


def test_Bnd_RangeTest_Center():
    assert Bnd_Range(2.0, 8.0).Center() == 5.0
    assert Bnd_Range(3.0, 3.0).Center() == 3.0


def test_Bnd_RangeTest_Center_NulloptOnVoid():
    assert Bnd_Range().Center() is None
