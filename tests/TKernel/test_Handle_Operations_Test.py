# Translated from OCCT src/FoundationClasses/TKernel/GTests/Handle_Operations_Test.cxx (LGPL-2.1 with the OCCT exception)
# AllocatorHandleCasting: `occ::handle<NCollection_BaseAllocator> aBasePtr = new NCollection_IncAllocator()` becomes an
# NCollection_IncAllocator passed through NCollection_OccAllocator__int(...).Allocator(), whose C++ result type is
# occ::handle<NCollection_BaseAllocator>. occ::down_cast<T> (dynamic_cast) is substituted by isinstance(handle, T): a
# returned handle arrives as the object of its dynamic C++ type, so isinstance answers what the down_cast's null check
# answers; a successful down_cast yields the same object, so the cast result is the handle itself and the get()
# comparisons become `is`. The handle null checks become `is not None` (a null handle is None).
# Not translated:
# - BasicHandleOperations, HandleDownCast, HandleComparisons, HandleCopyAndAssignment, HandleWithDifferentTypes,
#   HandleNullOperations: they use the test's own classes TestBase, TestDerived, TestOther (DEFINE_STANDARD_RTTI_INLINE
#   in the test), which cannot be bound, and they test occ::handle's own C++ API (get(), operator*, ==/!= between
#   handles and raw pointers, bool conversion, copy and assignment), which has no Python counterpart: nanocct passes a
#   handle as the object itself or None.
from nanocct.IMeshData import NCollection_OccAllocator__int
from nanocct.NCollection import NCollection_BaseAllocator, NCollection_HeapAllocator, NCollection_IncAllocator


def test_HandleOperationsTest_AllocatorHandleCasting():
    inc = NCollection_IncAllocator()
    base_ptr = NCollection_OccAllocator__int(inc).Allocator()  # occ::handle<NCollection_BaseAllocator>
    assert base_ptr is not None
    assert isinstance(base_ptr, NCollection_BaseAllocator)

    # Successful down_cast to IncAllocator: the same object
    assert isinstance(base_ptr, NCollection_IncAllocator)
    inc_alloc = base_ptr
    assert inc_alloc is inc

    # Upcast back to BaseAllocator, through the same occ::handle<NCollection_BaseAllocator> result
    base_alloc = NCollection_OccAllocator__int(inc_alloc).Allocator()
    assert base_alloc is not None
    assert base_alloc is base_ptr

    # Failed down_cast to HeapAllocator
    assert not isinstance(base_ptr, NCollection_HeapAllocator)
