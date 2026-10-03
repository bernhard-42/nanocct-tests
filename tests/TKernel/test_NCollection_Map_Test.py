# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_Map_Test.cxx (LGPL-2.1 with the OCCT exception)
# Skipped: Emplace/Emplaced/Contained (not bound), custom hashers, STL begin()/end() iterator tests.
# NCollection_MapAlgo is not bound; its Union/Intersection/... are used through the equivalent NCollection_Map members.
from nanocct.NCollection import NCollection_Map

MapInt = NCollection_Map[int]


def test_NCollection_MapTest_DefaultConstructor():
    aMap = MapInt(101)
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert aMap.Extent() == 0
    assert aMap.NbBuckets() == 101


def test_NCollection_MapTest_ConstructorWithBuckets():
    nbBuckets = 100
    aMap = MapInt(nbBuckets)
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert aMap.Extent() == 0
    assert aMap.NbBuckets() == nbBuckets


def test_NCollection_MapTest_AddAndContains():
    aMap = MapInt()
    assert aMap.Add(10)
    assert aMap.Add(20)
    assert aMap.Add(30)
    assert not aMap.Add(10)
    assert not aMap.Add(20)
    assert aMap.Size() == 3
    assert aMap.Contains(10)
    assert aMap.Contains(20)
    assert aMap.Contains(30)
    assert not aMap.Contains(40)


def test_NCollection_MapTest_Remove():
    aMap = MapInt()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    assert aMap.Remove(20)
    assert aMap.Size() == 2
    assert not aMap.Contains(20)
    assert aMap.Contains(10)
    assert aMap.Contains(30)
    assert not aMap.Remove(40)
    assert aMap.Size() == 2


def test_NCollection_MapTest_Clear():
    aMap = MapInt()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    assert not aMap.IsEmpty()
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Size() == 0
    assert not aMap.Contains(10)
    assert not aMap.Contains(20)
    assert not aMap.Contains(30)


def test_NCollection_MapTest_Assignment():
    aMap1 = MapInt()
    aMap1.Add(10)
    aMap1.Add(20)
    aMap1.Add(30)
    aMap2 = MapInt()
    aMap2.Assign(aMap1)
    assert aMap1.Size() == aMap2.Size()
    assert aMap2.Contains(10)
    assert aMap2.Contains(20)
    assert aMap2.Contains(30)
    aMap1.Add(40)
    aMap1.Remove(10)
    assert aMap1.Size() == 3
    assert aMap2.Size() == 3
    assert aMap2.Contains(10)
    assert not aMap1.Contains(10)
    assert aMap1.Contains(40)
    assert not aMap2.Contains(40)


def test_NCollection_MapTest_IteratorAccess():
    aMap = MapInt()
    aMap.Add(10)
    aMap.Add(20)
    aMap.Add(30)
    foundKeys = set()
    it = MapInt.Iterator(aMap)
    while it.More():
        foundKeys.add(it.Value())
        it.Next()
    assert foundKeys == {10, 20, 30}


def test_NCollection_MapTest_Resize():
    aMap = MapInt(10)
    for i in range(100):
        aMap.Add(i)
    assert aMap.Size() == 100
    elements = []
    it = MapInt.Iterator(aMap)
    while it.More():
        elements.append(it.Value())
        it.Next()
    aMap.ReSize(200)
    assert aMap.Size() == 100
    for element in elements:
        assert aMap.Contains(element)


def test_NCollection_MapTest_ExhaustiveIterator():
    NUM_ELEMENTS = 1000
    aMap = MapInt()
    for i in range(NUM_ELEMENTS):
        aMap.Add(i)
    assert aMap.Size() == NUM_ELEMENTS
    count = 0
    total = 0
    it = MapInt.Iterator(aMap)
    while it.More():
        total += it.Value()
        count += 1
        it.Next()
    assert count == NUM_ELEMENTS
    assert total == NUM_ELEMENTS * (NUM_ELEMENTS - 1) // 2


def test_NCollection_MapTest_OCC24271_BooleanOperations():
    aLeftLower, aLeftUpper = 1, 10
    aRightLower, aRightUpper = 5, 15
    aMapLeft = MapInt()
    for k in range(aLeftLower, aLeftUpper + 1):
        aMapLeft.Add(k)
    aMapRight = MapInt()
    for k in range(aRightLower, aRightUpper + 1):
        aMapRight.Add(k)

    assert not aMapLeft.Contains(aMapRight)
    assert not aMapRight.Contains(aMapLeft)

    aMapUnion = MapInt()
    aMapUnion.Union(aMapLeft, aMapRight)
    assert aMapUnion.Extent() == aRightUpper - aLeftLower + 1
    for k in range(aLeftLower, aRightUpper + 1):
        assert aMapUnion.Contains(k)

    aMapSect = MapInt()
    aMapSect.Intersection(aMapLeft, aMapRight)
    assert aMapSect.Extent() == aLeftUpper - aRightLower + 1
    for k in range(aRightLower, aLeftUpper + 1):
        assert aMapSect.Contains(k)
    assert aMapLeft.Contains(aMapSect)
    assert aMapRight.Contains(aMapSect)

    aMapSubsLR = MapInt()
    aMapSubsLR.Subtraction(aMapLeft, aMapRight)
    assert aMapSubsLR.Extent() == aRightLower - aLeftLower
    for k in range(aLeftLower, aRightLower):
        assert aMapSubsLR.Contains(k)

    aMapSubsRL = MapInt()
    aMapSubsRL.Subtraction(aMapRight, aMapLeft)
    assert aMapSubsRL.Extent() == aRightUpper - aLeftUpper
    for k in range(aLeftUpper + 1, aRightUpper + 1):
        assert aMapSubsRL.Contains(k)

    aMapDiff = MapInt()
    aMapDiff.Difference(aMapLeft, aMapRight)
    assert aMapDiff.Extent() == aRightLower - aLeftLower + aRightUpper - aLeftUpper
    for k in range(aLeftLower, aRightLower):
        assert aMapDiff.Contains(k)
    for k in range(aLeftUpper + 1, aRightUpper + 1):
        assert aMapDiff.Contains(k)

    aMapSwap = MapInt()
    aMapSwap.Exchange(aMapSect)
    for k in range(aRightLower, aLeftUpper + 1):
        assert aMapSwap.Contains(k)
    assert aMapSect.IsEmpty()


def test_NCollection_MapTest_RangeBasedForLoop():
    aMap = MapInt()
    aMap.Add(100)
    aMap.Add(200)
    aMap.Add(300)
    aFoundKeys = set()
    for aKey in aMap:
        aFoundKeys.add(aKey)
    assert aFoundKeys == {100, 200, 300}
