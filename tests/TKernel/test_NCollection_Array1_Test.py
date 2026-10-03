# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_Array1_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Not translated: external-buffer constructors (raw C++ pointers), Move/move semantics, STL algorithms on
# raw iterators, EmplaceValue (custom struct element type). ChangeValue/ChangeFirst/ChangeAt of a scalar
# element are not bound (no Python reference to an int); writes go through a[i] / SetValue instead.

import numpy as np
import pytest

from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_DimensionMismatch

A1 = NCollection_Array1[int]


def _data_ptr(arr):
    return np.asarray(arr).__array_interface__["data"][0]


def test_NCollection_Array1Test_DefaultConstructor():
    a = A1(1, 10)
    assert a.Length() == 10
    assert a.Lower() == 1
    assert a.Upper() == 10


def test_NCollection_Array1Test_ConstructorWithBounds():
    a = A1(1, 5)
    assert a.Size() == 5
    assert a.Lower() == 1
    assert a.Upper() == 5


def test_NCollection_Array1Test_ConstructorWithSizeTUpperUsesBounds():
    a = A1(1, 3)
    assert a.IsDeletable()
    assert a.Size() == 3
    assert a.Lower() == 1
    assert a.Upper() == 3
    a[1] = 10
    a[2] = 20
    a[3] = 30
    assert a.Value(1) == 10
    assert a.Value(2) == 20
    assert a.Value(3) == 30


def test_NCollection_Array1Test_ConstructorWithNegativeBounds():
    a = A1(-3, 2)
    assert a.Size() == 6
    assert a.Lower() == -3
    assert a.Upper() == 2


def test_NCollection_Array1Test_AssignmentValue():
    a = A1(1, 5)
    for i in range(a.Lower(), a.Upper() + 1):
        a[i] = i * 10
    for i in range(a.Lower(), a.Upper() + 1):
        assert a(i) == i * 10
    for i in range(a.Lower(), a.Upper() + 1):
        assert a.Value(i) == a(i)


def test_NCollection_Array1Test_CopyConstructor():
    a1 = A1(1, 5)
    for i in range(a1.Lower(), a1.Upper() + 1):
        a1[i] = i * 10
    a2 = A1(a1)
    assert a1.Length() == a2.Length()
    assert a1.Lower() == a2.Lower()
    assert a1.Upper() == a2.Upper()
    for i in range(a1.Lower(), a1.Upper() + 1):
        assert a1(i) == a2(i)
    a1[3] = 999
    assert a1(3) != a2(3)


def test_NCollection_Array1Test_ValueAccess():
    a = A1(1, 5)
    for i in range(1, 6):
        a.SetValue(i, i * 10)
    for i in range(1, 6):
        assert a.Value(i) == i * 10
        assert a(i) == i * 10


def test_NCollection_Array1Test_ChangeValueAccess():
    a = A1(1, 5)
    for i in range(1, 6):
        a[i] = i * 10
    for i in range(1, 6):
        assert a(i) == i * 10
    for i in range(1, 6):
        a[i] += 5
    for i in range(1, 6):
        assert a(i) == i * 10 + 5


def test_NCollection_Array1Test_AssignmentOperator():
    a1 = A1(1, 5)
    for i in range(a1.Lower(), a1.Upper() + 1):
        a1[i] = i * 10
    a2 = A1(11, 15)
    a2.Assign(a1)
    assert a1.Length() == a2.Length()
    assert a1.Lower() == a2.Lower()
    assert a1.Upper() == a2.Upper()
    for i in range(a1.Lower(), a1.Upper() + 1):
        assert a1(i) == a2(i)


def test_NCollection_Array1Test_AssignmentOperatorDifferentSize():
    a1 = A1(5, 8)
    for i in range(a1.Lower(), a1.Upper() + 1):
        a1[i] = i * 10
    a2 = A1(1, 2)
    a2.Assign(a1)
    assert a2.Length() == 4
    assert a2.Lower() == 5
    assert a2.Upper() == 8
    for i in range(a1.Lower(), a1.Upper() + 1):
        assert a1(i) == a2(i)


def test_NCollection_Array1Test_AssignmentOperatorReusesSameSizeOwnedStorage():
    a = A1(1, 6)
    # &ChangeFirst() -> data pointer of the zero-copy numpy view
    initial = _data_ptr(a)
    src = A1(20, 25)
    for i in range(src.Lower(), src.Upper() + 1):
        src[i] = i * 10
    a.Assign(src)
    assert _data_ptr(a) == initial
    assert a.Lower() == 20
    assert a.Upper() == 25
    for i in range(src.Lower(), src.Upper() + 1):
        assert src(i) == a(i)


def test_NCollection_Array1Test_AssignmentOperatorEmptySource():
    a = A1(1, 5)
    empty = A1()
    a.Assign(empty)
    assert a.Length() == 0
    assert a.Lower() == 1
    assert a.IsEmpty()


def test_NCollection_Array1Test_CopyValuesPreservesBounds():
    src = A1(1, 5)
    for i in range(src.Lower(), src.Upper() + 1):
        src[i] = i * 10
    a = A1(11, 15)
    a.CopyValues(src)
    assert a.Lower() == 11
    assert a.Upper() == 15
    for i in range(a.Length()):
        assert src(src.Lower() + i) == a(a.Lower() + i)


def test_NCollection_Array1Test_CopyValuesDifferentSize():
    a = A1(1, 5)
    src = A1(1, 4)
    with pytest.raises(Standard_DimensionMismatch):
        a.CopyValues(src)


def test_NCollection_Array1Test_Init():
    a = A1(1, 5)
    a.Init(42)
    for i in range(a.Lower(), a.Upper() + 1):
        assert a(i) == 42


def test_NCollection_Array1Test_SetValue():
    a = A1(1, 5)
    a.SetValue(3, 123)
    assert a(3) == 123


def test_NCollection_Array1Test_FirstLast():
    a = A1(5, 10)
    a[5] = 55
    a[10] = 1010
    assert a.First() == 55
    assert a.Last() == 1010
    # ChangeFirst()/ChangeLast() of an int element are not bound: write the bounds by index
    a[a.Lower()] = 555
    a[a.Upper()] = 10101
    assert a.First() == 555
    assert a.Last() == 10101


def test_NCollection_Array1Test_STLIteration():
    a = A1(1, 5)
    for i in range(a.Lower(), a.Upper() + 1):
        a[i] = i * 10
    index = 1
    for val in a:
        assert val == index * 10
        index += 1


def test_NCollection_Array1Test_Resize():
    a = A1(1, 5)
    for i in range(a.Lower(), a.Upper() + 1):
        a[i] = i * 10
    a.Resize(1, 10, True)
    assert a.Length() == 10
    assert a.Lower() == 1
    assert a.Upper() == 10
    for i in range(1, 6):
        assert a(i) == i * 10

    a2 = A1(1, 10)
    for i in range(a2.Lower(), a2.Upper() + 1):
        a2[i] = i * 10
    a2.Resize(1, 5, True)
    assert a2.Length() == 5
    assert a2.Lower() == 1
    assert a2.Upper() == 5
    for i in range(1, 6):
        assert a2(i) == i * 10


def test_NCollection_Array1Test_ChangeValue():
    a = A1(1, 5)
    a.Init(42)
    a[3] = 123
    assert a(3) == 123
    assert a(1) == 42
    assert a(2) == 42
    assert a(4) == 42
    assert a(5) == 42


def test_NCollection_Array1Test_IteratorAccess():
    a = A1(1, 5)
    for i in range(1, 6):
        a[i] = i * 10
    it = iter(a)
    for index in range(1, 6):
        assert next(it) == index * 10
    with pytest.raises(StopIteration):
        next(it)
    index = 1
    for value in a:
        assert value == index * 10
        index += 1


def test_NCollection_Array1Test_SizeConstructor_AllocatesCorrectly():
    size = 10
    a = A1(size)
    assert a.Size() == size
    assert a.Lower() == 0
    assert a.Upper() == size - 1
    assert not a.IsEmpty()
    assert a.IsDeletable()


def test_NCollection_Array1Test_SizeConstructor_ZeroSize():
    a = A1(0)
    assert a.Size() == 0
    assert a.IsEmpty()


def test_NCollection_Array1Test_SizeConstructor_AtAccess():
    size = 5
    a = A1(size)
    # ChangeAt(i) of an int element is not bound; Lower() == 0, so a[i] is the same slot
    for i in range(size):
        a[i] = i * 10
    for i in range(size):
        assert a.At(i) == i * 10


def test_NCollection_Array1Test_SizeConstructor_IteratorAccess():
    size = 6
    a = A1(size)
    for i in range(size):
        a[i] = i
    check = 0
    for val in a:
        assert val == check
        check += 1
    assert check == size


def test_NCollection_Array1Test_SizeConstructor_LegacyValueOperator():
    size = 4
    a = A1(size)
    for i in range(size):
        a[i] = i + 100
    for i in range(size):
        assert a[i] == i + 100


def test_NCollection_Array1Test_SizeConstructor_Resize_Grow():
    a = A1(3)
    a[0] = 10
    a[1] = 20
    a[2] = 30
    a.Resize(5, True)
    assert a.Size() == 5
    assert a.At(0) == 10
    assert a.At(1) == 20
    assert a.At(2) == 30


def test_NCollection_Array1Test_SizeConstructor_Resize_Shrink():
    a = A1(5)
    for i in range(5):
        a[i] = i
    a.Resize(3, True)
    assert a.Size() == 3
    assert a.At(0) == 0
    assert a.At(1) == 1
    assert a.At(2) == 2


def test_NCollection_Array1Test_SizeConstructor_Resize_NoData():
    a = A1(4)
    a[0] = 99
    a.Resize(6, False)
    assert a.Size() == 6
    assert a.IsDeletable()
