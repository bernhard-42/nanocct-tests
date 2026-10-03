# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_Vec4_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# NCollection_Vec4<float> / NCollection_Vec3<float> live in nanocct.Quantity, NCollection_Mat4<float> is
# nanocct.BVH.BVH_Mat4f. Component writes x() = v are spelled Setx(v).

from nanocct.BVH import BVH_Mat4f
from nanocct.Quantity import NCollection_Vec3__float as Vec3f
from nanocct.Quantity import NCollection_Vec4__float as Vec4f


def test_NCollection_Vec4Test_BasicConstruction():
    v1 = Vec4f()
    assert v1.x() == 0.0
    assert v1.y() == 0.0
    assert v1.z() == 0.0
    assert v1.w() == 0.0
    v2 = Vec4f(1.0, 2.0, 3.0, 4.0)
    assert v2.x() == 1.0
    assert v2.y() == 2.0
    assert v2.z() == 3.0
    assert v2.w() == 4.0


def test_NCollection_Vec4Test_XyzMethod():
    v = Vec4f(2.0, 3.0, 4.0, 5.0)
    v3 = v.xyz()
    assert v3.x() == 2.0
    assert v3.y() == 3.0
    assert v3.z() == 4.0


def test_NCollection_Vec4Test_MatrixMultiplicationAndTransformation():
    m = BVH_Mat4f()
    m.Translate(Vec3f(4.0, 3.0, 1.0))
    points1 = [None] * 8
    for x in range(2):
        for y in range(2):
            for z in range(2):
                points1[x * 4 + y * 2 + z] = Vec4f(-1.0 + 2.0 * x, -1.0 + 2.0 * y, -1.0 + 2.0 * z, 1.0)
    points2 = [None] * 8
    for i in range(8):
        points1[i] = m * points1[i]
        points2[i] = points1[i].xyz() / points1[i].w()
    assert abs(points2[7].SquareModulus() - 45.0) <= 0.001
    assert abs(points2[0].SquareModulus() - 13.0) <= 0.001


def test_NCollection_Vec4Test_ComponentAccess():
    v = Vec4f(1.5, 2.5, 3.5, 4.5)
    assert v.x() == 1.5
    assert v.y() == 2.5
    assert v.z() == 3.5
    assert v.w() == 4.5
    v.Setx(10.0)
    v.Sety(20.0)
    v.Setz(30.0)
    v.Setw(40.0)
    assert v.x() == 10.0
    assert v.y() == 20.0
    assert v.z() == 30.0
    assert v.w() == 40.0


def test_NCollection_Vec4Test_HomogeneousCoordinateDivision():
    v = Vec4f(8.0, 12.0, 16.0, 4.0)
    r = v.xyz() / v.w()
    assert r.x() == 2.0
    assert r.y() == 3.0
    assert r.z() == 4.0
