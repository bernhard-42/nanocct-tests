# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_LinearVector_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Not translated: move semantics, STL algorithms, EmplaceAppend (not bound), Data() (not bound), and every test
# with std::string, TCollection_AsciiString, MoveOnly or MultiArg elements (those instantiations are not bound).
# ChangeValue/ChangeFirst/ChangeLast of a scalar element are not bound; writes go through v[i] / SetValue.

import pytest

from nanocct.NCollection import NCollection_LinearVector
from nanocct.Standard import Standard_Failure

LV = NCollection_LinearVector[int]


def _make(*values):
    v = LV()
    for x in values:
        v.Append(x)
    return v


def test_NCollection_LinearVectorTest_DefaultConstructor():
    v = LV()
    assert v.Size() == 0
    assert v.IsEmpty()
    assert v.Capacity() == 0


def test_NCollection_LinearVectorTest_ReserveConstructor():
    v = LV(100)
    assert v.Size() == 0
    assert v.IsEmpty()
    assert v.Capacity() >= 100


def test_NCollection_LinearVectorTest_Append():
    v = _make(10, 20, 30)
    assert v.Size() == 3
    assert not v.IsEmpty()
    assert v(0) == 10
    assert v(1) == 20
    assert v(2) == 30


def test_NCollection_LinearVectorTest_Appended():
    # Appended() returns int& in C++; Python gets a copy, so write through the new index
    v = LV()
    v.Appended()
    v[0] = 42
    assert v.Size() == 1
    assert v(0) == 42


def test_NCollection_LinearVectorTest_SetValue():
    v = _make(10, 20)
    v.SetValue(0, 99)
    assert v(0) == 99
    v.SetValue(5, 55)
    assert v.Size() == 6
    assert v(5) == 55
    assert v(3) == 0


def test_NCollection_LinearVectorTest_ValueAccess():
    v = _make(10, 20, 30)
    assert v.Value(0) == 10
    assert v.Value(1) == 20
    assert v.Value(2) == 30
    v[1] = 99
    assert v(1) == 99
    assert v(0) == v[0]
    assert v(1) == v[1]
    assert v(2) == v[2]
    v[2] = 77
    assert v.Value(2) == 77


def test_NCollection_LinearVectorTest_FirstLast():
    v = _make(10, 20, 30)
    assert v.First() == 10
    assert v.Last() == 30
    v[0] = 99
    v[v.Size() - 1] = 88
    assert v(0) == 99
    assert v(2) == 88


def test_NCollection_LinearVectorTest_CopyConstructor():
    v = _make(1, 2, 3)
    cp = LV(v)
    assert cp.Size() == 3
    assert cp(0) == 1
    assert cp(1) == 2
    assert cp(2) == 3
    cp[0] = 99
    assert v(0) == 1


def test_NCollection_LinearVectorTest_Reserve():
    v = _make(1, 2)
    v.Reserve(100)
    assert v.Size() == 2
    assert v.Capacity() >= 100
    assert v(0) == 1
    assert v(1) == 2
    v.Reserve(5)
    assert v.Capacity() >= 100


def test_NCollection_LinearVectorTest_Resize():
    v = _make(1, 2, 3)
    v.Resize(5)
    assert v.Size() == 5
    assert v(0) == 1
    assert v(1) == 2
    assert v(2) == 3
    assert v(3) == 0
    assert v(4) == 0
    v.Resize(2)
    assert v.Size() == 2
    assert v(0) == 1
    assert v(1) == 2


def test_NCollection_LinearVectorTest_Resize_WithValue():
    v = _make(1, 2)
    v.Resize(5, -1)
    assert v.Size() == 5
    assert list(v) == [1, 2, -1, -1, -1]
    v.Resize(3, -1)
    assert v.Size() == 3
    assert list(v) == [1, 2, -1]


def test_NCollection_LinearVectorTest_EraseLast():
    v = _make(1, 2, 3)
    v.EraseLast()
    assert v.Size() == 2
    assert v(0) == 1
    assert v(1) == 2


def test_NCollection_LinearVectorTest_EraseSingle():
    v = _make(10, 20, 30, 40)
    v.Erase(1)
    assert v.Size() == 3
    assert list(v) == [10, 30, 40]
    v.Erase(0)
    assert v.Size() == 2
    assert list(v) == [30, 40]


def test_NCollection_LinearVectorTest_EraseRange():
    v = _make(*[i * 10 for i in range(6)])
    v.Erase(1, 4)
    assert v.Size() == 3
    assert list(v) == [0, 40, 50]


def test_NCollection_LinearVectorTest_InsertBefore():
    v = _make(10, 30)
    v.InsertBefore(0, 5)
    assert v.Size() == 3
    assert list(v) == [5, 10, 30]
    v.InsertBefore(2, 20)
    assert v.Size() == 4
    assert list(v) == [5, 10, 20, 30]
    v.InsertBefore(4, 40)
    assert v.Size() == 5
    assert v(4) == 40


def test_NCollection_LinearVectorTest_InsertAfter():
    v = _make(10, 30)
    v.InsertAfter(0, 20)
    assert v.Size() == 3
    assert list(v) == [10, 20, 30]


def test_NCollection_LinearVectorTest_Clear():
    v = _make(1, 2, 3)
    cap = v.Capacity()
    v.Clear(False)
    assert v.Size() == 0
    assert v.IsEmpty()
    assert v.Capacity() == cap
    v.Append(10)
    v.Clear(True)
    assert v.Size() == 0
    assert v.Capacity() == 0


def test_NCollection_LinearVectorTest_IteratorRangeFor():
    v = _make(1, 2, 3)
    total = 0
    for val in v:
        total += val
    assert total == 6
    for i in range(v.Size()):
        v[i] *= 10
    assert v(0) == 10
    assert v(1) == 20
    assert v(2) == 30


def test_NCollection_LinearVectorTest_TrivialTypeGrowth():
    v = NCollection_LinearVector[float]()
    for i in range(100):
        v.Append(float(i))
    assert v.Size() == 100
    for i in range(100):
        assert abs(v(i) - float(i)) <= 1e-15


def test_NCollection_LinearVectorTest_EmptyOperations():
    v = LV()
    v.EraseLast()
    assert v.Size() == 0
    v.Clear(False)
    assert v.Size() == 0
    v.Clear(True)
    assert v.Size() == 0
    assert v.Capacity() == 0


def test_NCollection_LinearVectorTest_LargeAppend():
    v = LV()
    count = 10000
    for i in range(count):
        v.Append(i)
    assert v.Size() == count
    for i in range(count):
        assert v(i) == i


def test_NCollection_LinearVectorTest_BoundsAccess():
    v = _make(10, 20, 30)
    assert v.Size() == 3
    assert v(0) == 10
    assert v(v.Size() - 1) == 30


def test_NCollection_LinearVectorTest_ReserveZero_NoEffect():
    v = _make(1)
    cap = v.Capacity()
    v.Reserve(0)
    assert v.Capacity() == cap
    assert v.Size() == 1
    assert v(0) == 1


def test_NCollection_LinearVectorTest_ReserveDecreasing_NoShrink():
    v = LV()
    v.Reserve(100)
    assert v.Capacity() >= 100
    cap = v.Capacity()
    v.Reserve(10)
    assert v.Capacity() == cap


def test_NCollection_LinearVectorTest_InsertBeforeAtEnd_EquivalentToAppend():
    v = _make(1, 2)
    v.InsertBefore(v.Size(), 3)
    assert v.Size() == 3
    assert list(v) == [1, 2, 3]


def test_NCollection_LinearVectorTest_InsertBeforeZero_InsertsAtFront():
    v = _make(2, 3)
    v.InsertBefore(0, 1)
    assert v.Size() == 3
    assert list(v) == [1, 2, 3]


def test_NCollection_LinearVectorTest_OutOfRangeIndicesThrow():
    v = _make(1)
    out = 5
    with pytest.raises(Standard_Failure):
        v.Value(out)
    # ChangeValue of an int element is not bound; v[i] = x is SetValue, which extends instead of raising
    with pytest.raises(Standard_Failure):
        v.InsertAfter(out, 1)
    with pytest.raises(Standard_Failure):
        v.Erase(out)


def test_NCollection_LinearVectorTest_Constructor_SizeAndValue():
    v = LV(5, 42)
    assert v.Size() == 5
    for i in range(v.Size()):
        assert v[i] == 42


def test_NCollection_LinearVectorTest_Constructor_SizeZero_IsEmpty():
    v = LV(0, 99)
    assert v.IsEmpty()


def test_NCollection_LinearVectorTest_OcctApiCoverage():
    v = LV()
    assert v.IsEmpty()
    assert v.Size() == 0
    v.Append(10)
    # EmplaceAppend(20) + write through the returned reference: Append + index write
    v.Append(20)
    v[1] = 30
    assert not v.IsEmpty()
    assert v.Size() == 2
    assert v.Capacity() >= v.Size()
    assert v.First() == 10
    assert v.Last() == 30
    assert v.Value(0) == 10
    assert v.Value(1) == 30
    v.Reserve(8)
    assert v.Capacity() >= 8
    v.Resize(4, 7)
    assert v.Size() == 4
    assert v[2] == 7
    assert v[3] == 7
    v.EraseLast()
    assert v.Size() == 3
    assert v.Last() == 7
    v.Clear()
    assert v.IsEmpty()
    assert v.Size() == 0


def test_NCollection_LinearVectorTest_ToArray1_SamePointer():
    v = _make(*[i * 10 for i in range(10)])
    arr = v.ToArray1()
    assert arr.Size() == 10
    # Data() is not bound; shared memory is shown by a write through the Array1 instead
    arr[arr.Lower()] = -1
    assert v[0] == -1


def test_NCollection_LinearVectorTest_ToArray1_ModifyReflectsInSource():
    v = _make(1, 2, 3, 4, 5)
    arr = v.ToArray1()
    arr[0] = 99
    arr[4] = 77
    assert v[0] == 99
    assert v[1] == 2
    assert v[4] == 77


def test_NCollection_LinearVectorTest_ToArray1_EmptyVector():
    arr = LV().ToArray1()
    assert arr.Size() == 0
    assert arr.IsEmpty()


def test_NCollection_LinearVectorTest_ToArray1_ReadThrough():
    v = _make(*[i * 11 for i in range(7)])
    arr = v.ToArray1()
    for i in range(7):
        assert arr[i] == i * 11
