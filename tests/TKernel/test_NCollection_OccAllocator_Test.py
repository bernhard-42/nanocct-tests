# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_OccAllocator_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_OccAllocator<int> is bound as IMeshData.NCollection_OccAllocator__int.
# Not translated:
# - AllocatorTypeTraits: compile-time checks of the allocator's typedefs (value_type, pointer, reference, ...) and
#   rebind<>::other.
# - STLContainerIntegration, DefaultAllocator, CrossTypeCompatibility: they use the allocator inside std::list /
#   std::vector, which a Python test cannot instantiate (STLContainerIntegration and CrossTypeCompatibility also build
#   NCollection_OccAllocator<char> / <void*>, which are not bound).
from nanocct.IMeshData import NCollection_OccAllocator__int
from nanocct.NCollection import NCollection_IncAllocator


def test_NCollection_OccAllocatorTest_AllocatorComparison():
    inc_alloc1 = NCollection_IncAllocator()
    inc_alloc2 = NCollection_IncAllocator()

    alloc1 = NCollection_OccAllocator__int(inc_alloc1)
    alloc2 = NCollection_OccAllocator__int(inc_alloc1)  # same underlying allocator
    alloc3 = NCollection_OccAllocator__int(inc_alloc2)  # different underlying allocator
    alloc4 = NCollection_OccAllocator__int()  # default allocator

    # EXPECT_EQ / EXPECT_NE use operator== / operator!=
    assert alloc1 == alloc2
    assert alloc1 != alloc3
    assert alloc1 != alloc4

    assert not (alloc1 != alloc2)
    assert alloc1 != alloc3
