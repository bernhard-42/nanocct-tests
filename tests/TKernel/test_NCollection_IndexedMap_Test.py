# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_IndexedMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_IndexedMap<int> is not bound: substituted by NCollection_IndexedMap[float] with integral keys
# (keys compare equal as 10 == 10.0; the tested indexing semantics are unchanged).
# Skipped: ComplexKeys (custom C++ key/hasher), STL iterator/algorithm tests, Added_MoveSemantics,
# Added_ReferenceValidity (addresses), Emplace*/Emplaced (not bound), custom hashers, IndexedItems() (not bound).
from nanocct.NCollection import NCollection_IndexedMap
from nanocct.TCollection import TCollection_AsciiString

IMap = NCollection_IndexedMap[float]


def test_NCollection_IndexedMapTest_DefaultConstructor():
    aMap = IMap()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Size() == 0


def test_NCollection_IndexedMapTest_BasicAddFind():
    aMap = IMap()
    assert aMap.Add(10) == 1
    assert aMap.Add(20) == 2
    assert aMap.Add(30) == 3
    assert aMap.Extent() == 3
    assert aMap.FindIndex(10) == 1
    assert aMap.FindIndex(20) == 2
    assert aMap.FindIndex(30) == 3
    assert aMap.FindKey(1) == 10
    assert aMap.FindKey(2) == 20
    assert aMap.FindKey(3) == 30
    assert aMap(1) == 10
    assert aMap(2) == 20
    assert aMap(3) == 30
    assert aMap.Contains(10)
    assert aMap.Contains(20)
    assert aMap.Contains(30)
    assert not aMap.Contains(40)


def test_NCollection_IndexedMapTest_DuplicateKey():
    aMap = IMap()
    assert aMap.Add(10) == 1
    assert aMap.Add(20) == 2
    assert aMap.Add(10) == 1
    assert aMap.Extent() == 2


def test_NCollection_IndexedMapTest_RemoveLast():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    aMap.RemoveLast()
    assert aMap.Extent() == 2
    assert aMap.Contains(10)
    assert aMap.Contains(20)
    assert not aMap.Contains(30)
    assert aMap.FindIndex(10) == 1
    assert aMap.FindIndex(20) == 2


def test_NCollection_IndexedMapTest_RemoveFromIndex():
    aMap = IMap()
    for k in (10, 20, 30, 40):
        aMap.Add(k)
    aMap.RemoveFromIndex(2)
    assert aMap.Extent() == 3
    assert aMap.Contains(10)
    assert not aMap.Contains(20)
    assert aMap.Contains(30)
    assert aMap.Contains(40)
    assert aMap.FindKey(2) == 40
    assert aMap.FindKey(1) == 10
    assert aMap.FindKey(3) == 30


def test_NCollection_IndexedMapTest_RemoveKey():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    assert aMap.RemoveKey(20)
    assert aMap.Extent() == 2
    assert aMap.Contains(10)
    assert not aMap.Contains(20)
    assert aMap.Contains(30)
    assert not aMap.RemoveKey(50)
    assert aMap.Extent() == 2


def test_NCollection_IndexedMapTest_Substitute():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    aMap.Substitute(2, 25)
    assert aMap.Extent() == 3
    assert aMap.Contains(10)
    assert not aMap.Contains(20)
    assert aMap.Contains(25)
    assert aMap.Contains(30)
    assert aMap.FindIndex(10) == 1
    assert aMap.FindIndex(25) == 2
    assert aMap.FindIndex(30) == 3
    assert aMap.FindKey(1) == 10
    assert aMap.FindKey(2) == 25
    assert aMap.FindKey(3) == 30


def test_NCollection_IndexedMapTest_Swap():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    aMap.Swap(1, 3)
    assert aMap.Extent() == 3
    assert aMap.Contains(10)
    assert aMap.Contains(20)
    assert aMap.Contains(30)
    assert aMap.FindKey(1) == 30
    assert aMap.FindKey(2) == 20
    assert aMap.FindKey(3) == 10
    assert aMap.FindIndex(10) == 3
    assert aMap.FindIndex(20) == 2
    assert aMap.FindIndex(30) == 1


def test_NCollection_IndexedMapTest_Clear():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    assert aMap.Extent() == 3
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Add(40) == 1
    assert aMap.Extent() == 1


def test_NCollection_IndexedMapTest_CopyConstructor():
    aMap1 = IMap()
    aMap1.Add(10)
    aMap1.Add(20)
    aMap1.Add(30)
    aMap2 = IMap(aMap1)
    assert aMap2.Extent() == 3
    assert aMap2.Contains(10)
    assert aMap2.Contains(20)
    assert aMap2.Contains(30)
    assert aMap2.FindIndex(10) == 1
    assert aMap2.FindIndex(20) == 2
    assert aMap2.FindIndex(30) == 3
    aMap1.Add(40)
    assert aMap1.Extent() == 4
    assert aMap2.Extent() == 3
    assert not aMap2.Contains(40)


def test_NCollection_IndexedMapTest_AssignmentOperator():
    aMap1 = IMap()
    aMap2 = IMap()
    aMap1.Add(10)
    aMap1.Add(20)
    aMap2.Add(30)
    aMap2.Add(40)
    aMap2.Add(50)
    aMap2.Assign(aMap1)
    assert aMap2.Extent() == 2
    assert aMap2.Contains(10)
    assert aMap2.Contains(20)
    assert not aMap2.Contains(30)
    assert not aMap2.Contains(40)
    assert not aMap2.Contains(50)


def test_NCollection_IndexedMapTest_Iterator():
    aMap = IMap()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    found = set()
    count = 0
    it = IMap.Iterator(aMap)
    while it.More():
        found.add(it.Value())
        count += 1
        it.Next()
    assert count == 3
    assert found == {10, 20, 30}


def test_NCollection_IndexedMapTest_StringKeys():
    aStringMap = NCollection_IndexedMap[TCollection_AsciiString]()
    assert aStringMap.Add(TCollection_AsciiString("First")) == 1
    assert aStringMap.Add(TCollection_AsciiString("Second")) == 2
    assert aStringMap.Add(TCollection_AsciiString("Third")) == 3
    assert aStringMap.FindIndex(TCollection_AsciiString("First")) == 1
    assert aStringMap.FindIndex(TCollection_AsciiString("Second")) == 2
    assert aStringMap.FindIndex(TCollection_AsciiString("Third")) == 3
    assert aStringMap.FindKey(1).IsEqual("First")
    assert aStringMap.FindKey(2).IsEqual("Second")
    assert aStringMap.FindKey(3).IsEqual("Third")


def test_NCollection_IndexedMapTest_Exchange():
    aMap1 = IMap()
    aMap2 = IMap()
    aMap1.Add(10)
    aMap1.Add(20)
    aMap2.Add(30)
    aMap2.Add(40)
    aMap2.Add(50)
    aMap1.Exchange(aMap2)
    assert aMap1.Extent() == 3
    assert aMap1.Contains(30)
    assert aMap1.Contains(40)
    assert aMap1.Contains(50)
    assert aMap2.Extent() == 2
    assert aMap2.Contains(10)
    assert aMap2.Contains(20)


def test_NCollection_IndexedMapTest_ReSize():
    aMap = IMap(3)
    for i in range(1, 101):
        aMap.Add(i)
    assert aMap.Extent() == 100
    for i in range(1, 101):
        assert aMap.Contains(i)
        assert aMap.FindIndex(i) == i
        assert aMap.FindKey(i) == i
    aMap.ReSize(200)
    assert aMap.Extent() == 100
    for i in range(1, 101):
        assert aMap.Contains(i)
        assert aMap.FindIndex(i) == i
        assert aMap.FindKey(i) == i


def test_NCollection_IndexedMapTest_Added_NewKey():
    aMap = IMap()
    assert aMap.Added(10) == 10
    assert aMap.Extent() == 1
    assert aMap.Contains(10)
    assert aMap.FindIndex(10) == 1
    assert aMap.Added(20) == 20
    assert aMap.Extent() == 2
    assert aMap.Contains(20)
    assert aMap.FindIndex(20) == 2


def test_NCollection_IndexedMapTest_Added_ExistingKey():
    aMap = IMap()
    aMap.Add(10)
    assert aMap.Extent() == 1
    assert aMap.Added(10) == 10
    assert aMap.Extent() == 1
    assert aMap.FindIndex(10) == 1


def test_NCollection_IndexedMapTest_RangeBasedForLoop():
    aMap = IMap()
    aMap.Add(100)
    aMap.Add(200)
    aMap.Add(300)
    aFoundKeys = set()
    for aKey in aMap:
        aFoundKeys.add(aKey)
    assert aFoundKeys == {100, 200, 300}
