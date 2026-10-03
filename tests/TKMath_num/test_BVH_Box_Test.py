# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_Box_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BVH import BVH_Vec2d, BVH_Vec3d
from nanocct.Bnd import BVH_Box__double__2 as Box2, BVH_Box__double__3 as Box3

TOL = 1e-7  # Precision::Confusion()


def near(a, b, tol=TOL):
    assert abs(a - b) <= tol, (a, b)


def V(x, y, z):
    return BVH_Vec3d(x, y, z)


def B(a, b):
    return Box3(V(*a), V(*b))


def test_BVH_BoxTest_DefaultConstructor():
    assert not Box3().IsValid()


def test_BVH_BoxTest_ConstructorWithCorners():
    box = Box3(V(0.0, 0.0, 0.0), V(1.0, 2.0, 3.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 0.0)
    near(box.CornerMin().y(), 0.0)
    near(box.CornerMin().z(), 0.0)
    near(box.CornerMax().x(), 1.0)
    near(box.CornerMax().y(), 2.0)
    near(box.CornerMax().z(), 3.0)


def test_BVH_BoxTest_Add():
    box = Box3()
    box.Add(V(1.0, 2.0, 3.0))
    assert box.IsValid()
    box.Add(V(-1.0, -2.0, -3.0))
    near(box.CornerMin().x(), -1.0)
    near(box.CornerMin().y(), -2.0)
    near(box.CornerMin().z(), -3.0)
    near(box.CornerMax().x(), 1.0)
    near(box.CornerMax().y(), 2.0)
    near(box.CornerMax().z(), 3.0)


def test_BVH_BoxTest_Combine():
    b1 = B((0, 0, 0), (1, 1, 1))
    b2 = B((2, 2, 2), (3, 3, 3))
    b1.Combine(b2)
    near(b1.CornerMin().x(), 0.0)
    near(b1.CornerMin().y(), 0.0)
    near(b1.CornerMin().z(), 0.0)
    near(b1.CornerMax().x(), 3.0)
    near(b1.CornerMax().y(), 3.0)
    near(b1.CornerMax().z(), 3.0)


def test_BVH_BoxTest_Size():
    s = B((0, 0, 0), (2, 3, 4)).Size()
    near(s.x(), 2.0)
    near(s.y(), 3.0)
    near(s.z(), 4.0)


def test_BVH_BoxTest_Center():
    c = B((0, 0, 0), (2, 4, 6)).Center()
    near(c.x(), 1.0)
    near(c.y(), 2.0)
    near(c.z(), 3.0)


def test_BVH_BoxTest_Area():
    near(B((0, 0, 0), (1, 2, 3)).Area(), 22.0)


def test_BVH_BoxTest_IsOut():
    b1 = B((0, 0, 0), (1, 1, 1))
    b2 = B((2, 2, 2), (3, 3, 3))
    b3 = B((0.5, 0.5, 0.5), (1.5, 1.5, 1.5))
    assert b1.IsOut(b2)
    assert not b1.IsOut(b3)


def test_BVH_BoxTest_Clear():
    box = B((0, 0, 0), (1, 1, 1))
    assert box.IsValid()
    box.Clear()
    assert not box.IsValid()


def test_BVH_BoxTest_Box2D():
    box = Box2()
    box.Add(BVH_Vec2d(0.0, 0.0))
    box.Add(BVH_Vec2d(1.0, 1.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 0.0)
    near(box.CornerMin().y(), 0.0)
    near(box.CornerMax().x(), 1.0)
    near(box.CornerMax().y(), 1.0)
    near(box.Area(), 1.0)


def test_BVH_BoxTest_SinglePointBox():
    box = Box3()
    box.Add(V(5.0, 5.0, 5.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 5.0)
    near(box.CornerMax().x(), 5.0)
    s = box.Size()
    near(s.x(), 0.0)
    near(s.y(), 0.0)
    near(s.z(), 0.0)
    near(box.Area(), 0.0)


def test_BVH_BoxTest_NegativeCoordinates():
    box = B((-10, -20, -30), (-5, -10, -15))
    assert box.IsValid()
    c = box.Center()
    near(c.x(), -7.5)
    near(c.y(), -15.0)
    near(c.z(), -22.5)
    s = box.Size()
    near(s.x(), 5.0)
    near(s.y(), 10.0)
    near(s.z(), 15.0)


def test_BVH_BoxTest_LargeValues():
    box = B((1e10, 1e10, 1e10), (1e10 + 1.0, 1e10 + 2.0, 1e10 + 3.0))
    assert box.IsValid()
    s = box.Size()
    near(s.x(), 1.0, 1e-5)
    near(s.y(), 2.0, 1e-5)
    near(s.z(), 3.0, 1e-5)


def test_BVH_BoxTest_CombineWithInvalid():
    b1 = B((0, 0, 0), (1, 1, 1))
    b1.Combine(Box3())
    assert b1.IsValid()
    near(b1.CornerMin().x(), 0.0)
    near(b1.CornerMax().x(), 1.0)


def test_BVH_BoxTest_AddToInvalid():
    b1 = Box3()
    b1.Combine(B((0, 0, 0), (1, 1, 1)))
    assert b1.IsValid()
    near(b1.CornerMin().x(), 0.0)
    near(b1.CornerMax().x(), 1.0)


def test_BVH_BoxTest_IsOutTouchingBoxes():
    assert not B((0, 0, 0), (1, 1, 1)).IsOut(B((1, 0, 0), (2, 1, 1)))


def test_BVH_BoxTest_IsOutTouchingAtEdge():
    assert not B((0, 0, 0), (1, 1, 1)).IsOut(B((1, 1, 0), (2, 2, 1)))


def test_BVH_BoxTest_IsOutTouchingAtCorner():
    assert not B((0, 0, 0), (1, 1, 1)).IsOut(B((1, 1, 1), (2, 2, 2)))


def test_BVH_BoxTest_AreaUnitCube():
    near(B((0, 0, 0), (1, 1, 1)).Area(), 6.0)


def test_BVH_BoxTest_CenterAtOrigin():
    c = B((-1, -1, -1), (1, 1, 1)).Center()
    near(c.x(), 0.0)
    near(c.y(), 0.0)
    near(c.z(), 0.0)


def test_BVH_BoxTest_MultipleAdds():
    box = Box3()
    box.Add(V(5.0, 3.0, 1.0))
    box.Add(V(-2.0, 7.0, 4.0))
    box.Add(V(1.0, -1.0, 8.0))
    box.Add(V(0.0, 2.0, -3.0))
    near(box.CornerMin().x(), -2.0)
    near(box.CornerMin().y(), -1.0)
    near(box.CornerMin().z(), -3.0)
    near(box.CornerMax().x(), 5.0)
    near(box.CornerMax().y(), 7.0)
    near(box.CornerMax().z(), 8.0)


def test_BVH_BoxTest_FlatBox2D():
    box = B((0, 0, 5), (3, 4, 5))
    assert box.IsValid()
    s = box.Size()
    near(s.x(), 3.0)
    near(s.y(), 4.0)
    near(s.z(), 0.0)
    near(box.Area(), 24.0)


def test_BVH_BoxTest_FlatBox1D():
    box = B((0, 5, 5), (10, 5, 5))
    assert box.IsValid()
    s = box.Size()
    near(s.x(), 10.0)
    near(s.y(), 0.0)
    near(s.z(), 0.0)
    assert box.Area() >= 0.0


def test_BVH_BoxTest_CombineMultiple():
    b1 = B((0, 0, 0), (1, 1, 1))
    b1.Combine(B((2, 0, 0), (3, 1, 1)))
    b1.Combine(B((0, 2, 0), (1, 3, 1)))
    near(b1.CornerMin().x(), 0.0)
    near(b1.CornerMin().y(), 0.0)
    near(b1.CornerMin().z(), 0.0)
    near(b1.CornerMax().x(), 3.0)
    near(b1.CornerMax().y(), 3.0)
    near(b1.CornerMax().z(), 1.0)


def test_BVH_BoxTest_IsOutPartialOverlap():
    b1 = B((0, 0, 0), (2, 2, 2))
    b2 = B((1, 1, 1), (3, 3, 3))
    assert not b1.IsOut(b2)
    assert not b2.IsOut(b1)


def test_BVH_BoxTest_IsOutContained():
    b1 = B((0, 0, 0), (10, 10, 10))
    b2 = B((2, 2, 2), (3, 3, 3))
    assert not b1.IsOut(b2)
    assert not b2.IsOut(b1)


def test_BVH_BoxTest_Box2DIsOut():
    b1 = Box2(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(1.0, 1.0))
    b2 = Box2(BVH_Vec2d(2.0, 2.0), BVH_Vec2d(3.0, 3.0))
    b3 = Box2(BVH_Vec2d(0.5, 0.5), BVH_Vec2d(1.5, 1.5))
    assert b1.IsOut(b2)
    assert not b1.IsOut(b3)


def test_BVH_BoxTest_Box2DCenter():
    c = Box2(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(4.0, 6.0)).Center()
    near(c.x(), 2.0)
    near(c.y(), 3.0)


def test_BVH_BoxTest_Box2DSize():
    s = Box2(BVH_Vec2d(1.0, 2.0), BVH_Vec2d(4.0, 7.0)).Size()
    near(s.x(), 3.0)
    near(s.y(), 5.0)


def test_BVH_BoxTest_VerySmallBox():
    small = 1e-10
    box = B((0, 0, 0), (small, small, small))
    assert box.IsValid()
    s = box.Size()
    near(s.x(), small, 1e-15)
    near(s.y(), small, 1e-15)
    near(s.z(), small, 1e-15)


def test_BVH_BoxTest_SymmetricBox():
    box = B((-5, -5, -5), (5, 5, 5))
    c = box.Center()
    near(c.x(), 0.0)
    near(c.y(), 0.0)
    near(c.z(), 0.0)
    s = box.Size()
    near(s.x(), 10.0)
    near(s.y(), 10.0)
    near(s.z(), 10.0)


def test_BVH_BoxTest_NonCubicBox():
    box = B((0, 0, 0), (1, 10, 100))
    s = box.Size()
    near(s.x(), 1.0)
    near(s.y(), 10.0)
    near(s.z(), 100.0)
    near(box.Area(), 2220.0)


def test_BVH_BoxTest_ClearAndReuse():
    box = B((0, 0, 0), (1, 1, 1))
    assert box.IsValid()
    box.Clear()
    assert not box.IsValid()
    box.Add(V(5.0, 5.0, 5.0))
    box.Add(V(10.0, 10.0, 10.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 5.0)
    near(box.CornerMax().x(), 10.0)


def test_BVH_BoxTest_IsOutSameBox():
    box = B((0, 0, 0), (1, 1, 1))
    assert not box.IsOut(box)


def test_BVH_BoxTest_CombineSameBox():
    b1 = B((0, 0, 0), (1, 1, 1))
    b1.Combine(B((0, 0, 0), (1, 1, 1)))
    near(b1.CornerMin().x(), 0.0)
    near(b1.CornerMax().x(), 1.0)


def test_BVH_BoxTest_IsOutNearMiss():
    assert B((0, 0, 0), (1, 1, 1)).IsOut(B((1.0001, 0, 0), (2, 1, 1)))


def test_BVH_BoxTest_AddDuplicatePoint():
    box = Box3()
    for _ in range(3):
        box.Add(V(1.0, 2.0, 3.0))
    near(box.CornerMin().x(), 1.0)
    near(box.CornerMax().x(), 1.0)
    near(box.Size().x(), 0.0)


def test_BVH_BoxTest_SinglePointConstructor():
    box = Box3(V(5.0, 10.0, 15.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 5.0)
    near(box.CornerMin().y(), 10.0)
    near(box.CornerMin().z(), 15.0)
    near(box.CornerMax().x(), 5.0)
    near(box.CornerMax().y(), 10.0)
    near(box.CornerMax().z(), 15.0)
    s = box.Size()
    near(s.x(), 0.0)
    near(s.y(), 0.0)
    near(s.z(), 0.0)


def test_BVH_BoxTest_SinglePointConstructor2D():
    box = Box2(BVH_Vec2d(3.0, 7.0))
    assert box.IsValid()
    near(box.CornerMin().x(), 3.0)
    near(box.CornerMin().y(), 7.0)
    near(box.CornerMax().x(), 3.0)
    near(box.CornerMax().y(), 7.0)


def test_BVH_BoxTest_SinglePointConstructorOrigin():
    box = Box3(V(0.0, 0.0, 0.0))
    assert box.IsValid()
    near(box.Center().x(), 0.0)
    near(box.Center().y(), 0.0)
    near(box.Center().z(), 0.0)


def test_BVH_BoxTest_CenterByAxis():
    box = B((0, 0, 0), (10, 20, 30))
    near(box.Center(0), 5.0)
    near(box.Center(1), 10.0)
    near(box.Center(2), 15.0)


def test_BVH_BoxTest_CenterByAxis2D():
    box = Box2(BVH_Vec2d(2.0, 4.0), BVH_Vec2d(8.0, 12.0))
    near(box.Center(0), 5.0)
    near(box.Center(1), 8.0)


def test_BVH_BoxTest_CenterByAxisNegative():
    box = B((-10, -20, -30), (10, 20, 30))
    near(box.Center(0), 0.0)
    near(box.Center(1), 0.0)
    near(box.Center(2), 0.0)


def test_BVH_BoxTest_IsOutPoint_Inside():
    box = B((0, 0, 0), (10, 10, 10))
    assert not box.IsOut(V(5.0, 5.0, 5.0))
    assert not box.IsOut(V(1.0, 1.0, 1.0))
    assert not box.IsOut(V(9.0, 9.0, 9.0))


def test_BVH_BoxTest_IsOutPoint_Outside():
    box = B((0, 0, 0), (10, 10, 10))
    assert box.IsOut(V(11.0, 5.0, 5.0))
    assert box.IsOut(V(5.0, 11.0, 5.0))
    assert box.IsOut(V(5.0, 5.0, 11.0))
    assert box.IsOut(V(-1.0, 5.0, 5.0))
    assert box.IsOut(V(15.0, 15.0, 15.0))


def test_BVH_BoxTest_IsOutPoint_OnBoundary():
    box = B((0, 0, 0), (10, 10, 10))
    assert not box.IsOut(V(0.0, 5.0, 5.0))
    assert not box.IsOut(V(10.0, 5.0, 5.0))
    assert not box.IsOut(V(5.0, 0.0, 5.0))
    assert not box.IsOut(V(5.0, 10.0, 5.0))
    assert not box.IsOut(V(0.0, 0.0, 0.0))
    assert not box.IsOut(V(10.0, 10.0, 10.0))


def test_BVH_BoxTest_IsOutPoint_InvalidBox():
    box = Box3()
    assert box.IsOut(V(0.0, 0.0, 0.0))
    assert box.IsOut(V(5.0, 5.0, 5.0))


def test_BVH_BoxTest_IsOutPoint_2D():
    box = Box2(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(5.0, 5.0))
    assert not box.IsOut(BVH_Vec2d(2.5, 2.5))
    assert box.IsOut(BVH_Vec2d(6.0, 2.5))
    assert box.IsOut(BVH_Vec2d(2.5, 6.0))
    assert not box.IsOut(BVH_Vec2d(0.0, 0.0))


def test_BVH_BoxTest_IsOutPoint_NegativeCoords():
    box = B((-5, -5, -5), (5, 5, 5))
    assert not box.IsOut(V(0.0, 0.0, 0.0))
    assert not box.IsOut(V(-3.0, -3.0, -3.0))
    assert box.IsOut(V(-6.0, 0.0, 0.0))


def test_BVH_BoxTest_Contains_FullyContained():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(B((2, 2, 2), (8, 8, 8)))
    assert is_contained
    assert has_overlap


def test_BVH_BoxTest_Contains_NotContained():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(B((8, 8, 8), (12, 12, 12)))
    assert not is_contained
    assert has_overlap


def test_BVH_BoxTest_Contains_NoOverlap():
    is_contained, has_overlap = B((0, 0, 0), (5, 5, 5)).Contains(B((10, 10, 10), (15, 15, 15)))
    assert not is_contained
    assert not has_overlap


def test_BVH_BoxTest_Contains_SameBox():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(B((0, 0, 0), (10, 10, 10)))
    assert is_contained
    assert has_overlap


def test_BVH_BoxTest_Contains_TouchingBoundary():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(B((0, 0, 0), (5, 5, 5)))
    assert is_contained
    assert has_overlap


def test_BVH_BoxTest_Contains_InvalidBox():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(Box3())
    assert not is_contained
    assert not has_overlap


def test_BVH_BoxTest_Contains_InvalidContainer():
    is_contained, has_overlap = Box3().Contains(B((0, 0, 0), (10, 10, 10)))
    assert not is_contained
    assert not has_overlap


def test_BVH_BoxTest_Contains_PartialOverlapOneAxis():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(B((5, 5, 5), (15, 8, 8)))
    assert not is_contained
    assert has_overlap


def test_BVH_BoxTest_Contains_2D():
    b1 = Box2(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(10.0, 10.0))
    b2 = Box2(BVH_Vec2d(2.0, 2.0), BVH_Vec2d(8.0, 8.0))
    is_contained, has_overlap = b1.Contains(b2)
    assert is_contained
    assert has_overlap


def test_BVH_BoxTest_ContainsByCorners_FullyContained():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(V(2.0, 2.0, 2.0), V(8.0, 8.0, 8.0))
    assert is_contained
    assert has_overlap


def test_BVH_BoxTest_ContainsByCorners_NotContained():
    is_contained, has_overlap = B((0, 0, 0), (10, 10, 10)).Contains(V(8.0, 8.0, 8.0), V(12.0, 12.0, 12.0))
    assert not is_contained
    assert has_overlap


def test_BVH_BoxTest_ModifyCornerMin():
    box = B((0, 0, 0), (10, 10, 10))
    # C++: aBox.CornerMin() = BVH_Vec3d(-5, -5, -5)  (non-const reference)
    box.CornerMin().SetValues(-5.0, -5.0, -5.0)
    near(box.CornerMin().x(), -5.0)
    near(box.CornerMin().y(), -5.0)
    near(box.CornerMin().z(), -5.0)
    near(box.CornerMax().x(), 10.0)


def test_BVH_BoxTest_ModifyCornerMax():
    box = B((0, 0, 0), (10, 10, 10))
    box.CornerMax().SetValues(20.0, 30.0, 40.0)
    near(box.CornerMax().x(), 20.0)
    near(box.CornerMax().y(), 30.0)
    near(box.CornerMax().z(), 40.0)
    near(box.CornerMin().x(), 0.0)


def test_BVH_BoxTest_ModifyCornerComponents():
    box = B((0, 0, 0), (10, 10, 10))
    box.CornerMin().Setx(-1.0)
    box.CornerMin().Sety(-2.0)
    box.CornerMax().Setz(15.0)
    near(box.CornerMin().x(), -1.0)
    near(box.CornerMin().y(), -2.0)
    near(box.CornerMin().z(), 0.0)
    near(box.CornerMax().z(), 15.0)


def test_BVH_BoxTest_Area_DegenerateBox2D():
    area = Box2(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(5.0, 0.0)).Area()
    assert area >= 0.0
    near(area, 5.0)


def test_BVH_BoxTest_IsOut_TwoCorners_Overlapping():
    assert not B((0, 0, 0), (10, 10, 10)).IsOut(V(5.0, 5.0, 5.0), V(15.0, 15.0, 15.0))


def test_BVH_BoxTest_IsOut_TwoCorners_Disjoint():
    assert B((0, 0, 0), (10, 10, 10)).IsOut(V(20.0, 20.0, 20.0), V(30.0, 30.0, 30.0))


def test_BVH_BoxTest_IsOut_TwoCorners_Contained():
    assert not B((0, 0, 0), (10, 10, 10)).IsOut(V(2.0, 2.0, 2.0), V(8.0, 8.0, 8.0))
