# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_DynamicArray_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Not translated: move semantics, custom allocators, STL algorithms / C++ iterator lifetime across appends,
# EmplaceAppend/EmplaceValue (not bound; custom struct element types), the int-vs-size_t overload tests
# (Python sees one overload). ChangeValue/ChangeFirst/ChangeLast of a scalar element are not bound and
# NCollection_DynamicArray<int>::Iterator is not exposed: writes go through d[i] / SetValue, iteration
# through Python's iterator.

import pytest

from nanocct.NCollection import NCollection_DynamicArray
from nanocct.Standard import Standard_OutOfRange

DA = NCollection_DynamicArray[int]


def _make(*values):
    v = DA()
    for x in values:
        v.Append(x)
    return v


def test_NCollection_DynamicArrayTest_DefaultConstructor():
    v = DA()
    assert v.Length() == 0
    assert v.IsEmpty()


def test_NCollection_DynamicArrayTest_ResizeConstructor():
    n, val = 10, 42
    v = DA(n)
    for i in range(n):
        v.SetValue(i, val)
    assert v.Length() == n
    assert not v.IsEmpty()
    for i in range(n):
        assert v(i) == val


def test_NCollection_DynamicArrayTest_Append():
    v = _make(10, 20, 30)
    assert v.Length() == 3
    assert v(0) == 10
    assert v(1) == 20
    assert v(2) == 30


def test_NCollection_DynamicArrayTest_SetValue():
    v = DA(5, None)
    v.SetValue(2, 42)
    assert v(2) == 42
    assert v(0) == 0
    assert v(1) == 0
    # aVector(3) = 99: index 3 is past the end (Length() == 3); operator() does not grow the array and
    # past-the-end access is unchecked in OCCT (see Pythonic-OCCT.md), so use SetValue, which appends
    v.SetValue(3, 99)
    assert v(3) == 99


def test_NCollection_DynamicArrayTest_Value():
    v = _make(10, 20)
    assert v.Value(0) == 10
    assert v.Value(1) == 20
    assert v.Value(0) == v(0)
    assert v.Value(1) == v(1)


def test_NCollection_DynamicArrayTest_ChangeValue():
    v = _make(10, 20)
    v[1] = 25
    assert v(1) == 25
    v[0] = 15
    assert v(0) == 15


def test_NCollection_DynamicArrayTest_FirstLast():
    v = _make(10, 20, 30)
    assert v.First() == 10
    assert v.Last() == 30
    v[v.Lower()] = 15
    v[v.Upper()] = 35
    assert v.First() == 15
    assert v.Last() == 35


def test_NCollection_DynamicArrayTest_CopyConstructor():
    v1 = _make(10, 20, 30)
    v2 = DA(v1)
    assert v1.Length() == v2.Length()
    for i in range(v1.Length()):
        assert v1(i) == v2(i)
    v1[1] = 25
    assert v2(1) == 20


def test_NCollection_DynamicArrayTest_AssignmentOperator():
    v1 = _make(10, 20, 30)
    v2 = DA()
    v2.Assign(v1)
    assert v1.Length() == v2.Length()
    for i in range(v1.Length()):
        assert v1(i) == v2(i)
    v1[1] = 25
    assert v2(1) == 20


def test_NCollection_DynamicArrayTest_Clear():
    v = _make(10, 20)
    v.Clear()
    assert v.Length() == 0
    assert v.IsEmpty()


def test_NCollection_DynamicArrayTest_Iterator():
    v = _make(10, 20, 30)
    assert sum(v) == 60
    for i in range(v.Length()):
        v[i] = v[i] * 2
    assert v(0) == 20
    assert v(1) == 40
    assert v(2) == 60


def test_NCollection_DynamicArrayTest_STLIterators():
    v = _make(10, 20, 30)
    total = 0
    for val in v:
        total += val
    assert total == 60
    total = 0
    for i in range(v.Length()):
        v[i] *= 2
        total += v[i]
    assert total == 120
    assert v(0) == 20
    assert v(1) == 40
    assert v(2) == 60


def test_NCollection_DynamicArrayTest_Grow():
    v = DA()
    for i in range(1000):
        v.Append(i)
    assert v.Length() == 1000
    for i in range(1000):
        assert v(i) == i


def test_NCollection_DynamicArrayTest_EraseLast():
    v = _make(10, 20, 30)
    assert v.Length() == 3
    v.EraseLast()
    assert v.Length() == 2
    assert v(0) == 10
    assert v(1) == 20
    v.EraseLast()
    assert v.Length() == 1
    assert v(0) == 10
    v.EraseLast()
    assert v.Length() == 0
    assert v.IsEmpty()
    v.EraseLast()
    assert v.Length() == 0


def test_NCollection_DynamicArrayTest_Appended():
    # Appended() returns int& in C++; Python gets a copy, so write through the new index
    v = DA()
    v.Appended()
    v[0] = 10
    v.Appended()
    v[1] = 20
    assert v.Length() == 2
    assert v(0) == 10
    assert v(1) == 20
    v[0] = 15
    assert v(0) == 15


def test_NCollection_DynamicArrayTest_SetIncrement():
    v = DA()
    v.SetIncrement(512)
    for i in range(1000):
        v.Append(i)
    assert v.Length() == 1000
    for i in range(1000):
        assert v(i) == i


def test_NCollection_DynamicArrayTest_SetValue_ReplacesExisting():
    # element type substituted: int for the custom VecMultiArgType
    v = DA()
    v.SetValue(0, 10)
    v.SetValue(1, 20)
    v.SetValue(2, 30)
    assert v.Length() == 3
    assert v.SetValue(1, 200) == 200
    assert v.Length() == 3
    assert v(0) == 10
    assert v(1) == 200
    assert v(2) == 30


def test_NCollection_DynamicArrayTest_InsertAfter_Middle():
    v = _make(10, 20, 30, 40)
    v.InsertAfter(1, 99)
    assert v.Length() == 5
    assert list(v) == [10, 20, 99, 30, 40]


def test_NCollection_DynamicArrayTest_InsertAfter_First():
    v = _make(10, 20, 30)
    v.InsertAfter(0, 99)
    assert v.Length() == 4
    assert list(v) == [10, 99, 20, 30]


def test_NCollection_DynamicArrayTest_InsertAfter_Last():
    v = _make(10, 20, 30)
    v.InsertAfter(2, 99)
    assert v.Length() == 4
    assert list(v) == [10, 20, 30, 99]


def test_NCollection_DynamicArrayTest_InsertAfter_SingleElement():
    v = _make(10)
    v.InsertAfter(0, 99)
    assert v.Length() == 2
    assert v(0) == 10
    assert v(1) == 99


def test_NCollection_DynamicArrayTest_InsertBefore_Middle():
    v = _make(10, 20, 30, 40)
    v.InsertBefore(2, 99)
    assert v.Length() == 5
    assert list(v) == [10, 20, 99, 30, 40]


def test_NCollection_DynamicArrayTest_InsertBefore_First():
    v = _make(10, 20, 30)
    v.InsertBefore(0, 99)
    assert v.Length() == 4
    assert list(v) == [99, 10, 20, 30]


def test_NCollection_DynamicArrayTest_InsertBefore_Last():
    v = _make(10, 20, 30)
    v.InsertBefore(2, 99)
    assert v.Length() == 4
    assert list(v) == [10, 20, 99, 30]


def test_NCollection_DynamicArrayTest_InsertAfter_MultipleInserts():
    v = _make(10, 40)
    v.InsertAfter(0, 20)
    v.InsertAfter(1, 30)
    assert v.Length() == 4
    assert list(v) == [10, 20, 30, 40]


def test_NCollection_DynamicArrayTest_SizeReturnsSizeT():
    v = DA()
    assert v.Size() == 0
    v.Append(42)
    v.Append(43)
    assert v.Size() == 2


def test_NCollection_DynamicArrayTest_LengthStillReturnsInt():
    v = DA()
    assert v.Length() == 0


def test_NCollection_DynamicArrayTest_UpperReturnsMinusOneForEmpty():
    v = DA()
    assert v.Lower() == 0
    assert v.Upper() == -1
    v.Append(10)
    assert v.Upper() == 0


def test_NCollection_DynamicArrayTest_SizeTConstructor():
    v = DA(128)
    v.Append(1)
    assert v.Size() == 1


def test_NCollection_DynamicArrayTest_SizeTValueAccess():
    v = DA()
    for i in range(10):
        v.Append(i * 7)
    assert v.Value(2) == 14
    assert v[2] == 14
    assert v(2) == 14


def test_NCollection_DynamicArrayTest_SizeTSetValueExtends():
    v = DA()
    v.SetValue(5, 99)
    assert v.Size() == 6
    assert v.Value(5) == 99


def test_NCollection_DynamicArrayTest_SizeTInsertBeforeAfter():
    v = _make(0, 1, 2)
    v.InsertBefore(1, 99)
    assert v.Size() == 4
    assert v[1] == 99
    assert v[2] == 1
    v.InsertAfter(0, 42)
    assert v.Size() == 5
    assert v[1] == 42


def test_NCollection_DynamicArrayTest_IntOverloadGuardsNegative():
    v = _make(1)
    with pytest.raises(Standard_OutOfRange):
        v.SetValue(-1, 99)
    with pytest.raises(Standard_OutOfRange):
        v.InsertBefore(-1, 99)
    with pytest.raises(Standard_OutOfRange):
        v.InsertAfter(-1, 99)
    # EmplaceValue is not bound


def test_NCollection_DynamicArrayTest_SetValue_OutOfOrderIndices_CorrectValues():
    v = DA()
    v.SetValue(0, 1)
    v.SetValue(2, 500)
    v.SetValue(1, 2)
    assert v.Size() == 3
    assert v.Value(0) == 1
    assert v.Value(1) == 2
    assert v.Value(2) == 500
