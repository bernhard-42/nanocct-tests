# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_IndexedDataMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_IndexedDataMap<int, double> / <int, AsciiString> are not bound: substituted by
# NCollection_IndexedDataMap[TCollection_AsciiString, TCollection_AsciiString] with keys K(10) == "10" and items
# V(1.5) == "1.5" (a class-type item also keeps the C++ "modify through the returned reference" meaning).
# StringKeys uses the bound <AsciiString, int> (its items are integral).
# Skipped: StlIterator, STL algorithm tests, ComplexKeyAndValue (custom C++ types), *_MoveSemantics,
# TryBound_ReferenceValidity (addresses), Emplace*/TryEmplace* (not bound), custom hashers,
# ItemsModifyValue / IndexedItems* / ItemsIteratorEquality (C++ views not bound; Python items() returns copies).
# ChangeValues: the `aMap(1) = 1.9` part is left out (Python cannot assign to a call; __call__ returns a copy).
from nanocct.NCollection import NCollection_IndexedDataMap
from nanocct.TCollection import TCollection_AsciiString

IDMap = NCollection_IndexedDataMap[TCollection_AsciiString, TCollection_AsciiString]


def K(key):
    return str(key)


def V(value):
    return repr(float(value))


def f(item):
    return float(item.ToCString())


def k(key):
    return int(key.ToCString())


def filled(*pairs, buckets=None):
    aMap = IDMap() if buckets is None else IDMap(buckets)
    for key, value in pairs:
        aMap.Add(K(key), V(value))
    return aMap


def test_NCollection_IndexedDataMapTest_DefaultConstructor():
    aMap = IDMap()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Size() == 0


def test_NCollection_IndexedDataMapTest_BasicAddFind():
    aMap = IDMap()
    assert aMap.Add(K(10), V(1.0)) == 1
    assert aMap.Add(K(20), V(2.0)) == 2
    assert aMap.Add(K(30), V(3.0)) == 3
    assert aMap.Extent() == 3
    assert aMap.FindIndex(K(10)) == 1
    assert aMap.FindIndex(K(20)) == 2
    assert aMap.FindIndex(K(30)) == 3
    assert k(aMap.FindKey(1)) == 10
    assert k(aMap.FindKey(2)) == 20
    assert k(aMap.FindKey(3)) == 30
    assert f(aMap.FindFromIndex(1)) == 1.0
    assert f(aMap.FindFromIndex(2)) == 2.0
    assert f(aMap.FindFromIndex(3)) == 3.0
    assert f(aMap(1)) == 1.0
    assert f(aMap(2)) == 2.0
    assert f(aMap(3)) == 3.0
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert f(aMap.FindFromKey(K(20))) == 2.0
    assert f(aMap.FindFromKey(K(30))) == 3.0
    assert aMap.Contains(K(10))
    assert aMap.Contains(K(20))
    assert aMap.Contains(K(30))
    assert not aMap.Contains(K(40))


def test_NCollection_IndexedDataMapTest_DuplicateKey():
    aMap = IDMap()
    assert aMap.Add(K(10), V(1.0)) == 1
    assert aMap.Add(K(20), V(2.0)) == 2
    assert aMap.Add(K(10), V(3.0)) == 1
    assert aMap.Extent() == 2
    assert f(aMap.FindFromKey(K(10))) == 1.0


def test_NCollection_IndexedDataMapTest_ChangeValues():
    aMap = filled((10, 1.0), (20, 2.0))
    aMap.ChangeFromIndex(1).Copy(V(1.5))
    aMap.ChangeFromIndex(2).Copy(V(2.5))
    assert f(aMap.FindFromIndex(1)) == 1.5
    assert f(aMap.FindFromIndex(2)) == 2.5
    assert f(aMap.FindFromKey(K(10))) == 1.5
    assert f(aMap.FindFromKey(K(20))) == 2.5
    aMap.ChangeFromKey(K(10)).Copy(V(1.75))
    aMap.ChangeFromKey(K(20)).Copy(V(2.75))
    assert f(aMap.FindFromIndex(1)) == 1.75
    assert f(aMap.FindFromIndex(2)) == 2.75
    assert f(aMap.FindFromKey(K(10))) == 1.75
    assert f(aMap.FindFromKey(K(20))) == 2.75


def test_NCollection_IndexedDataMapTest_SeekTests():
    aMap = filled((10, 1.0), (20, 2.0))
    item1 = aMap.Seek(K(10))
    item2 = aMap.Seek(K(20))
    item3 = aMap.Seek(K(30))
    assert item1 is not None
    assert item2 is not None
    assert item3 is None
    assert f(item1) == 1.0
    assert f(item2) == 2.0
    changeItem1 = aMap.ChangeSeek(K(10))
    changeItem2 = aMap.ChangeSeek(K(20))
    changeItem3 = aMap.ChangeSeek(K(30))
    assert changeItem1 is not None
    assert changeItem2 is not None
    assert changeItem3 is None
    changeItem1.Copy(V(1.5))
    changeItem2.Copy(V(2.5))
    assert f(aMap.FindFromKey(K(10))) == 1.5
    assert f(aMap.FindFromKey(K(20))) == 2.5
    value = TCollection_AsciiString()
    assert aMap.FindFromKey(K(10), value)
    assert f(value) == 1.5
    assert not aMap.FindFromKey(K(30), value)


def test_NCollection_IndexedDataMapTest_RemoveLast():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    aMap.RemoveLast()
    assert aMap.Extent() == 2
    assert aMap.Contains(K(10))
    assert aMap.Contains(K(20))
    assert not aMap.Contains(K(30))
    assert aMap.FindIndex(K(10)) == 1
    assert aMap.FindIndex(K(20)) == 2


def test_NCollection_IndexedDataMapTest_RemoveFromIndex():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0), (40, 4.0))
    aMap.RemoveFromIndex(2)
    assert aMap.Extent() == 3
    assert aMap.Contains(K(10))
    assert not aMap.Contains(K(20))
    assert aMap.Contains(K(30))
    assert aMap.Contains(K(40))
    assert k(aMap.FindKey(2)) == 40
    assert f(aMap.FindFromIndex(2)) == 4.0
    assert k(aMap.FindKey(1)) == 10
    assert k(aMap.FindKey(3)) == 30


def test_NCollection_IndexedDataMapTest_RemoveKey():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    aMap.RemoveKey(K(20))
    assert aMap.Extent() == 2
    assert aMap.Contains(K(10))
    assert not aMap.Contains(K(20))
    assert aMap.Contains(K(30))
    aMap.RemoveKey(K(50))
    assert aMap.Extent() == 2


def test_NCollection_IndexedDataMapTest_Substitute():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    aMap.Substitute(2, K(25), V(2.5))
    assert aMap.Extent() == 3
    assert aMap.Contains(K(10))
    assert not aMap.Contains(K(20))
    assert aMap.Contains(K(25))
    assert aMap.Contains(K(30))
    assert aMap.FindIndex(K(10)) == 1
    assert aMap.FindIndex(K(25)) == 2
    assert aMap.FindIndex(K(30)) == 3
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert f(aMap.FindFromKey(K(25))) == 2.5
    assert f(aMap.FindFromKey(K(30))) == 3.0


def test_NCollection_IndexedDataMapTest_Swap():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    aMap.Swap(1, 3)
    assert aMap.Extent() == 3
    assert aMap.Contains(K(10))
    assert aMap.Contains(K(20))
    assert aMap.Contains(K(30))
    assert k(aMap.FindKey(1)) == 30
    assert k(aMap.FindKey(2)) == 20
    assert k(aMap.FindKey(3)) == 10
    assert aMap.FindIndex(K(10)) == 3
    assert aMap.FindIndex(K(20)) == 2
    assert aMap.FindIndex(K(30)) == 1
    assert f(aMap.FindFromIndex(1)) == 3.0
    assert f(aMap.FindFromIndex(2)) == 2.0
    assert f(aMap.FindFromIndex(3)) == 1.0
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert f(aMap.FindFromKey(K(20))) == 2.0
    assert f(aMap.FindFromKey(K(30))) == 3.0


def test_NCollection_IndexedDataMapTest_Clear():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    assert aMap.Extent() == 3
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Add(K(40), V(4.0)) == 1
    assert aMap.Extent() == 1


def test_NCollection_IndexedDataMapTest_CopyConstructor():
    aMap1 = filled((10, 1.0), (20, 2.0), (30, 3.0))
    aMap2 = IDMap(aMap1)
    assert aMap2.Extent() == 3
    for i, (key, value) in enumerate(((10, 1.0), (20, 2.0), (30, 3.0)), start=1):
        assert aMap2.Contains(K(key))
        assert aMap2.FindIndex(K(key)) == i
        assert f(aMap2.FindFromKey(K(key))) == value
    aMap1.Add(K(40), V(4.0))
    assert aMap1.Extent() == 4
    assert aMap2.Extent() == 3
    assert not aMap2.Contains(K(40))


def test_NCollection_IndexedDataMapTest_AssignmentOperator():
    aMap1 = filled((10, 1.0), (20, 2.0))
    aMap2 = filled((30, 3.0), (40, 4.0), (50, 5.0))
    aMap2.Assign(aMap1)
    assert aMap2.Extent() == 2
    assert aMap2.Contains(K(10))
    assert aMap2.Contains(K(20))
    assert not aMap2.Contains(K(30))
    assert not aMap2.Contains(K(40))
    assert not aMap2.Contains(K(50))
    assert f(aMap2.FindFromKey(K(10))) == 1.0
    assert f(aMap2.FindFromKey(K(20))) == 2.0


def test_NCollection_IndexedDataMapTest_Iterator():
    aMap = filled((10, 1.0), (20, 2.0), (30, 3.0))
    found = set()
    count = 0
    it = IDMap.Iterator(aMap)
    while it.More():
        found.add((k(it.Key()), f(it.Value())))
        count += 1
        it.Next()
    assert count == 3
    assert found == {(10, 1.0), (20, 2.0), (30, 3.0)}
    it = IDMap.Iterator(aMap)
    while it.More():
        aValue = it.ChangeValue()
        aValue.Copy(V(f(aValue) * 2))
        it.Next()
    assert f(aMap.FindFromKey(K(10))) == 2.0
    assert f(aMap.FindFromKey(K(20))) == 4.0
    assert f(aMap.FindFromKey(K(30))) == 6.0


def test_NCollection_IndexedDataMapTest_StringKeys():
    aStringMap = NCollection_IndexedDataMap[TCollection_AsciiString, int]()
    assert aStringMap.Add(TCollection_AsciiString("First"), 1) == 1
    assert aStringMap.Add(TCollection_AsciiString("Second"), 2) == 2
    assert aStringMap.Add(TCollection_AsciiString("Third"), 3) == 3
    assert aStringMap.FindIndex(TCollection_AsciiString("First")) == 1
    assert aStringMap.FindIndex(TCollection_AsciiString("Second")) == 2
    assert aStringMap.FindIndex(TCollection_AsciiString("Third")) == 3
    assert aStringMap.FindKey(1).IsEqual("First")
    assert aStringMap.FindKey(2).IsEqual("Second")
    assert aStringMap.FindKey(3).IsEqual("Third")
    assert aStringMap.FindFromKey(TCollection_AsciiString("First")) == 1
    assert aStringMap.FindFromKey(TCollection_AsciiString("Second")) == 2
    assert aStringMap.FindFromKey(TCollection_AsciiString("Third")) == 3


def test_NCollection_IndexedDataMapTest_Exchange():
    aMap1 = filled((10, 1.0), (20, 2.0))
    aMap2 = filled((30, 3.0), (40, 4.0), (50, 5.0))
    aMap1.Exchange(aMap2)
    assert aMap1.Extent() == 3
    for key, value in ((30, 3.0), (40, 4.0), (50, 5.0)):
        assert aMap1.Contains(K(key))
        assert f(aMap1.FindFromKey(K(key))) == value
    assert aMap2.Extent() == 2
    for key, value in ((10, 1.0), (20, 2.0)):
        assert aMap2.Contains(K(key))
        assert f(aMap2.FindFromKey(K(key))) == value


def test_NCollection_IndexedDataMapTest_ReSize():
    aMap = filled(*((i, i / 10.0) for i in range(1, 101)), buckets=3)
    assert aMap.Extent() == 100
    for i in range(1, 101):
        assert aMap.Contains(K(i))
        assert aMap.FindIndex(K(i)) == i
        assert f(aMap.FindFromKey(K(i))) == i / 10.0
    aMap.ReSize(200)
    assert aMap.Extent() == 100
    for i in range(1, 101):
        assert aMap.Contains(K(i))
        assert aMap.FindIndex(K(i)) == i
        assert f(aMap.FindFromKey(K(i))) == i / 10.0


def test_NCollection_IndexedDataMapTest_TryBound_NewKey():
    aMap = IDMap()
    aRef1 = aMap.TryBound(K(10), V(1.0))
    assert f(aRef1) == 1.0
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1
    aRef2 = aMap.TryBound(K(20), V(2.0))
    assert f(aRef2) == 2.0
    assert f(aMap.FindFromKey(K(20))) == 2.0
    assert aMap.Extent() == 2
    assert aMap.FindIndex(K(20)) == 2
    aRef1.Copy(V(1.5))
    assert f(aMap.FindFromKey(K(10))) == 1.5


def test_NCollection_IndexedDataMapTest_TryBound_ExistingKey():
    aMap = filled((10, 1.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    aRef = aMap.TryBound(K(10), V(999.0))
    assert f(aRef) == 1.0
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1
    aRef.Copy(V(1.5))
    assert f(aMap.FindFromKey(K(10))) == 1.5


def test_NCollection_IndexedDataMapTest_Bind_NewKey():
    aMap = IDMap()
    assert aMap.Bind(K(10), V(1.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1
    assert aMap.Bind(K(20), V(2.0))
    assert f(aMap.FindFromKey(K(20))) == 2.0
    assert aMap.Extent() == 2
    assert aMap.FindIndex(K(20)) == 2


def test_NCollection_IndexedDataMapTest_Bind_ExistingKey():
    aMap = IDMap()
    aMap.Bind(K(10), V(1.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert not aMap.Bind(K(10), V(999.0))
    assert f(aMap.FindFromKey(K(10))) == 999.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1


def test_NCollection_IndexedDataMapTest_Bound_NewKey():
    aMap = IDMap()
    pVal1 = aMap.Bound(K(10), V(1.0))
    assert pVal1 is not None
    assert f(pVal1) == 1.0
    assert f(aMap.FindFromKey(K(10))) == 1.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1
    pVal2 = aMap.Bound(K(20), V(2.0))
    assert pVal2 is not None
    assert f(pVal2) == 2.0
    assert f(aMap.FindFromKey(K(20))) == 2.0
    assert aMap.Extent() == 2
    assert aMap.FindIndex(K(20)) == 2
    pVal1.Copy(V(1.5))
    assert f(aMap.FindFromKey(K(10))) == 1.5


def test_NCollection_IndexedDataMapTest_Bound_ExistingKey():
    aMap = filled((10, 1.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    pVal = aMap.Bound(K(10), V(999.0))
    assert pVal is not None
    assert f(pVal) == 999.0
    assert f(aMap.FindFromKey(K(10))) == 999.0
    assert aMap.Extent() == 1
    assert aMap.FindIndex(K(10)) == 1
    pVal.Copy(V(1.5))
    assert f(aMap.FindFromKey(K(10))) == 1.5


def test_NCollection_IndexedDataMapTest_Bind_Bound_VsAdd_Behavior():
    aMap = IDMap()
    aMap.Add(K(10), V(1.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    aMap.Add(K(10), V(999.0))
    assert f(aMap.FindFromKey(K(10))) == 1.0
    aMap.Bind(K(10), V(2.0))
    assert f(aMap.FindFromKey(K(10))) == 2.0
    aMap.Bound(K(10), V(3.0))
    assert f(aMap.FindFromKey(K(10))) == 3.0
    aMap.TryBound(K(10), V(999.0))
    assert f(aMap.FindFromKey(K(10))) == 3.0


def test_NCollection_IndexedDataMapTest_ItemsIteration():
    aMap = IDMap()
    aMap.Add(K(1), "One")
    aMap.Add(K(2), "Two")
    aMap.Add(K(3), "Three")
    aFoundKeys = set()
    aFoundValues = set()
    for aKey, aValue in aMap.items():
        aFoundKeys.add(k(aKey))
        aFoundValues.add(aValue.ToCString())
    assert aFoundKeys == {1, 2, 3}
    assert aFoundValues == {"One", "Two", "Three"}


def test_NCollection_IndexedDataMapTest_ItemsStructuredBindings():
    aMap = IDMap()
    aMap.Add(K(10), "Ten")
    aMap.Add(K(20), "Twenty")
    aSum = 0
    for aKey, _aValue in aMap.items():
        aSum += k(aKey)
    assert aSum == 30


def test_NCollection_IndexedDataMapTest_ConstItemsIteration():
    aMap = IDMap()
    aMap.Add(K(1), "One")
    aMap.Add(K(2), "Two")
    aCount = 0
    for _aKey, _aValue in aMap.items():
        aCount += 1
    assert aCount == 2
