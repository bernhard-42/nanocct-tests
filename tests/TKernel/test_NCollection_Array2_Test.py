# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_Array2_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Not translated: external-buffer constructors (raw C++ pointers), move constructor/assignment, EmplaceValue
# (custom struct element type). ChangeValue/ChangeAt of a scalar element are not bound; writes go through
# a[row, col] / SetValue instead.

import numpy as np
import pytest

from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Standard import Standard_DimensionMismatch

A2 = NCollection_Array2[int]


def _data_ptr(arr):
    return np.asarray(arr).__array_interface__["data"][0]


def _fill(arr, fn):
    for r in range(arr.LowerRow(), arr.UpperRow() + 1):
        for c in range(arr.LowerCol(), arr.UpperCol() + 1):
            arr[r, c] = fn(r, c)


def test_NCollection_Array2Test_DefaultConstructor():
    a = A2()
    assert a.Length() == 0
    assert a.NbRows() == 0
    assert a.NbColumns() == 0


def test_NCollection_Array2Test_ConstructorWithBounds():
    a = A2(1, 5, 1, 10)
    assert a.Length() == 50
    assert a.NbRows() == 5
    assert a.NbColumns() == 10
    assert a.LowerRow() == 1
    assert a.UpperRow() == 5
    assert a.LowerCol() == 1
    assert a.UpperCol() == 10


def test_NCollection_Array2Test_ConstructorWithNegativeBounds():
    a = A2(-2, 2, -5, 5)
    assert a.Length() == 55
    assert a.NbRows() == 5
    assert a.NbColumns() == 11
    assert a.LowerRow() == -2
    assert a.UpperRow() == 2
    assert a.LowerCol() == -5
    assert a.UpperCol() == 5


def test_NCollection_Array2Test_ValueAccess():
    a = A2(1, 3, 1, 4)
    for r in range(a.LowerRow(), a.UpperRow() + 1):
        for c in range(a.LowerCol(), a.UpperCol() + 1):
            a.SetValue(r, c, r * 100 + c)
    for r in range(a.LowerRow(), a.UpperRow() + 1):
        for c in range(a.LowerCol(), a.UpperCol() + 1):
            assert a.Value(r, c) == r * 100 + c
            assert a(r, c) == r * 100 + c


def test_NCollection_Array2Test_ChangeValueAccess():
    a = A2(0, 2, 0, 3)
    _fill(a, lambda r, c: r * 100 + c)
    assert a(1, 2) == 102
    a[1, 2] = 999
    assert a(1, 2) == 999


def test_NCollection_Array2Test_Init():
    a = A2(1, 5, 1, 5)
    a.Init(42)
    for r in range(a.LowerRow(), a.UpperRow() + 1):
        for c in range(a.LowerCol(), a.UpperCol() + 1):
            assert a(r, c) == 42


def test_NCollection_Array2Test_CopyConstructor():
    a1 = A2(1, 3, 1, 4)
    a1.Init(123)
    a2 = A2(a1)
    assert a1.Length() == a2.Length()
    assert a1.NbRows() == a2.NbRows()
    assert a1.NbColumns() == a2.NbColumns()
    assert a1(2, 3) == a2(2, 3)
    a1.SetValue(2, 3, 999)
    assert a2(2, 3) == 123
    assert a1(2, 3) != a2(2, 3)


def test_NCollection_Array2Test_AssignmentOperator():
    a1 = A2(5, 7, 10, 13)
    _fill(a1, lambda r, c: r * 100 + c)
    a2 = A2(1, 1, 1, 1)
    a2.Init(0)
    a2.Assign(a1)
    assert a1.NbRows() == a2.NbRows()
    assert a1.NbColumns() == a2.NbColumns()
    assert a1.LowerRow() == a2.LowerRow()
    assert a1.LowerCol() == a2.LowerCol()
    assert a2(6, 12) == 612
    a1.SetValue(6, 12, 999)
    assert a2(6, 12) == 612


def test_NCollection_Array2Test_AssignmentOperatorReusesSameSizeOwnedStorage():
    a = A2(1, 3, 1, 4)
    # &ChangeFirst() -> data pointer of the zero-copy numpy view
    initial = _data_ptr(a)
    src = A2(10, 12, 20, 23)
    _fill(src, lambda r, c: r * 100 + c)
    a.Assign(src)
    assert _data_ptr(a) == initial
    assert a.LowerRow() == 10
    assert a.UpperRow() == 12
    assert a.LowerCol() == 20
    assert a.UpperCol() == 23
    assert a(11, 22) == 1122


def test_NCollection_Array2Test_CopyValuesPreservesBounds():
    src = A2(5, 6, 7, 9)
    _fill(src, lambda r, c: r * 100 + c)
    a = A2(1, 2, 1, 3)
    a.CopyValues(src)
    assert a.LowerRow() == 1
    assert a.UpperRow() == 2
    assert a.LowerCol() == 1
    assert a.UpperCol() == 3
    assert a(1, 1) == 507
    assert a(2, 3) == 609


def test_NCollection_Array2Test_CopyValuesDifferentDimensions():
    a = A2(1, 2, 1, 3)
    src = A2(1, 3, 1, 2)
    with pytest.raises(Standard_DimensionMismatch):
        a.CopyValues(src)


def test_NCollection_Array2Test_Resize():
    a = A2(1, 4, 1, 5)
    for r in range(1, 5):
        for c in range(1, 6):
            a[r, c] = r * 100 + c
    a.Resize(0, 5, 0, 6, True)
    assert a.NbRows() == 6
    assert a.NbColumns() == 7
    assert a.LowerRow() == 0
    assert a.UpperCol() == 6
    for r in range(0, 4):
        for c in range(0, 5):
            assert a(r, c) == (r + 1) * 100 + (c + 1)


def test_NCollection_Array2Test_ReIndex_UpdateBounds():
    a = A2(1, 5, 1, 10)
    a.UpdateLowerRow(0)
    a.UpdateLowerCol(0)
    assert a.LowerRow() == 0
    assert a.UpperRow() == 4
    assert a.LowerCol() == 0
    assert a.UpperCol() == 9
    assert a.NbRows() == 5
    assert a.NbColumns() == 10

    a.UpdateUpperRow(10)
    a.UpdateUpperCol(20)
    assert a.UpperRow() == 10
    assert a.UpperCol() == 20
    assert a.LowerRow() == 6
    assert a.LowerCol() == 11
    assert a.NbRows() == 5
    assert a.NbColumns() == 10


def test_NCollection_Array2Test_STLIteration():
    a = A2(1, 2, 1, 3)
    for r in range(1, 3):
        for c in range(1, 4):
            a[r, c] = r * 10 + c
    expected = [11, 12, 13, 21, 22, 23]
    index = 0
    for value in a:
        assert value == expected[index]
        index += 1
    assert index == 6


def _check_region(arr, rows, cols):
    for r in rows:
        for c in cols:
            assert arr(r, c) == r * 100 + c


def test_NCollection_Array2Test_ResizeWithTrim_PreservesElementPositions():
    a = A2(1, 5, 1, 4)
    _fill(a, lambda r, c: r * 100 + c)

    cp = A2(a)
    cp.ResizeWithTrim(1, 3, 1, 4, True)
    assert cp.NbRows() == 3
    assert cp.NbColumns() == 4
    _check_region(cp, range(1, 4), range(1, 5))

    cp = A2(a)
    cp.ResizeWithTrim(1, 5, 1, 2, True)
    assert cp.NbRows() == 5
    assert cp.NbColumns() == 2
    _check_region(cp, range(1, 6), range(1, 3))

    cp = A2(a)
    cp.ResizeWithTrim(1, 3, 1, 2, True)
    assert cp.NbRows() == 3
    assert cp.NbColumns() == 2
    _check_region(cp, range(1, 4), range(1, 3))

    cp = A2(a)
    cp.ResizeWithTrim(1, 7, 1, 6, True)
    assert cp.NbRows() == 7
    assert cp.NbColumns() == 6
    _check_region(cp, range(1, 6), range(1, 5))


def test_NCollection_Array2Test_ResizeWithTrim_NonUnitLowerBounds():
    a = A2(3, 5, 10, 12)
    _fill(a, lambda r, c: r * 100 + c)

    cp = A2(a)
    cp.ResizeWithTrim(3, 4, 10, 12, True)
    assert cp.NbRows() == 2
    assert cp.NbColumns() == 3
    _check_region(cp, range(3, 5), range(10, 13))

    cp = A2(a)
    cp.ResizeWithTrim(3, 7, 10, 14, True)
    assert cp.NbRows() == 5
    assert cp.NbColumns() == 5
    _check_region(cp, range(3, 6), range(10, 13))

    cp = A2(a)
    cp.ResizeWithTrim(3, 5, 10, 12, True)
    assert cp.NbRows() == 3
    assert cp.NbColumns() == 3
    _check_region(cp, range(3, 6), range(10, 13))


def test_NCollection_Array2Test_Resize_FromEmpty():
    e = A2()
    assert e.NbRows() == 0
    assert e.NbColumns() == 0
    e.Resize(1, 3, 1, 2, True)
    assert e.NbRows() == 3
    assert e.NbColumns() == 2

    e2 = A2()
    e2.ResizeWithTrim(1, 2, 1, 4, True)
    assert e2.NbRows() == 2
    assert e2.NbColumns() == 4


def test_NCollection_Array2Test_Resize_SameSizeNewBounds():
    a = A2(1, 3, 1, 3)
    for r in range(1, 4):
        for c in range(1, 4):
            a[r, c] = r * 10 + c
    a.ResizeWithTrim(5, 7, 10, 12, True)
    assert a.NbRows() == 3
    assert a.NbColumns() == 3
    for r in range(5, 8):
        for c in range(10, 13):
            assert a(r, c) == (r - 4) * 10 + (c - 9)


def test_NCollection_Array2Test_Resize_ChangeShapeSameSize():
    a = A2(1, 4, 1, 6)
    expected = 0
    for r in range(1, 5):
        for c in range(1, 7):
            a[r, c] = expected
            expected += 1
    a.Resize(1, 6, 1, 4, True)
    assert a.NbRows() == 6
    assert a.NbColumns() == 4
    assert a.Length() == 24
    # static_cast<NCollection_Array1<int>&>(anArray).Value(i): call the base class method
    for i in range(a.Lower(), a.Lower() + 16):
        assert NCollection_Array1[int].Value(a, i) == i - a.Lower()


def test_NCollection_Array2Test_ReIndex_Interference():
    a = A2(1, 10, 1, 1)
    n = a.NbRows()
    a.UpdateLowerRow(5)
    assert a.LowerRow() == 5
    assert a.UpperRow() == 14
    a.UpdateUpperRow(12)
    assert a.UpperRow() == 12
    assert a.LowerRow() == 3
    assert a.LowerRow() != 5
    assert a.NbRows() == n


def test_NCollection_Array2Test_Resize_SameSizeNewBounds_Linear():
    a = A2(1, 3, 1, 3)
    for r in range(1, 4):
        for c in range(1, 4):
            a[r, c] = r * 10 + c
    a.Resize(5, 7, 10, 12, True)
    assert a.NbRows() == 3
    assert a.NbColumns() == 3
    for r in range(5, 8):
        for c in range(10, 13):
            assert a(r, c) == (r - 4) * 10 + (c - 9)


def test_NCollection_Array2Test_Resize_NoCopy():
    a = A2(1, 3, 1, 4)
    a.Init(42)
    a.Resize(1, 5, 1, 2, False)
    assert a.NbRows() == 5
    assert a.NbColumns() == 2
    a.Init(7)
    a.Resize(10, 14, 20, 21, False)
    assert a.NbRows() == 5
    assert a.NbColumns() == 2
    assert a.LowerRow() == 10
    assert a.LowerCol() == 20


def test_NCollection_Array2Test_ResizeWithTrim_GrowPreservesOldRegion():
    a = A2(1, 2, 1, 2)
    a.Init(99)
    a.ResizeWithTrim(1, 4, 1, 3, True)
    assert a.NbRows() == 4
    assert a.NbColumns() == 3
    for r in range(1, 3):
        for c in range(1, 3):
            assert a(r, c) == 99


def test_NCollection_Array2Test_SizeConstructor_AllocatesCorrectly():
    nr, nc = 3, 4
    a = A2(nr, nc)
    assert a.NbRows() == nr
    assert a.NbColumns() == nc
    assert a.Size() == nr * nc
    assert a.LowerRow() == 0
    assert a.LowerCol() == 0
    assert a.UpperRow() == nr - 1
    assert a.UpperCol() == nc - 1
    assert a.IsDeletable()


def test_NCollection_Array2Test_SizeConstructor_AtAccess():
    nr, nc = 3, 5
    a = A2(nr, nc)
    # ChangeAt(row, col) of an int element is not bound; lower bounds are 0, so a[row, col] is the same slot
    for r in range(nr):
        for c in range(nc):
            a[r, c] = r * 100 + c
    for r in range(nr):
        for c in range(nc):
            assert a.At(r, c) == r * 100 + c


def test_NCollection_Array2Test_SizeConstructor_LegacyOperatorZeroBased():
    a = A2(2, 3)
    a[0, 0] = 1
    a[0, 1] = 2
    a[1, 2] = 9
    assert a.At(0, 0) == 1
    assert a.At(0, 1) == 2
    assert a.At(1, 2) == 9


def test_NCollection_Array2Test_SizeConstructor_Resize_Grow():
    a = A2(2, 2)
    a.Init(7)
    a.Resize(3, 3, True)
    assert a.NbRows() == 3
    assert a.NbColumns() == 3
    assert a.At(0, 0) == 7
    assert a.At(0, 1) == 7


def test_NCollection_Array2Test_SizeConstructor_Resize_NoData():
    a = A2(3, 4)
    a.Init(5)
    a.Resize(2, 2, False)
    assert a.NbRows() == 2
    assert a.NbColumns() == 2
    assert a.LowerRow() == 0
    assert a.LowerCol() == 0
    assert a.IsDeletable()


def test_NCollection_Array2Test_SizeConstructor_ResizeWithTrim_GrowPreserves():
    a = A2(2, 2)
    a.Init(42)
    a.ResizeWithTrim(3, 3, True)
    assert a.NbRows() == 3
    assert a.NbColumns() == 3
    for r in range(2):
        for c in range(2):
            assert a.At(r, c) == 42
