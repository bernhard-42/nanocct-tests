# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_BaseAllocator_Test.cxx (LGPL-2.1 with the OCCT exception)
# The test's own C++ struct TestStruct (int myValue1, double myValue2, char myChar) cannot be bound: in UsageWithVector
# and CopyAndMove, NCollection_DynamicArray<TestStruct> is substituted by NCollection_DynamicArray[gp_XYZ] with
# TestStruct(v1, v2, c) -> gp_XYZ(v1, v2, ord(c)) (the int and the char code are exact in a double). Each field check
# compares the mapped coordinate, TestStruct::operator== becomes same_struct() with the same field rules. The array
# stores, indexes and copies its elements by value whatever their type, so the tested storage, copy and assignment
# behaviour is unchanged. C++ `aVector3 = aVector1` is operator=, which calls Assign(theOther, false).
# Not translated:
# - Allocate, AllocateStruct, AllocateArray, BigAllocation: Allocate/Free hand out and take raw void* memory (placement
#   new, memset), which is not bound (raw memory, docs/Excluded.md).
from nanocct.gp import gp_XYZ
from nanocct.NCollection import NCollection_BaseAllocator, NCollection_DynamicArray

Vector = NCollection_DynamicArray[gp_XYZ]


def make_struct(value1, value2, char):
    """TestStruct(theVal1, theVal2, theChar) mapped to gp_XYZ."""
    return gp_XYZ(value1, value2, ord(char))


def same_struct(lhs, rhs):
    """TestStruct::operator==: equal ints, doubles within 1e-10, equal chars."""
    return lhs.X() == rhs.X() and abs(lhs.Y() - rhs.Y()) < 1e-10 and lhs.Z() == rhs.Z()


def test_NCollection_BaseAllocatorTest_DefaultInstance():
    default_alloc = NCollection_BaseAllocator.CommonBaseAllocator_s()

    assert default_alloc is not None

    # The same instance comes back on the next request (EXPECT_EQ on two handles compares the pointers)
    another_default_alloc = NCollection_BaseAllocator.CommonBaseAllocator_s()
    assert default_alloc is another_default_alloc


def test_NCollection_BaseAllocatorTest_UsageWithVector():
    # A collection using the default allocator
    vector = Vector()

    vector.Append(make_struct(10, 1.0, "X"))
    vector.Append(make_struct(20, 2.0, "Y"))
    vector.Append(make_struct(30, 3.0, "Z"))

    assert vector.Length() == 3
    assert vector(0).X() == 10
    assert vector(0).Y() == 1.0
    assert vector(0).Z() == ord("X")

    assert vector(1).X() == 20
    assert vector(1).Y() == 2.0
    assert vector(1).Z() == ord("Y")

    assert vector(2).X() == 30
    assert vector(2).Y() == 3.0
    assert vector(2).Z() == ord("Z")

    # A collection using a custom allocator
    custom_alloc = NCollection_BaseAllocator.CommonBaseAllocator_s()
    vector_with_custom_alloc = Vector(5, custom_alloc)

    vector_with_custom_alloc.Append(make_struct(40, 4.0, "P"))
    vector_with_custom_alloc.Append(make_struct(50, 5.0, "Q"))

    assert vector_with_custom_alloc.Length() == 2
    assert vector_with_custom_alloc(0).X() == 40
    assert vector_with_custom_alloc(0).Y() == 4.0
    assert vector_with_custom_alloc(0).Z() == ord("P")

    assert vector_with_custom_alloc(1).X() == 50
    assert vector_with_custom_alloc(1).Y() == 5.0
    assert vector_with_custom_alloc(1).Z() == ord("Q")


def test_NCollection_BaseAllocatorTest_CopyAndMove():
    alloc1 = NCollection_BaseAllocator.CommonBaseAllocator_s()

    vector1 = Vector(5, alloc1)
    vector1.Append(make_struct(10, 1.0, "A"))
    vector1.Append(make_struct(20, 2.0, "B"))

    # Copy constructor
    vector2 = Vector(vector1)
    assert vector2.Length() == 2
    assert same_struct(vector2(0), make_struct(10, 1.0, "A"))
    assert same_struct(vector2(1), make_struct(20, 2.0, "B"))

    # A new collection with another allocator handle
    alloc2 = NCollection_BaseAllocator.CommonBaseAllocator_s()
    vector3 = Vector(5, alloc2)

    # Assignment operator (operator= is Assign(theOther, false))
    vector3.Assign(vector1, False)
    assert vector3.Length() == 2
    assert same_struct(vector3(0), make_struct(10, 1.0, "A"))
    assert same_struct(vector3(1), make_struct(20, 2.0, "B"))
