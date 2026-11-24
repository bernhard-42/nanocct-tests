# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_FlatMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_FlatMap<int> / <TCollection_AsciiString> are not bound: every translated case is substituted by
# NCollection_FlatMap[BRepGraph_NodeId], int keys mapped one-to-one by K(i) == BRepGraph_NodeId(Kind.Face, i) (read
# back through .Index), the TCollection_AsciiString keys of AddedNewKey, AddedExistingKey and ChangeSeekModify by
# S(text) == BRepGraph_NodeId(Kind.Edge, n) ("Hello" -> 0, "World" -> 1); the keys compare by value (operator==),
# so the set semantics tested are unchanged.
# Not translated: MoveConstructor (move semantics), LongProbeSequence / HasherConstructorCopy / HasherConstructorMove /
# CopyConstructorPreservesHasher (custom C++ hashers; GetHasher and the hasher constructors are not bound),
# StringKeys (tests TCollection_AsciiString as the key type), EmplaceNewKey / EmplaceExistingKey / EmplacedNewKey /
# EmplacedExistingKey (Emplace/Emplaced not bound).
from nanocct.BRepGraph import BRepGraph_NodeId
from nanocct.NCollection import NCollection_FlatMap

FMap = NCollection_FlatMap[BRepGraph_NodeId]
Kind = BRepGraph_NodeId.Kind
NAMES = ("Hello", "World")


def K(value):
    return BRepGraph_NodeId(Kind.Face, value)


def num(key):
    assert key.NodeKind == Kind.Face
    return key.Index


def S(text):
    return BRepGraph_NodeId(Kind.Edge, NAMES.index(text))


def test_NCollection_FlatMapTest_DefaultConstructor():
    aMap = FMap()
    assert aMap.IsEmpty()
    assert aMap.Size() == 0


def test_NCollection_FlatMapTest_AddAndContains():
    aMap = FMap()
    assert aMap.Add(K(1))
    assert aMap.Add(K(2))
    assert aMap.Add(K(3))
    assert not aMap.Add(K(1))
    assert aMap.Size() == 3
    assert aMap.Contains(K(1))
    assert aMap.Contains(K(2))
    assert aMap.Contains(K(3))
    assert not aMap.Contains(K(4))


def test_NCollection_FlatMapTest_Remove():
    aMap = FMap()
    aMap.Add(K(1))
    aMap.Add(K(2))
    aMap.Add(K(3))
    assert aMap.Remove(K(2))
    assert aMap.Size() == 2
    assert not aMap.Contains(K(2))
    assert not aMap.Remove(K(4))
    assert aMap.Size() == 2


def test_NCollection_FlatMapTest_Clear():
    aMap = FMap()
    aMap.Add(K(1))
    aMap.Add(K(2))
    aMap.Clear()
    assert aMap.IsEmpty()


def test_NCollection_FlatMapTest_CopyConstructor():
    aMap1 = FMap()
    aMap1.Add(K(1))
    aMap1.Add(K(2))
    aMap1.Add(K(3))
    aMap2 = FMap(aMap1)
    assert aMap2.Size() == aMap1.Size()
    assert aMap2.Contains(K(1))
    assert aMap2.Contains(K(2))
    assert aMap2.Contains(K(3))


def test_NCollection_FlatMapTest_Iterator():
    aMap = FMap()
    aMap.Add(K(10))
    aMap.Add(K(20))
    aMap.Add(K(30))
    foundKeys = set()
    it = FMap.Iterator(aMap)
    while it.More():
        foundKeys.add(num(it.Key()))
        it.Next()
    assert len(foundKeys) == 3
    assert 10 in foundKeys
    assert 20 in foundKeys
    assert 30 in foundKeys


def test_NCollection_FlatMapTest_LargeDataSet():
    NUM_ELEMENTS = 10000
    aMap = FMap()
    for i in range(NUM_ELEMENTS):
        aMap.Add(K(i))
    assert aMap.Size() == NUM_ELEMENTS
    for i in range(NUM_ELEMENTS):
        assert aMap.Contains(K(i)), f"Key {i} not found"


def test_NCollection_FlatMapTest_AddedNewKey():
    aMap = FMap()
    aRef = aMap.Added(S("Hello"))
    assert aRef == S("Hello")
    assert aMap.Size() == 1


def test_NCollection_FlatMapTest_AddedExistingKey():
    aMap = FMap()
    aMap.Add(S("Hello"))
    aRef = aMap.Added(S("Hello"))
    assert aRef == S("Hello")
    assert aMap.Size() == 1


def test_NCollection_FlatMapTest_SeekFound():
    aMap = FMap()
    aMap.Add(K(10))
    aMap.Add(K(20))
    aMap.Add(K(30))
    pKey = aMap.Seek(K(10))
    assert pKey is not None
    assert num(pKey) == 10
    pKey = aMap.Seek(K(30))
    assert pKey is not None
    assert num(pKey) == 30


def test_NCollection_FlatMapTest_SeekNotFound():
    aMap = FMap()
    aMap.Add(K(10))
    pKey = aMap.Seek(K(99))
    assert pKey is None
    anEmptyMap = FMap()
    assert anEmptyMap.Seek(K(10)) is None


def test_NCollection_FlatMapTest_ChangeSeekModify():
    aMap = FMap()
    aMap.Add(S("Hello"))
    aMap.Add(S("World"))
    pKey = aMap.ChangeSeek(S("Hello"))
    assert pKey is not None
    assert pKey == S("Hello")


def test_NCollection_FlatMapTest_ChangeSeekNotFound():
    aMap = FMap()
    aMap.Add(K(10))
    pKey = aMap.ChangeSeek(K(99))
    assert pKey is None


def test_NCollection_FlatMapTest_IteratorEquality():
    aMap = FMap()
    aMap.Add(K(1))
    aMap.Add(K(2))
    aMap.Add(K(3))
    anIt1 = FMap.Iterator(aMap)
    anIt2 = FMap.Iterator(aMap)
    anEndIt = FMap.Iterator()
    assert anIt1.IsEqual(anIt2)
    assert not anIt1.IsEqual(anEndIt)
    anIt2.Next()
    assert not anIt1.IsEqual(anIt2)
    anIt3 = FMap.Iterator(aMap)
    anIt3.Next()
    assert anIt2.IsEqual(anIt3)
    anEndIt2 = FMap.Iterator()
    assert anEndIt.IsEqual(anEndIt2)
