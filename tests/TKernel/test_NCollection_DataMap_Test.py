# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_DataMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# Skipped: STL algorithm tests, move semantics, Emplace*/TryEmplace* (not bound), custom hashers,
# ItemsModifyValue / ItemsIteratorEquality (the C++ Items() view is not bound; Python items() returns a list of copies).
import pytest

from nanocct.NCollection import NCollection_DataMap
from nanocct.Standard import Standard_NoSuchObject
from nanocct.TCollection import TCollection_AsciiString

MapIS = NCollection_DataMap[int, TCollection_AsciiString]
MapII = NCollection_DataMap[int, int]


def test_NCollection_DataMapTest_IntegerKeys():
    aMap = MapIS()
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert aMap.Extent() == 0


def test_NCollection_DataMapTest_BindingAndAccess():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aMap.Bind(3, "Three")
    assert not aMap.IsEmpty()
    assert aMap.Size() == 3
    assert aMap.Find(1).ToCString() == "One"
    assert aMap.Find(2).ToCString() == "Two"
    assert aMap.Find(3).ToCString() == "Three"
    assert aMap.IsBound(1)
    assert aMap.IsBound(2)
    assert aMap.IsBound(3)
    assert not aMap.IsBound(4)


def test_NCollection_DataMapTest_ChangeFind():
    aMap = MapIS()
    aMap.Bind(1, "One")
    assert aMap.Find(1).ToCString() == "One"
    aMap.ChangeFind(1).Copy("Modified One")
    assert aMap.Find(1).ToCString() == "Modified One"


def test_NCollection_DataMapTest_Rebind():
    aMap = MapIS()
    aMap.Bind(1, "One")
    assert aMap.Find(1).ToCString() == "One"
    aMap.Bind(1, "New One")
    assert aMap.Find(1).ToCString() == "New One"
    assert aMap.Size() == 1


def test_NCollection_DataMapTest_UnBind():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aMap.Bind(3, "Three")
    assert aMap.UnBind(2)
    assert aMap.Size() == 2
    assert not aMap.IsBound(2)
    assert not aMap.UnBind(4)
    assert aMap.Size() == 2


def test_NCollection_DataMapTest_Clear():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert not aMap.IsBound(1)
    assert not aMap.IsBound(2)


def test_NCollection_DataMapTest_Assignment():
    aMap1 = MapIS()
    aMap1.Bind(1, "One")
    aMap1.Bind(2, "Two")
    aMap2 = MapIS()
    aMap2.Assign(aMap1)
    assert aMap1.Size() == aMap2.Size()
    assert aMap1.Find(1).ToCString() == aMap2.Find(1).ToCString()
    assert aMap1.Find(2).ToCString() == aMap2.Find(2).ToCString()
    aMap1.ChangeFind(1).Copy("Modified One")
    assert aMap1.Find(1).ToCString() == "Modified One"
    assert aMap2.Find(1).ToCString() == "One"


def test_NCollection_DataMapTest_Find_NonExisting():
    aMap = MapIS()
    aMap.Bind(1, "One")
    with pytest.raises(Standard_NoSuchObject):
        aMap.Find(2)
    with pytest.raises(Standard_NoSuchObject):
        aMap.ChangeFind(2)


def test_NCollection_DataMapTest_IteratorAccess():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aMap.Bind(3, "Three")
    foundKeys = set()
    foundValues = set()
    it = MapIS.Iterator(aMap)
    while it.More():
        foundKeys.add(it.Key())
        foundValues.add(it.Value().ToCString())
        it.Next()
    assert foundKeys == {1, 2, 3}
    assert foundValues == {"One", "Two", "Three"}


def test_NCollection_DataMapTest_ChangeValue():
    aMap = MapIS()
    aMap.Bind(1, "One")
    it = MapIS.Iterator(aMap)
    assert it.Value().ToCString() == "One"
    it.ChangeValue().Copy("Modified via Iterator")
    assert it.Value().ToCString() == "Modified via Iterator"
    assert aMap.Find(1).ToCString() == "Modified via Iterator"


def test_NCollection_DataMapTest_ExhaustiveIterator():
    NUM_ELEMENTS = 1000
    aMap = MapII()
    for i in range(NUM_ELEMENTS):
        aMap.Bind(i, i * 2)
    assert aMap.Size() == NUM_ELEMENTS
    count = 0
    it = MapII.Iterator(aMap)
    while it.More():
        assert it.Value() == it.Key() * 2
        count += 1
        it.Next()
    assert count == NUM_ELEMENTS


def test_NCollection_DataMapTest_TryBind_NewKey():
    aMap = MapIS()
    assert aMap.TryBind(1, "One")
    assert aMap.Size() == 1
    assert aMap.Find(1).ToCString() == "One"
    assert aMap.TryBind(2, "Two")
    assert aMap.Size() == 2
    assert aMap.Find(2).ToCString() == "Two"


def test_NCollection_DataMapTest_TryBind_ExistingKey():
    aMap = MapIS()
    aMap.Bind(1, "One")
    assert aMap.Find(1).ToCString() == "One"
    assert not aMap.TryBind(1, "New One")
    assert aMap.Size() == 1
    assert aMap.Find(1).ToCString() == "One"


def test_NCollection_DataMapTest_TryBound_NewKey():
    aMap = MapIS()
    aRef = aMap.TryBound(1, "One")
    assert aRef.ToCString() == "One"
    assert aMap.Find(1).ToCString() == "One"
    assert aMap.Size() == 1
    aRef.Copy("Modified One")
    assert aMap.Find(1).ToCString() == "Modified One"


def test_NCollection_DataMapTest_TryBound_ExistingKey():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aRef = aMap.TryBound(1, "New One")
    assert aRef.ToCString() == "One"
    assert aMap.Find(1).ToCString() == "One"
    assert aMap.Size() == 1
    aRef.Copy("Modified One")
    assert aMap.Find(1).ToCString() == "Modified One"


def test_NCollection_DataMapTest_ItemsIteration():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aMap.Bind(3, "Three")
    aFoundKeys = set()
    aFoundValues = set()
    for aKey, aValue in aMap.items():
        aFoundKeys.add(aKey)
        aFoundValues.add(aValue.ToCString())
    assert aFoundKeys == {1, 2, 3}
    assert aFoundValues == {"One", "Two", "Three"}


def test_NCollection_DataMapTest_ItemsStructuredBindings():
    aMap = MapIS()
    aMap.Bind(10, "Ten")
    aMap.Bind(20, "Twenty")
    aSum = 0
    for aKey, _aValue in aMap.items():
        aSum += aKey
    assert aSum == 30


def test_NCollection_DataMapTest_ConstItemsIteration():
    aMap = MapIS()
    aMap.Bind(1, "One")
    aMap.Bind(2, "Two")
    aCount = 0
    for _aKey, _aValue in aMap.items():
        aCount += 1
    assert aCount == 2
