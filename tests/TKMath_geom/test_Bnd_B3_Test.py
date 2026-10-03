# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_B3_Test.cxx (LGPL-2.1 with the OCCT exception)

import math

from nanocct.Bnd import Bnd_B3d, Bnd_B3f
from nanocct.gp import gp_Ax1, gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_XYZ
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def near(a, b, tol=CONF):
    return abs(a - b) <= tol


def check_corners(box, mn, mx, tol=CONF):
    aMin = box.CornerMin()
    aMax = box.CornerMax()
    assert near(aMin.X(), mn[0], tol)
    assert near(aMin.Y(), mn[1], tol)
    assert near(aMin.Z(), mn[2], tol)
    assert near(aMax.X(), mx[0], tol)
    assert near(aMax.Y(), mx[1], tol)
    assert near(aMax.Z(), mx[2], tol)


def unit_box():
    return Bnd_B3d(gp_XYZ(0.0, 0.0, 0.0), gp_XYZ(1.0, 1.0, 1.0))


def test_Bnd_B3dTest_DefaultConstructor():
    assert Bnd_B3d().IsVoid() is True


def test_Bnd_B3dTest_ConstructorWithCenterAndHSize():
    aBox = Bnd_B3d(gp_XYZ(5.0, 10.0, 15.0), gp_XYZ(2.0, 3.0, 4.0))
    assert aBox.IsVoid() is False
    check_corners(aBox, (3.0, 7.0, 11.0), (7.0, 13.0, 19.0))


def test_Bnd_B3dTest_Clear():
    aBox = unit_box()
    assert aBox.IsVoid() is False
    aBox.Clear()
    assert aBox.IsVoid() is True


def test_Bnd_B3dTest_AddPoint():
    aBox = Bnd_B3d()
    aBox.Add(gp_XYZ(1.0, 2.0, 3.0))
    assert aBox.IsVoid() is False
    check_corners(aBox, (1.0, 2.0, 3.0), (1.0, 2.0, 3.0))
    aBox.Add(gp_XYZ(4.0, 5.0, 6.0))
    check_corners(aBox, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))


def test_Bnd_B3dTest_AddPnt():
    aBox = Bnd_B3d()
    aBox.Add(gp_Pnt(1.0, 2.0, 3.0))
    assert aBox.IsVoid() is False
    aMin = aBox.CornerMin()
    assert near(aMin.X(), 1.0)
    assert near(aMin.Y(), 2.0)
    assert near(aMin.Z(), 3.0)


def test_Bnd_B3dTest_AddBox():
    aBox1 = unit_box()
    aBox2 = Bnd_B3d(gp_XYZ(3.0, 3.0, 3.0), gp_XYZ(1.0, 1.0, 1.0))
    aBox1.Add(aBox2)
    check_corners(aBox1, (-1.0, -1.0, -1.0), (4.0, 4.0, 4.0))


def test_Bnd_B3dTest_SquareExtent():
    aBox = Bnd_B3d(gp_XYZ(0.0, 0.0, 0.0), gp_XYZ(3.0, 4.0, 5.0))
    assert near(aBox.SquareExtent(), 200.0)


def test_Bnd_B3dTest_Enlarge():
    aBox = unit_box()
    aBox.Enlarge(0.5)
    check_corners(aBox, (-1.5, -1.5, -1.5), (1.5, 1.5, 1.5))


def test_Bnd_B3dTest_Limit():
    aBox1 = Bnd_B3d(gp_XYZ(0.0, 0.0, 0.0), gp_XYZ(5.0, 5.0, 5.0))
    aBox2 = Bnd_B3d(gp_XYZ(2.0, 2.0, 2.0), gp_XYZ(2.0, 2.0, 2.0))
    assert aBox1.Limit(aBox2) is True
    check_corners(aBox1, (0.0, 0.0, 0.0), (5.0, 5.0, 5.0))

    aBox3 = unit_box()
    aBox4 = Bnd_B3d(gp_XYZ(10.0, 10.0, 10.0), gp_XYZ(1.0, 1.0, 1.0))
    assert aBox3.Limit(aBox4) is False


def test_Bnd_B3dTest_IsOutPoint():
    aBox = unit_box()
    assert aBox.IsOut(gp_XYZ(0.0, 0.0, 0.0)) is False
    assert aBox.IsOut(gp_XYZ(0.5, 0.5, 0.5)) is False
    assert aBox.IsOut(gp_XYZ(2.0, 0.0, 0.0)) is True
    assert aBox.IsOut(gp_XYZ(0.0, 2.0, 0.0)) is True
    assert aBox.IsOut(gp_XYZ(0.0, 0.0, 2.0)) is True


def test_Bnd_B3dTest_IsOutSphere():
    aBox = unit_box()
    assert aBox.IsOut(gp_XYZ(0.0, 0.0, 0.0), 0.5) is False
    assert aBox.IsOut(gp_XYZ(10.0, 10.0, 10.0), 1.0) is True


def test_Bnd_B3dTest_IsOutBox():
    aBox1 = unit_box()
    aBox2 = Bnd_B3d(gp_XYZ(0.5, 0.5, 0.5), gp_XYZ(1.0, 1.0, 1.0))
    aBox3 = Bnd_B3d(gp_XYZ(5.0, 5.0, 5.0), gp_XYZ(1.0, 1.0, 1.0))
    assert aBox1.IsOut(aBox2) is False
    assert aBox1.IsOut(aBox3) is True


def test_Bnd_B3dTest_IsOutLine():
    aBox = unit_box()
    aLine1 = gp_Ax1(gp_Pnt(-2.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert aBox.IsOut(aLine1) is False
    aLine2 = gp_Ax1(gp_Pnt(-2.0, 5.0, 5.0), gp_Dir(1.0, 0.0, 0.0))
    assert aBox.IsOut(aLine2) is True


def test_Bnd_B3dTest_IsOutPlane():
    aBox = unit_box()
    aPlane1 = gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    assert aBox.IsOut(aPlane1) is False
    aPlane2 = gp_Ax3(gp_Pnt(0.0, 0.0, 5.0), gp_Dir(0.0, 0.0, 1.0))
    assert aBox.IsOut(aPlane2) is True


def test_Bnd_B3dTest_IsInBox():
    aBox1 = Bnd_B3d(gp_XYZ(0.0, 0.0, 0.0), gp_XYZ(0.5, 0.5, 0.5))
    aBox2 = Bnd_B3d(gp_XYZ(0.0, 0.0, 0.0), gp_XYZ(2.0, 2.0, 2.0))
    assert aBox1.IsIn(aBox2) is True
    assert aBox2.IsIn(aBox1) is False


def test_Bnd_B3dTest_Transformed():
    aBox = Bnd_B3d(gp_XYZ(1.0, 1.0, 1.0), gp_XYZ(1.0, 1.0, 1.0))
    aTrsf = gp_Trsf()
    aTrsf.SetTranslation(gp_Vec(2.0, 3.0, 4.0))
    check_corners(aBox.Transformed(aTrsf), (2.0, 3.0, 4.0), (4.0, 5.0, 6.0))


def test_Bnd_B3dTest_TransformedWithRotation():
    aBox = Bnd_B3d(gp_XYZ(1.0, 0.0, 0.0), gp_XYZ(0.5, 0.5, 0.5))
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2.0)
    aT = aBox.Transformed(aTrsf)
    aMin = aT.CornerMin()
    aMax = aT.CornerMax()
    assert near((aMin.X() + aMax.X()) / 2.0, 0.0, 1e-10)
    assert near((aMin.Y() + aMax.Y()) / 2.0, 1.0, 1e-10)
    assert near((aMin.Z() + aMax.Z()) / 2.0, 0.0, 1e-10)


def test_Bnd_B3dTest_SetCenterAndHSize():
    aBox = Bnd_B3d()
    aBox.SetCenter(gp_XYZ(5.0, 10.0, 15.0))
    aBox.SetHSize(gp_XYZ(2.0, 3.0, 4.0))
    check_corners(aBox, (3.0, 7.0, 11.0), (7.0, 13.0, 19.0))


def test_Bnd_B3fTest_FloatPrecision():
    aBox = Bnd_B3f(gp_XYZ(1.0, 2.0, 3.0), gp_XYZ(0.5, 0.5, 0.5))
    assert aBox.IsVoid() is False
    check_corners(aBox, (0.5, 1.5, 2.5), (1.5, 2.5, 3.5), 1e-5)


def test_Bnd_B3dTest_IsOutRay():
    aBox = Bnd_B3d(gp_XYZ(1.0, 1.0, 1.0), gp_XYZ(1.0, 1.0, 1.0))
    aRay1 = gp_Ax1(gp_Pnt(-1.0, 1.0, 1.0), gp_Dir(1.0, 0.0, 0.0))
    assert aBox.IsOut(aRay1, True) is False
    aRay2 = gp_Ax1(gp_Pnt(1.0, 1.0, 1.0), gp_Dir(1.0, 0.0, 0.0))
    assert aBox.IsOut(aRay2, True) is False
    aRay3 = gp_Ax1(gp_Pnt(-1.0, 1.0, 1.0), gp_Dir(-1.0, 0.0, 0.0))
    assert aBox.IsOut(aRay3, True) is True


def test_Bnd_B3dTest_IsOutLineWithOverthickness():
    aBox = unit_box()
    aLine = gp_Ax1(gp_Pnt(-2.0, 1.2, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert aBox.IsOut(aLine, False, 0.0) is True
    assert aBox.IsOut(aLine, False, 0.3) is False
