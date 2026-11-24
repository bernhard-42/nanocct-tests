# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_FlatDataMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_FlatDataMap<int, TCollection_AsciiString> / <int, int> are not bound. Every translated case except
# ChangeSeekMethod is substituted by NCollection_FlatDataMap[BRepGraph_ItemId, BRepGraph_ItemId], with an int key or
# value mapped one-to-one by I(i) == BRepGraph_ItemId(BRepGraph_NodeId(Kind.Face, i)) (read back through
# NodeId().Index) and a TCollection_AsciiString value by S(text) == BRepGraph_ItemId(BRepGraph_NodeId(Kind.Edge, n)),
# n the position of the text in NAMES (read back as the text); ItemIds compare by value (operator==), so the binding,
# lookup and iteration semantics tested are unchanged.
# ChangeSeekMethod assigns a whole value through the returned pointer, which an ItemId value cannot take (no public
# fields, operator= not bound): it is substituted by NCollection_FlatDataMap[BRepGraph_NodeId,
# BRepGraphInc_Storage.CachedShape] with key K(i) == BRepGraph_NodeId(Kind.Face, i) and value V(text) == a
# CachedShape of null Shape and StoredSubtreeGen = 1 + position of the text in NAMES; `*aPtr = value` assigns both
# fields of that aggregate.
# Not translated: MoveConstructor / MoveAssignment (move semantics), Assignment (operator= is not bound and the class
# has no Assign), LongProbeSequence / HasherConstructorCopy / HasherConstructorMove / CopyConstructorPreservesHasher
# (custom C++ hashers; GetHasher and the hasher constructors are not bound), Emplace* / Emplaced* / TryEmplace* /
# TryEmplaced* (not bound), ItemsModifyValue / ItemsIteratorEquality (the C++ Items() view is not bound; Python
# items() returns a list of copies).
import pytest

from nanocct.BRepGraph import BRepGraph_ItemId, BRepGraph_NodeId
from nanocct.BRepGraphInc import BRepGraphInc_Storage
from nanocct.NCollection import NCollection_FlatDataMap
from nanocct.Standard import Standard_NoSuchObject

DMap = NCollection_FlatDataMap[BRepGraph_ItemId, BRepGraph_ItemId]
CMap = NCollection_FlatDataMap[BRepGraph_NodeId, BRepGraphInc_Storage.CachedShape]
Kind = BRepGraph_NodeId.Kind
NAMES = ("One", "Two", "Three", "New One", "Modified One", "Ten", "Twenty")


def I(value):
    return BRepGraph_ItemId(BRepGraph_NodeId(Kind.Face, value))


def num(item):
    assert item.IsNode()
    assert item.NodeId().NodeKind == Kind.Face
    return item.NodeId().Index


def S(text):
    return BRepGraph_ItemId(BRepGraph_NodeId(Kind.Edge, NAMES.index(text)))


def text(item):
    assert item.IsNode()
    assert item.NodeId().NodeKind == Kind.Edge
    return NAMES[item.NodeId().Index]


def K(value):
    return BRepGraph_NodeId(Kind.Face, value)


def V(name):
    aValue = BRepGraphInc_Storage.CachedShape()
    aValue.StoredSubtreeGen = 1 + NAMES.index(name)
    return aValue


def vtext(value):
    assert value.Shape.IsNull()
    return NAMES[value.StoredSubtreeGen - 1]


def test_NCollection_FlatDataMapTest_DefaultConstructor():
    aMap = DMap()
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert aMap.Extent() == 0


def test_NCollection_FlatDataMapTest_BindingAndAccess():
    aMap = DMap()
    assert aMap.Bind(I(1), S("One"))
    assert aMap.Bind(I(2), S("Two"))
    assert aMap.Bind(I(3), S("Three"))
    assert not aMap.IsEmpty()
    assert aMap.Size() == 3
    assert text(aMap.Find(I(1))) == "One"
    assert text(aMap.Find(I(2))) == "Two"
    assert text(aMap.Find(I(3))) == "Three"
    assert aMap.IsBound(I(1))
    assert aMap.IsBound(I(2))
    assert aMap.IsBound(I(3))
    assert not aMap.IsBound(I(4))


def test_NCollection_FlatDataMapTest_SeekMethod():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aPtr = aMap.Seek(I(1))
    assert aPtr is not None
    assert text(aPtr) == "One"
    assert aMap.Seek(I(2)) is None


def test_NCollection_FlatDataMapTest_ChangeSeekMethod():
    aMap = CMap()
    aMap.Bind(K(1), V("One"))
    aPtr = aMap.ChangeSeek(K(1))
    assert aPtr is not None
    aNew = V("Modified One")
    aPtr.Shape = aNew.Shape
    aPtr.StoredSubtreeGen = aNew.StoredSubtreeGen
    assert vtext(aMap.Find(K(1))) == "Modified One"


def test_NCollection_FlatDataMapTest_Rebind():
    aMap = DMap()
    assert aMap.Bind(I(1), S("One"))
    assert text(aMap.Find(I(1))) == "One"
    assert not aMap.Bind(I(1), S("New One"))
    assert text(aMap.Find(I(1))) == "New One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_UnBind():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aMap.Bind(I(3), S("Three"))
    assert aMap.UnBind(I(2))
    assert aMap.Size() == 2
    assert not aMap.IsBound(I(2))
    assert not aMap.UnBind(I(4))
    assert aMap.Size() == 2


def test_NCollection_FlatDataMapTest_Clear():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aMap.Clear(False)
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert not aMap.IsBound(I(1))
    assert not aMap.IsBound(I(2))
    assert aMap.Capacity() > 0


def test_NCollection_FlatDataMapTest_ClearWithRelease():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aMap.Clear(True)
    assert aMap.IsEmpty()
    assert aMap.Capacity() == 0


def test_NCollection_FlatDataMapTest_CopyConstructor():
    aMap1 = DMap()
    aMap1.Bind(I(1), S("One"))
    aMap1.Bind(I(2), S("Two"))
    aMap2 = DMap(aMap1)
    assert aMap2.Size() == aMap1.Size()
    assert text(aMap1.Find(I(1))) == text(aMap2.Find(I(1)))
    assert text(aMap1.Find(I(2))) == text(aMap2.Find(I(2)))
    aMap1.Bind(I(1), S("Modified One"))
    assert text(aMap1.Find(I(1))) == "Modified One"
    assert text(aMap2.Find(I(1))) == "One"


def test_NCollection_FlatDataMapTest_Find_NonExisting():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    with pytest.raises(Standard_NoSuchObject):
        aMap.Find(I(2))
    with pytest.raises(Standard_NoSuchObject):
        aMap.ChangeFind(I(2))


def test_NCollection_FlatDataMapTest_IteratorAccess():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aMap.Bind(I(3), S("Three"))
    it = DMap.Iterator(aMap)
    foundKeys = set()
    foundValues = set()
    while it.More():
        foundKeys.add(num(it.Key()))
        foundValues.add(text(it.Value()))
        it.Next()
    assert len(foundKeys) == 3
    assert 1 in foundKeys
    assert 2 in foundKeys
    assert 3 in foundKeys
    assert len(foundValues) == 3
    assert "One" in foundValues
    assert "Two" in foundValues
    assert "Three" in foundValues


def test_NCollection_FlatDataMapTest_LargeDataSet():
    NUM_ELEMENTS = 10000
    aMap = DMap()
    for i in range(NUM_ELEMENTS):
        aMap.Bind(I(i), I(i * 2))
    assert aMap.Size() == NUM_ELEMENTS
    for i in range(NUM_ELEMENTS):
        assert aMap.IsBound(I(i)), f"Key {i} not found"
        assert num(aMap.Find(I(i))) == i * 2
    count = 0
    it = DMap.Iterator(aMap)
    while it.More():
        assert num(it.Value()) == num(it.Key()) * 2
        count += 1
        it.Next()
    assert count == NUM_ELEMENTS


def test_NCollection_FlatDataMapTest_UnBindAndRebind():
    aMap = DMap()
    for i in range(100):
        aMap.Bind(I(i), I(i))
    for i in range(0, 100, 2):
        assert aMap.UnBind(I(i))
    assert aMap.Size() == 50
    for i in range(0, 100, 2):
        aMap.Bind(I(i), I(i * 10))
    assert aMap.Size() == 100
    for i in range(100):
        if i % 2 == 0:
            assert num(aMap.Find(I(i))) == i * 10
        else:
            assert num(aMap.Find(I(i))) == i


def test_NCollection_FlatDataMapTest_IntegerKeyIntegerValue():
    aMap = DMap()
    aMap.Bind(I(10), I(100))
    aMap.Bind(I(20), I(200))
    aMap.Bind(I(30), I(300))
    assert num(aMap(I(10))) == 100
    assert num(aMap(I(20))) == 200
    assert num(aMap(I(30))) == 300


def test_NCollection_FlatDataMapTest_TryBindNewKey():
    aMap = DMap()
    assert aMap.TryBind(I(1), S("One"))
    assert aMap.Size() == 1
    assert text(aMap.Find(I(1))) == "One"


def test_NCollection_FlatDataMapTest_TryBindExistingKey():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    assert not aMap.TryBind(I(1), S("New One"))
    assert text(aMap.Find(I(1))) == "One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_TryBoundNewKey():
    aMap = DMap()
    aRef = aMap.TryBound(I(1), S("One"))
    assert text(aRef) == "One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_TryBoundExistingKey():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aRef = aMap.TryBound(I(1), S("New One"))
    assert text(aRef) == "One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_BoundNewKey():
    aMap = DMap()
    aRef = aMap.Bound(I(1), S("One"))
    assert text(aRef) == "One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_BoundExistingKey():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aRef = aMap.Bound(I(1), S("New One"))
    assert text(aRef) == "New One"
    assert aMap.Size() == 1


def test_NCollection_FlatDataMapTest_ItemsIteration():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aMap.Bind(I(3), S("Three"))
    aFoundKeys = set()
    aFoundValues = set()
    for aKey, aValue in aMap.items():
        aFoundKeys.add(num(aKey))
        aFoundValues.add(text(aValue))
    assert len(aFoundKeys) == 3
    assert 1 in aFoundKeys
    assert 2 in aFoundKeys
    assert 3 in aFoundKeys
    assert len(aFoundValues) == 3
    assert "One" in aFoundValues
    assert "Two" in aFoundValues
    assert "Three" in aFoundValues


def test_NCollection_FlatDataMapTest_ItemsStructuredBindings():
    aMap = DMap()
    aMap.Bind(I(10), S("Ten"))
    aMap.Bind(I(20), S("Twenty"))
    aSum = 0
    for aKey, _aValue in aMap.items():
        aSum += num(aKey)
    assert aSum == 30


def test_NCollection_FlatDataMapTest_ConstItemsIteration():
    aMap = DMap()
    aMap.Bind(I(1), S("One"))
    aMap.Bind(I(2), S("Two"))
    aCount = 0
    for _aKey, _aValue in aMap.items():
        aCount += 1
    assert aCount == 2
