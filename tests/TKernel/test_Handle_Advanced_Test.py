# Translated from OCCT src/FoundationClasses/TKernel/GTests/Handle_Advanced_Test.cxx (LGPL-2.1 with the OCCT exception)
# AllocatorHandlePerformance: the QATimer (OSD_Timer) parts check nothing about time and are not translated; the two
# loops keep their 1000 checks. `occ::handle<NCollection_BaseAllocator> aBasePtr = new NCollection_IncAllocator()`
# becomes an NCollection_IncAllocator passed through NCollection_OccAllocator__int(...).Allocator(), whose C++ result
# type is occ::handle<NCollection_BaseAllocator>. occ::down_cast<T> (dynamic_cast) is substituted by
# isinstance(handle, T): a returned handle arrives as the object of its dynamic C++ type, so isinstance answers what
# the down_cast's null check answers. The handle null check becomes `is not None` (a null handle is None).
# Not translated:
# - CompilerSpecificBehavior, DeepHierarchyRTTI, TypeInfoCompatibility, HandleArrayOperations, ConstHandleOperations,
#   WeakReferenceSimulation: they use the test's own classes TransientRoot and the 51-class chain QaClass00_50 ...
#   QaClass50_50 (plus an anonymous-namespace and a QaNamespace class), defined with DEFINE_STANDARD_RTTI_INLINE in the
#   test, which cannot be bound; their checks are about those classes (names, depth, typeid) or occ::handle's own C++
#   API (get(), const handles, overload resolution, std::vector of handles, raw pointers), which has no Python
#   counterpart: nanocct passes a handle as the object itself or None.
from nanocct.IMeshData import NCollection_OccAllocator__int
from nanocct.NCollection import NCollection_HeapAllocator, NCollection_IncAllocator


def test_HandleAdvancedTest_AllocatorHandlePerformance():
    inc = NCollection_IncAllocator()
    base_ptr = NCollection_OccAllocator__int(inc).Allocator()  # occ::handle<NCollection_BaseAllocator>
    assert base_ptr is not None

    # down_cast to IncAllocator succeeds
    for _ in range(1000):
        assert isinstance(base_ptr, NCollection_IncAllocator)

    # down_cast to HeapAllocator fails
    for _ in range(1000):
        assert not isinstance(base_ptr, NCollection_HeapAllocator)
