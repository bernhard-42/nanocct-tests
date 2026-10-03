# Translated from OCCT src/Visualization/TKService/GTests/Graphic3d_BndBox_Test.cxx (LGPL-2.1 with the OCCT exception)
# The six Transformation* TESTs are left out: neither BVH_Box::Transform nor gp_Trsf::GetMat4 is bound.
import pytest

from nanocct.BVH import BVH_Vec3d
from nanocct.Graphic3d import Graphic3d_BndBox3d


def _corners(box):
    lo, hi = box.CornerMin(), box.CornerMax()
    return (lo.x(), lo.y(), lo.z()), (hi.x(), hi.y(), hi.z())


def test_Graphic3d_BndBox3dTest_DefaultConstructor():
    assert not Graphic3d_BndBox3d().IsValid()


def test_Graphic3d_BndBox3dTest_PointConstructor():
    box = Graphic3d_BndBox3d(BVH_Vec3d(1.0, 2.0, 3.0))
    assert box.IsValid()
    assert _corners(box) == ((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))


def test_Graphic3d_BndBox3dTest_PointsConstructor():
    box = Graphic3d_BndBox3d(BVH_Vec3d(1.0, 2.0, 3.0), BVH_Vec3d(4.0, 5.0, 6.0))
    assert box.IsValid()
    assert _corners(box) == ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0))


def test_Graphic3d_BndBox3dTest_AddPoint():
    box = Graphic3d_BndBox3d()
    box.Add(BVH_Vec3d(1.5, 2.5, 3.5))
    assert box.IsValid()
    assert _corners(box) == ((1.5, 2.5, 3.5), (1.5, 2.5, 3.5))


def test_Graphic3d_BndBox3dTest_CombineBoxes():
    box1 = Graphic3d_BndBox3d(BVH_Vec3d(1.0, 2.0, 3.0), BVH_Vec3d(4.0, 5.0, 6.0))
    box2 = Graphic3d_BndBox3d(BVH_Vec3d(2.0, 0.0, 0.0), BVH_Vec3d(6.0, 3.0, 6.0))
    box1.Combine(box2)
    assert box1.IsValid()
    assert _corners(box1) == ((1.0, 0.0, 0.0), (6.0, 5.0, 6.0))


def test_Graphic3d_BndBox3dTest_BoxSize():
    box = Graphic3d_BndBox3d(BVH_Vec3d(0.5, -2.0, -3.0), BVH_Vec3d(3.5, 1.0, 3.0))
    size = box.Size()
    assert (size.x(), size.y(), size.z()) == pytest.approx((3.0, 3.0, 6.0))


def test_Graphic3d_BndBox3dTest_BoxCenter():
    box = Graphic3d_BndBox3d(BVH_Vec3d(-4.0, -4.0, -4.0), BVH_Vec3d(4.0, 4.0, 4.0))
    c = box.Center()
    assert (c.x(), c.y(), c.z()) == (0.0, 0.0, 0.0)


def test_Graphic3d_BndBox3dTest_BoxArea():
    box = Graphic3d_BndBox3d(BVH_Vec3d(0.0, 0.0, 0.0), BVH_Vec3d(2.0, 3.0, 4.0))
    assert box.Area() == pytest.approx(52.0)
