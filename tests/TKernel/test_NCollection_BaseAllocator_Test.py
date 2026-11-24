# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_BaseAllocator_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated:
# - Allocate, AllocateStruct, AllocateArray, BigAllocation: Allocate/Free hand out and take raw void* memory (placement
#   new, memset), which is not bound (raw memory, docs/Excluded.md).
# - UsageWithVector, CopyAndMove: they store the test's own C++ struct TestStruct in
#   NCollection_DynamicArray<TestStruct>; a C++ type defined in the test cannot be bound.
from nanocct.NCollection import NCollection_BaseAllocator


def test_NCollection_BaseAllocatorTest_DefaultInstance():
    default_alloc = NCollection_BaseAllocator.CommonBaseAllocator_s()

    assert default_alloc is not None

    # The same instance comes back on the next request (EXPECT_EQ on two handles compares the pointers)
    another_default_alloc = NCollection_BaseAllocator.CommonBaseAllocator_s()
    assert default_alloc is another_default_alloc
