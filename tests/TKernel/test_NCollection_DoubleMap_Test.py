# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_DoubleMap_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_DoubleMap<int, double> is not bound: substituted by NCollection_DoubleMap[int, TCollection_AsciiString]
# with Key2 = the text of the double (k2(1.0) == "1.0"); the bidirectional-map semantics tested are unchanged.
# Skipped: StringKeys (<AsciiString, AsciiString> not bound), ComplexKeys (custom C++ key types),
# TryBind_MoveSemantics (move), TryEmplace_* (not bound).
import pytest

from nanocct.NCollection import NCollection_DoubleMap
from nanocct.Standard import Standard_Failure, Standard_MultiplyDefined
from nanocct.TCollection import TCollection_AsciiString

DMap = NCollection_DoubleMap[int, TCollection_AsciiString]


def k2(value):
    return repr(float(value))


def find1(aMap, key1):
    return aMap.Find1(key1).ToCString()


def test_NCollection_DoubleMapTest_DefaultConstructor():
    aMap = DMap()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Size() == 0


def test_NCollection_DoubleMapTest_CustomBuckets():
    aMap = DMap(100)
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    assert aMap.Size() == 0


def test_NCollection_DoubleMapTest_BasicBindFind():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    aMap.Bind(30, k2(3.0))
    assert aMap.Extent() == 3
    assert aMap.IsBound1(10)
    assert aMap.IsBound1(20)
    assert aMap.IsBound1(30)
    assert not aMap.IsBound1(40)
    assert aMap.IsBound2(k2(1.0))
    assert aMap.IsBound2(k2(2.0))
    assert aMap.IsBound2(k2(3.0))
    assert not aMap.IsBound2(k2(4.0))
    assert find1(aMap, 10) == k2(1.0)
    assert find1(aMap, 20) == k2(2.0)
    assert find1(aMap, 30) == k2(3.0)
    assert aMap.Find2(k2(1.0)) == 10
    assert aMap.Find2(k2(2.0)) == 20
    assert aMap.Find2(k2(3.0)) == 30


def test_NCollection_DoubleMapTest_BindWithDuplicateKeys():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    assert aMap.Extent() == 1
    assert find1(aMap, 10) == k2(1.0)
    with pytest.raises(Standard_Failure):
        aMap.Bind(10, k2(2.0))
    assert aMap.Extent() == 1
    assert find1(aMap, 10) == k2(1.0)
    assert not aMap.IsBound2(k2(2.0))
    with pytest.raises(Standard_Failure):
        aMap.Bind(20, k2(1.0))
    assert aMap.Extent() == 1
    assert not aMap.IsBound1(20)


def test_NCollection_DoubleMapTest_UnbindTest():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    aMap.Bind(30, k2(3.0))
    assert aMap.Extent() == 3
    aMap.UnBind1(20)
    assert aMap.Extent() == 2
    assert not aMap.IsBound1(20)
    assert not aMap.IsBound2(k2(2.0))
    aMap.UnBind2(k2(3.0))
    assert aMap.Extent() == 1
    assert not aMap.IsBound1(30)
    assert not aMap.IsBound2(k2(3.0))
    aMap.UnBind1(40)
    assert aMap.Extent() == 1
    aMap.UnBind2(k2(4.0))
    assert aMap.Extent() == 1


def test_NCollection_DoubleMapTest_Clear():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    aMap.Bind(30, k2(3.0))
    assert aMap.Extent() == 3
    aMap.Clear()
    assert aMap.IsEmpty()
    assert aMap.Extent() == 0
    aMap.Bind(40, k2(4.0))
    assert aMap.Extent() == 1


def test_NCollection_DoubleMapTest_SeekTests():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    key2 = aMap.Seek1(10)
    assert key2 is not None
    assert key2.ToCString() == k2(1.0)
    key1 = aMap.Seek2(k2(2.0))
    assert key1 is not None
    assert key1 == 20
    assert aMap.Seek1(30) is None
    assert aMap.Seek2(k2(3.0)) is None


def test_NCollection_DoubleMapTest_CopyConstructor():
    aMap1 = DMap()
    aMap1.Bind(10, k2(1.0))
    aMap1.Bind(20, k2(2.0))
    aMap1.Bind(30, k2(3.0))
    aMap2 = DMap(aMap1)
    assert aMap2.Extent() == 3
    for key1, value in ((10, 1.0), (20, 2.0), (30, 3.0)):
        assert aMap2.IsBound1(key1)
        assert aMap2.IsBound2(k2(value))
    aMap1.Bind(40, k2(4.0))
    assert aMap1.Extent() == 4
    assert aMap2.Extent() == 3
    assert not aMap2.IsBound1(40)
    assert not aMap2.IsBound2(k2(4.0))


def test_NCollection_DoubleMapTest_AssignmentOperator():
    aMap1 = DMap()
    aMap2 = DMap()
    aMap1.Bind(10, k2(1.0))
    aMap1.Bind(20, k2(2.0))
    aMap2.Bind(30, k2(3.0))
    aMap2.Bind(40, k2(4.0))
    aMap2.Bind(50, k2(5.0))
    aMap2.Assign(aMap1)
    assert aMap2.Extent() == 2
    assert aMap2.IsBound1(10)
    assert aMap2.IsBound1(20)
    assert not aMap2.IsBound1(30)
    assert not aMap2.IsBound1(40)
    assert not aMap2.IsBound1(50)
    assert aMap2.IsBound2(k2(1.0))
    assert aMap2.IsBound2(k2(2.0))
    assert not aMap2.IsBound2(k2(3.0))
    assert not aMap2.IsBound2(k2(4.0))
    assert not aMap2.IsBound2(k2(5.0))


def test_NCollection_DoubleMapTest_ReSize():
    aMap = DMap(3)
    for i in range(1, 101):
        aMap.Bind(i, k2(i / 10.0))
    assert aMap.Extent() == 100
    for i in range(1, 101):
        assert aMap.IsBound1(i)
        assert aMap.IsBound2(k2(i / 10.0))
        assert find1(aMap, i) == k2(i / 10.0)
        assert aMap.Find2(k2(i / 10.0)) == i


def test_NCollection_DoubleMapTest_Exchange():
    aMap1 = DMap()
    aMap2 = DMap()
    aMap1.Bind(10, k2(1.0))
    aMap1.Bind(20, k2(2.0))
    aMap2.Bind(30, k2(3.0))
    aMap2.Bind(40, k2(4.0))
    aMap2.Bind(50, k2(5.0))
    aMap1.Exchange(aMap2)
    assert aMap1.Extent() == 3
    for key1, value in ((30, 3.0), (40, 4.0), (50, 5.0)):
        assert aMap1.IsBound1(key1)
        assert aMap1.IsBound2(k2(value))
    assert aMap2.Extent() == 2
    for key1, value in ((10, 1.0), (20, 2.0)):
        assert aMap2.IsBound1(key1)
        assert aMap2.IsBound2(k2(value))


def test_NCollection_DoubleMapTest_Iterator():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    aMap.Bind(30, k2(3.0))
    found = set()
    count = 0
    it = DMap.Iterator(aMap)
    while it.More():
        found.add((it.Key1(), it.Key2().ToCString()))
        count += 1
        it.Next()
    assert count == 3
    assert found == {(10, k2(1.0)), (20, k2(2.0)), (30, k2(3.0))}


def test_NCollection_DoubleMapTest_TryBind_NewKeys():
    aMap = DMap()
    assert aMap.TryBind(10, k2(1.0))
    assert aMap.Extent() == 1
    assert aMap.IsBound1(10)
    assert aMap.IsBound2(k2(1.0))
    assert find1(aMap, 10) == k2(1.0)
    assert aMap.Find2(k2(1.0)) == 10
    assert aMap.TryBind(20, k2(2.0))
    assert aMap.Extent() == 2
    assert aMap.IsBound1(20)
    assert aMap.IsBound2(k2(2.0))


def test_NCollection_DoubleMapTest_TryBind_ExistingKey1():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    assert aMap.Extent() == 1
    assert not aMap.TryBind(10, k2(999.0))
    assert aMap.Extent() == 1
    assert find1(aMap, 10) == k2(1.0)
    assert not aMap.IsBound2(k2(999.0))


def test_NCollection_DoubleMapTest_TryBind_ExistingKey2():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    assert aMap.Extent() == 1
    assert not aMap.TryBind(999, k2(1.0))
    assert aMap.Extent() == 1
    assert aMap.Find2(k2(1.0)) == 10
    assert not aMap.IsBound1(999)


def test_NCollection_DoubleMapTest_TryBind_BothKeysExist():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    aMap.Bind(20, k2(2.0))
    assert aMap.Extent() == 2
    assert not aMap.TryBind(10, k2(2.0))
    assert aMap.Extent() == 2
    assert find1(aMap, 10) == k2(1.0)
    assert aMap.Find2(k2(2.0)) == 20


def test_NCollection_DoubleMapTest_TryBind_VsBindException():
    aMap = DMap()
    aMap.Bind(10, k2(1.0))
    with pytest.raises(Standard_MultiplyDefined):
        aMap.Bind(10, k2(2.0))
    with pytest.raises(Standard_MultiplyDefined):
        aMap.Bind(20, k2(1.0))
    assert not aMap.TryBind(10, k2(3.0))
    assert not aMap.TryBind(30, k2(1.0))
    assert aMap.Extent() == 1
