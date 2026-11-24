# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_Triangulation_Test.cxx (LGPL-2.1 with the OCCT exception)
# BVH_Triangulation<float, 3> is bound as OpenGl_BVHTriangulation3f (its OCCT typedef). BVH::Array<T, N>::Append is a
# C++ helper (not bound) that calls theArray.Append(theElement); Vertices / Elements are views of the members, so
# .Append on them is the same call.
# Not translated: DefaultConstructor, AddSingleTriangle, AddMultipleTriangles, BoxForSingleTriangle,
# BoxForDegenerateTriangle, BoxForFlatTriangle, CenterComputation, CenterAlongXAxis, CenterAlongYAxis,
# CenterAlongZAxis, SwapTwoTriangles, SwapPreservesVertices, SharedVertices, NegativeCoordinates (all on
# BVH_Triangulation<double, 3>) and Triangulation2D (BVH_Triangulation<double, 2>): neither instantiation is bound.
from nanocct.BVH import BVH_Vec3f, BVH_Vec4i
from nanocct.OpenGl import OpenGl_BVHTriangulation3f


def test_BVH_TriangulationTest_FloatPrecision():
    triangulation = OpenGl_BVHTriangulation3f()

    triangulation.Vertices.Append(BVH_Vec3f(0.0, 0.0, 0.0))
    triangulation.Vertices.Append(BVH_Vec3f(1.0, 0.0, 0.0))
    triangulation.Vertices.Append(BVH_Vec3f(0.0, 1.0, 0.0))
    triangulation.Elements.Append(BVH_Vec4i(0, 1, 2, 0))

    assert triangulation.Size() == 1

    box = triangulation.Box(0)
    assert abs(box.CornerMax().x() - 1.0) <= 1e-6
    assert abs(box.CornerMax().y() - 1.0) <= 1e-6
