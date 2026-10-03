# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_PackedMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# Only NCollection_PackedMap<int> is bound (as TColStd_PackedMapOfInteger): the typed tests run for TypeParam = int.
# NCollection_PackedMapAlgo is not bound: its functions are used through the equivalent member functions.
# Skipped: MoveConstructor/MoveAssignment (move), NCollection_PackedMap64BitTest (int64_t/size_t not bound),
# ConfigFor64BitTypes; ConfigFor32BitTypes checks the int instantiation only (unsigned int not bound).
from nanocct.TColStd import TColStd_PackedMapOfInteger

PMap = TColStd_PackedMapOfInteger


def mk(*values):
    aMap = PMap()
    for v in values:
        aMap.Add(v)
    return aMap


def test_NCollection_PackedMapTypedTest_DefaultConstructor():
    aMap = PMap()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0


def test_NCollection_PackedMapTypedTest_ConstructorWithBuckets():
    aMap = PMap(100)
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0


def test_NCollection_PackedMapTypedTest_CopyConstructor():
    aMap1 = mk(1, 10, 100)
    aMap2 = PMap(aMap1)
    assert aMap2.Extent() == 3
    assert aMap2.Contains(1)
    assert aMap2.Contains(10)
    assert aMap2.Contains(100)
    aMap1.Add(1000)
    assert aMap1.Extent() == 4
    assert aMap2.Extent() == 3
    assert not aMap2.Contains(1000)


def test_NCollection_PackedMapTypedTest_CopyAssignment():
    aMap1 = mk(5, 15)
    aMap2 = mk(100, 200)
    aMap2.Assign(aMap1)
    assert aMap2.Extent() == 2
    assert aMap2.Contains(5)
    assert aMap2.Contains(15)
    assert not aMap2.Contains(100)


def test_NCollection_PackedMapTypedTest_AddAndContains():
    aMap = PMap()
    assert aMap.Add(10)
    assert aMap.Add(20)
    assert aMap.Add(30)
    assert aMap.Extent() == 3
    assert aMap.Contains(10)
    assert aMap.Contains(20)
    assert aMap.Contains(30)
    assert not aMap.Contains(40)


def test_NCollection_PackedMapTypedTest_AddDuplicate():
    aMap = PMap()
    assert aMap.Add(10)
    assert aMap.Extent() == 1
    assert not aMap.Add(10)
    assert aMap.Extent() == 1


def test_NCollection_PackedMapTypedTest_Remove():
    aMap = mk(10, 20, 30)
    assert aMap.Extent() == 3
    assert aMap.Remove(20)
    assert aMap.Extent() == 2
    assert not aMap.Contains(20)
    assert not aMap.Remove(20)
    assert not aMap.Remove(40)
    assert aMap.Extent() == 2


def test_NCollection_PackedMapTypedTest_Clear():
    aMap = mk(1, 2, 3)
    assert aMap.Extent() == 3
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    aMap.Add(100)
    assert aMap.Extent() == 1
    assert aMap.Contains(100)


def test_NCollection_PackedMapTypedTest_ZeroValue():
    aMap = PMap()
    assert aMap.Add(0)
    assert aMap.Contains(0)
    assert aMap.Extent() == 1
    assert aMap.Remove(0)
    assert not aMap.Contains(0)
    assert aMap.IsEmpty()


def test_NCollection_PackedMapTypedTest_ConsecutiveValues():
    aMap = PMap()
    aNbValues = 64
    for i in range(aNbValues):
        aMap.Add(i)
    assert aMap.Extent() == aNbValues
    for i in range(aNbValues):
        assert aMap.Contains(i)


def test_NCollection_PackedMapTypedTest_SparseValues():
    values = (0, 100, 1000, 10000, 100000)
    aMap = mk(*values)
    assert aMap.Extent() == 5
    for v in values:
        assert aMap.Contains(v)


def test_NCollection_PackedMapTypedTest_BlockBoundary():
    aBitsPerBlock = PMap.BitsPerBlock
    aMap = mk(aBitsPerBlock - 1, aBitsPerBlock, aBitsPerBlock + 1)
    assert aMap.Extent() == 3
    assert aMap.Contains(aBitsPerBlock - 1)
    assert aMap.Contains(aBitsPerBlock)
    assert aMap.Contains(aBitsPerBlock + 1)


def test_NCollection_PackedMapTypedTest_GetMinimalMapped():
    aMap = mk(50, 10, 100, 5, 75)
    assert aMap.GetMinimalMapped() == 5
    aMap.Remove(5)
    assert aMap.GetMinimalMapped() == 10


def test_NCollection_PackedMapTypedTest_GetMaximalMapped():
    aMap = mk(50, 10, 100, 5, 75)
    assert aMap.GetMaximalMapped() == 100
    aMap.Remove(100)
    assert aMap.GetMaximalMapped() == 75


def test_NCollection_PackedMapTypedTest_Union():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(3, 4, 5)
    aResult = PMap()
    aResult.Union(aMap1, aMap2)
    assert aResult.Extent() == 5
    for v in (1, 2, 3, 4, 5):
        assert aResult.Contains(v)


def test_NCollection_PackedMapTypedTest_Unite():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(3, 4, 5)
    assert aMap1.Unite(aMap2)
    assert aMap1.Extent() == 5
    for v in (1, 2, 3, 4, 5):
        assert aMap1.Contains(v)
    assert not aMap1.Unite(aMap2)


def test_NCollection_PackedMapTypedTest_UniteInPlace():
    aMap1 = mk(1, 2)
    aMap2 = mk(2, 3)
    aMap1.Unite(aMap2)
    assert aMap1.Extent() == 3
    for v in (1, 2, 3):
        assert aMap1.Contains(v)


def test_NCollection_PackedMapTypedTest_Intersection():
    aMap1 = mk(1, 2, 3, 4)
    aMap2 = mk(2, 3, 5, 6)
    aResult = PMap()
    aResult.Intersection(aMap1, aMap2)
    assert aResult.Extent() == 2
    assert aResult.Contains(2)
    assert aResult.Contains(3)
    assert not aResult.Contains(1)
    assert not aResult.Contains(4)


def test_NCollection_PackedMapTypedTest_Intersect():
    aMap1 = mk(1, 2, 3, 4)
    aMap2 = mk(2, 3, 5)
    assert aMap1.Intersect(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(2)
    assert aMap1.Contains(3)


def test_NCollection_PackedMapTypedTest_IntersectInPlace():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(2, 3, 4)
    aMap1.Intersect(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(2)
    assert aMap1.Contains(3)


def test_NCollection_PackedMapTypedTest_IntersectionDisjoint():
    aMap1 = mk(1, 2)
    aMap2 = mk(3, 4)
    aResult = PMap()
    aResult.Intersection(aMap1, aMap2)
    assert aResult.IsEmpty()


def test_NCollection_PackedMapTypedTest_Subtraction():
    aMap1 = mk(1, 2, 3, 4)
    aMap2 = mk(2, 3, 5)
    aResult = PMap()
    aResult.Subtraction(aMap1, aMap2)
    assert aResult.Extent() == 2
    assert aResult.Contains(1)
    assert aResult.Contains(4)
    assert not aResult.Contains(2)
    assert not aResult.Contains(3)


def test_NCollection_PackedMapTypedTest_Subtract():
    aMap1 = mk(1, 2, 3, 4)
    aMap2 = mk(2, 3, 5)
    assert aMap1.Subtract(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(1)
    assert aMap1.Contains(4)


def test_NCollection_PackedMapTypedTest_SubtractInPlace():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(2)
    aMap1.Subtract(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(1)
    assert aMap1.Contains(3)
    assert not aMap1.Contains(2)


def test_NCollection_PackedMapTypedTest_Difference():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(2, 3, 4)
    aResult = PMap()
    aResult.Difference(aMap1, aMap2)
    assert aResult.Extent() == 2
    assert aResult.Contains(1)
    assert aResult.Contains(4)
    assert not aResult.Contains(2)
    assert not aResult.Contains(3)


def test_NCollection_PackedMapTypedTest_Differ():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(2, 3, 4)
    assert aMap1.Differ(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(1)
    assert aMap1.Contains(4)


def test_NCollection_PackedMapTypedTest_DifferInPlace():
    aMap1 = mk(1, 2)
    aMap2 = mk(2, 3)
    aMap1.Differ(aMap2)
    assert aMap1.Extent() == 2
    assert aMap1.Contains(1)
    assert aMap1.Contains(3)
    assert not aMap1.Contains(2)


def test_NCollection_PackedMapTypedTest_IsEqual():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(1, 2, 3)
    assert aMap1.IsEqual(aMap2)
    aMap2.Add(4)
    assert not aMap1.IsEqual(aMap2)


def test_NCollection_PackedMapTypedTest_IsEqualEmpty():
    aMap1 = PMap()
    aMap2 = PMap()
    assert aMap1.IsEqual(aMap2)


def test_NCollection_PackedMapTypedTest_IsSubset():
    aMap1 = mk(1, 2)
    aMap2 = mk(1, 2, 3, 4)
    assert aMap1.IsSubset(aMap2)
    assert not aMap2.IsSubset(aMap1)


def test_NCollection_PackedMapTypedTest_IsSubsetSame():
    aMap1 = mk(1, 2)
    aMap2 = mk(1, 2)
    assert aMap1.IsSubset(aMap2)
    assert aMap2.IsSubset(aMap1)


def test_NCollection_PackedMapTypedTest_IsSubsetEmpty():
    aEmptyMap = PMap()
    aMap = mk(1)
    assert aEmptyMap.IsSubset(aMap)
    assert aEmptyMap.IsSubset(aEmptyMap)


def test_NCollection_PackedMapTypedTest_HasIntersection():
    aMap1 = mk(1, 2, 3)
    aMap2 = mk(3, 4, 5)
    assert aMap1.HasIntersection(aMap2)
    aMap3 = mk(10, 20)
    assert not aMap1.HasIntersection(aMap3)


def test_NCollection_PackedMapTypedTest_IteratorBasic():
    aMap = mk(10, 20, 30)
    aValues = []
    anIt = PMap.Iterator(aMap)
    while anIt.More():
        aValues.append(anIt.Key())
        anIt.Next()
    assert len(aValues) == 3
    assert 10 in aValues
    assert 20 in aValues
    assert 30 in aValues


def test_NCollection_PackedMapTypedTest_IteratorEmpty():
    aMap = PMap()
    aCount = 0
    anIt = PMap.Iterator(aMap)
    while anIt.More():
        aCount += 1
        anIt.Next()
    assert aCount == 0


def _count(anIt):
    aCount = 0
    while anIt.More():
        aCount += 1
        anIt.Next()
    return aCount


def test_NCollection_PackedMapTypedTest_IteratorReinitialize():
    aMap1 = mk(1, 2)
    aMap2 = mk(100, 200, 300)
    anIt = PMap.Iterator(aMap1)
    assert _count(anIt) == 2
    anIt.Initialize(aMap2)
    assert _count(anIt) == 3


def test_NCollection_PackedMapTypedTest_IteratorReset():
    aMap = mk(1, 2)
    anIt = PMap.Iterator(aMap)
    assert _count(anIt) == 2
    anIt.Reset()
    assert _count(anIt) == 2


def test_NCollection_PackedMapTypedTest_ReSize():
    aMap = PMap(1)
    for i in range(1000):
        aMap.Add(i)
    assert aMap.Extent() == 1000
    for i in range(1000):
        assert aMap.Contains(i)


def test_NCollection_PackedMapTypedTest_LargeValues():
    aMap = mk(1000000, 2000000, 3000000)
    assert aMap.Extent() == 3
    assert aMap.Contains(1000000)
    assert aMap.Contains(2000000)
    assert aMap.Contains(3000000)


def test_NCollection_PackedMapTypedTest_UnionWithSelf():
    aMap = mk(1, 2, 3)
    aResult = PMap()
    aResult.Union(aMap, aMap)
    assert aResult.Extent() == 3
    assert aResult.IsEqual(aMap)


def test_NCollection_PackedMapTypedTest_IntersectionWithSelf():
    aMap = mk(1, 2, 3)
    aResult = PMap()
    aResult.Intersection(aMap, aMap)
    assert aResult.Extent() == 3
    assert aResult.IsEqual(aMap)


def test_NCollection_PackedMapTypedTest_SubtractionFromSelf():
    aMap = mk(1, 2, 3)
    aResult = PMap()
    aResult.Subtraction(aMap, aMap)
    assert aResult.IsEmpty()


def test_NCollection_PackedMapTypedTest_DifferenceWithSelf():
    aMap = mk(1, 2, 3)
    aResult = PMap()
    aResult.Difference(aMap, aMap)
    assert aResult.IsEmpty()


def test_NCollection_PackedMapTypedTest_UnionWithEmpty():
    aMap = mk(1, 2)
    aEmpty = PMap()
    aResult = PMap()
    aResult.Union(aMap, aEmpty)
    assert aResult.IsEqual(aMap)


def test_NCollection_PackedMapTypedTest_IntersectionWithEmpty():
    aMap = mk(1, 2)
    aEmpty = PMap()
    aResult = PMap()
    aResult.Intersection(aMap, aEmpty)
    assert aResult.IsEmpty()


def test_NCollection_PackedMapTypedTest_SubtractionEmpty():
    aMap = mk(1, 2)
    aEmpty = PMap()
    aResult = PMap()
    aResult.Subtraction(aMap, aEmpty)
    assert aResult.IsEqual(aMap)
    aResult2 = PMap()
    aResult2.Subtraction(aEmpty, aMap)
    assert aResult2.IsEmpty()


def test_NCollection_PackedMapSignedTest_NegativeValues():
    aMap = mk(-1, -100, -1000)
    assert aMap.Extent() == 3
    assert aMap.Contains(-1)
    assert aMap.Contains(-100)
    assert aMap.Contains(-1000)
    assert not aMap.Contains(1)
    assert aMap.Remove(-100)
    assert aMap.Extent() == 2
    assert not aMap.Contains(-100)


def test_NCollection_PackedMapSignedTest_MixedPositiveNegative():
    aMap = mk(-50, 0, 50)
    assert aMap.Extent() == 3
    assert aMap.Contains(-50)
    assert aMap.Contains(0)
    assert aMap.Contains(50)


def test_NCollection_PackedMapSignedTest_MinMaxWithNegatives():
    aMap = mk(-100, -50, 0, 50, 100)
    assert aMap.GetMinimalMapped() == -100
    assert aMap.GetMaximalMapped() == 100


def test_NCollection_PackedMapConfigTest_ConfigFor32BitTypes():
    assert not PMap.Is64Bit
    assert PMap.BitsPerBlock == 32
