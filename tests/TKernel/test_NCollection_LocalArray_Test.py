# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_LocalArray_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_LocalArray<int> (and <int, 1024>, <int, 64>) is not bound: substituted by NCollection_LocalArray[float]
# (MAX_ARRAY_SIZE 1024) with integral values (i * 10 -> float(i * 10), exact in a double), in all translated cases.
# operator T* (the C++ element access array[i] and static_cast<int*>) is not bound: elements are read and written
# through ToArray1(), an Array1 over the same buffer (lower bound 0); that view is released before a growing
# Allocate, which raises BufferError while it lives. ReallocateStackToStack_WithCopy uses <int, 64>: 10 and 32
# elements are inline for 64 and for 1024 alike, so the tested inline-to-inline copy is the same.
# Not translated: CustomMaxArraySize, TransitionStackToHeap, ReallocateStackToHeap_WithCopy,
# ReallocateHeapToHeap_WithCopy, ReallocateNoCopy, ReallocateShrink, ReallocateAsGrowableStack (compile-time
# MAX_ARRAY_SIZE other than 1024: their inline/heap transitions do not happen at 1024); MoveConstructor_FromStack,
# MoveConstructor_FromHeap, MoveAssignment (move semantics, not bound); CustomType and all NonTrivial_* cases (element
# types the test defines itself, constructor/destructor counters); ToArray1_SamePointer, ToArray1_HeapBuffer (pointer
# equality with the raw buffer; HeapBuffer also needs MAX_ARRAY_SIZE 8). The HasToArray1 static_asserts are
# compile-time checks.
from nanocct.NCollection import NCollection_LocalArray

LocalArray = NCollection_LocalArray[float]


def test_NCollection_LocalArrayTest_DefaultConstructor():
    array = LocalArray()
    assert array.Size() == 0


def test_NCollection_LocalArrayTest_ConstructorWithSize():
    size = 100
    array = LocalArray(size)
    assert array.Size() == size


def test_NCollection_LocalArrayTest_SmallSizeAllocation():
    size = 10
    array = LocalArray(size)
    assert array.Size() == size
    view = array.ToArray1()
    for i in range(size):
        view[i] = i * 10
    for i in range(size):
        assert view[i] == i * 10


def test_NCollection_LocalArrayTest_LargeSizeAllocation():
    size = 2000
    array = LocalArray(size)
    assert array.Size() == size
    view = array.ToArray1()
    for i in range(size):
        view[i] = i * 10
    for i in range(size):
        assert view[i] == i * 10


def test_NCollection_LocalArrayTest_Reallocation():
    array = LocalArray(10)
    assert array.Size() == 10
    view = array.ToArray1()
    for i in range(10):
        view[i] = i
    del view

    array.Allocate(50)
    assert array.Size() == 50
    view = array.ToArray1()
    for i in range(50):
        view[i] = i * 2
    for i in range(50):
        assert view[i] == i * 2
    del view

    array.Allocate(5)
    assert array.Size() == 5
    view = array.ToArray1()
    for i in range(5):
        assert view[i] == i * 2


def test_NCollection_LocalArrayTest_ReallocateStackToStack_WithCopy():
    anArray = LocalArray(10)
    view = anArray.ToArray1()
    for i in range(10):
        view[i] = i * 100
    del view

    anArray.Reallocate(32, True)
    assert anArray.Size() == 32
    view = anArray.ToArray1()
    for i in range(10):
        assert view[i] == i * 100


def test_NCollection_LocalArrayTest_ToArray1_ModifyReflectsInSource():
    aSrc = LocalArray(5)
    aSrcData = aSrc.ToArray1()
    for i in range(5):
        aSrcData[i] = i

    aArr = aSrc.ToArray1()
    aArr[0] = 99
    aArr[4] = 77

    assert aSrcData[0] == 99
    assert aSrcData[1] == 1
    assert aSrcData[4] == 77


def test_NCollection_LocalArrayTest_ToArray1_EmptyVector():
    aEmpty = LocalArray()
    aArr = aEmpty.ToArray1()
    assert aArr.Size() == 0
    assert aArr.IsEmpty()


def test_NCollection_LocalArrayTest_ToArray1_ReadThrough():
    aSrc = LocalArray(7)
    aSrcData = aSrc.ToArray1()
    for i in range(7):
        aSrcData[i] = i * 11
    del aSrcData

    aArr = aSrc.ToArray1()
    for i in range(7):
        assert aArr[i] == i * 11
