# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_Traverse_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated:
# - CountAllElements, EmptyTree, NullTree, BoxSelection, EmptyBoxSelection, FullBoxSelection, DistanceBasedSelection,
#   EarlyTermination, LargeDataSet, MetricBasedPruning, CountAllPairs, EmptyFirstTree, EmptySecondTree, NullTrees,
#   OverlapDetection_SameTrees, OverlapDetection_NonOverlapping, AsymmetricPairs, LargeDataSets: they run the test's
#   own selectors, C++ subclasses of BVH_Traverse / BVH_PairTraverse<double, 3, void, double> overriding RejectNode,
#   Accept, ...; a Python subclass would need a trampoline, and nanocct generates none (docs/Excluded.md). All but
#   EmptyTree, NullTree and NullTrees also build their trees with CreateSimpleTriangulationBVH, which needs
#   BVH_Triangulation<double, 3> and BVH_BinnedBuilder<double, 3> (not bound).
# - TriangulationBoxVerification, BVHRootBoxVerification: they build BVH_Triangulation<double, 3> (and
#   BVH_BinnedBuilder<double, 3>), which are not bound.
from nanocct.BVH import BVH_Vec3d
from nanocct.Bnd import BVH_Box__double__3 as Box3


def test_BVH_PairTraverseTest_IsOutVerification():
    box1 = Box3(BVH_Vec3d(0.0, 0.0, 0.0), BVH_Vec3d(3.0, 1.0, 0.0))
    box2 = Box3(BVH_Vec3d(100.0, 0.0, 0.0), BVH_Vec3d(103.0, 1.0, 0.0))

    assert box1.IsOut(box2.CornerMin(), box2.CornerMax())
    assert box2.IsOut(box1.CornerMin(), box1.CornerMax())
