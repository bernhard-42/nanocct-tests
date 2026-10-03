# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_B2_Test.cxx (LGPL-2.1 with the OCCT exception)

from nanocct.Bnd import Bnd_B2d, Bnd_B2f
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d, gp_XY
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def near(a, b, tol=CONF):
    return abs(a - b) <= tol


def check_corners(box, mn, mx, tol=CONF):
    aMin = box.CornerMin()
    aMax = box.CornerMax()
    assert near(aMin.X(), mn[0], tol)
    assert near(aMin.Y(), mn[1], tol)
    assert near(aMax.X(), mx[0], tol)
    assert near(aMax.Y(), mx[1], tol)


def test_Bnd_B2dTest_DefaultConstructor():
    assert Bnd_B2d().IsVoid() is True


def test_Bnd_B2dTest_ConstructorWithCenterAndHSize():
    aBox = Bnd_B2d(gp_XY(5.0, 10.0), gp_XY(2.0, 3.0))
    assert aBox.IsVoid() is False
    check_corners(aBox, (3.0, 7.0), (7.0, 13.0))


def test_Bnd_B2dTest_Clear():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    assert aBox.IsVoid() is False
    aBox.Clear()
    assert aBox.IsVoid() is True


def test_Bnd_B2dTest_AddPoint():
    aBox = Bnd_B2d()
    aBox.Add(gp_XY(1.0, 2.0))
    assert aBox.IsVoid() is False
    check_corners(aBox, (1.0, 2.0), (1.0, 2.0))
    aBox.Add(gp_XY(4.0, 5.0))
    check_corners(aBox, (1.0, 2.0), (4.0, 5.0))


def test_Bnd_B2dTest_AddPnt2d():
    aBox = Bnd_B2d()
    aBox.Add(gp_Pnt2d(1.0, 2.0))
    assert aBox.IsVoid() is False
    aMin = aBox.CornerMin()
    assert near(aMin.X(), 1.0)
    assert near(aMin.Y(), 2.0)


def test_Bnd_B2dTest_AddBox():
    aBox1 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    aBox2 = Bnd_B2d(gp_XY(3.0, 3.0), gp_XY(1.0, 1.0))
    aBox1.Add(aBox2)
    check_corners(aBox1, (-1.0, -1.0), (4.0, 4.0))


def test_Bnd_B2dTest_SquareExtent():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(3.0, 4.0))
    assert near(aBox.SquareExtent(), 100.0)


def test_Bnd_B2dTest_Enlarge():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    aBox.Enlarge(0.5)
    check_corners(aBox, (-1.5, -1.5), (1.5, 1.5))


def test_Bnd_B2dTest_Limit():
    aBox1 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(5.0, 5.0))
    aBox2 = Bnd_B2d(gp_XY(2.0, 2.0), gp_XY(2.0, 2.0))
    assert aBox1.Limit(aBox2) is True
    check_corners(aBox1, (0.0, 0.0), (5.0, 5.0))

    aBox3 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    aBox4 = Bnd_B2d(gp_XY(10.0, 10.0), gp_XY(1.0, 1.0))
    assert aBox3.Limit(aBox4) is False


def test_Bnd_B2dTest_IsOutPoint():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    assert aBox.IsOut(gp_XY(0.0, 0.0)) is False
    assert aBox.IsOut(gp_XY(0.5, 0.5)) is False
    assert aBox.IsOut(gp_XY(2.0, 0.0)) is True
    assert aBox.IsOut(gp_XY(0.0, 2.0)) is True


def test_Bnd_B2dTest_IsOutCircle():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    assert aBox.IsOut(gp_XY(0.0, 0.0), 0.5) is False
    assert aBox.IsOut(gp_XY(10.0, 10.0), 1.0) is True


def test_Bnd_B2dTest_IsOutBox():
    aBox1 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    aBox2 = Bnd_B2d(gp_XY(0.5, 0.5), gp_XY(1.0, 1.0))
    aBox3 = Bnd_B2d(gp_XY(5.0, 5.0), gp_XY(1.0, 1.0))
    assert aBox1.IsOut(aBox2) is False
    assert aBox1.IsOut(aBox3) is True


def test_Bnd_B2dTest_IsOutLine():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    aLine1 = gp_Ax2d(gp_Pnt2d(-2.0, 0.0), gp_Dir2d(1.0, 0.0))
    assert aBox.IsOut(aLine1) is False
    aLine2 = gp_Ax2d(gp_Pnt2d(-2.0, 5.0), gp_Dir2d(1.0, 0.0))
    assert aBox.IsOut(aLine2) is True


def test_Bnd_B2dTest_IsOutSegment():
    aBox = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(1.0, 1.0))
    assert aBox.IsOut(gp_XY(-2.0, 0.0), gp_XY(2.0, 0.0)) is False
    assert aBox.IsOut(gp_XY(5.0, 5.0), gp_XY(6.0, 6.0)) is True


def test_Bnd_B2dTest_IsInBox():
    aBox1 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(0.5, 0.5))
    aBox2 = Bnd_B2d(gp_XY(0.0, 0.0), gp_XY(2.0, 2.0))
    assert aBox1.IsIn(aBox2) is True
    assert aBox2.IsIn(aBox1) is False


def test_Bnd_B2dTest_Transformed():
    aBox = Bnd_B2d(gp_XY(1.0, 1.0), gp_XY(1.0, 1.0))
    aTrsf = gp_Trsf2d()
    aTrsf.SetTranslation(gp_Vec2d(2.0, 3.0))
    check_corners(aBox.Transformed(aTrsf), (2.0, 3.0), (4.0, 5.0))


def test_Bnd_B2dTest_SetCenterAndHSize():
    aBox = Bnd_B2d()
    aBox.SetCenter(gp_XY(5.0, 10.0))
    aBox.SetHSize(gp_XY(2.0, 3.0))
    check_corners(aBox, (3.0, 7.0), (7.0, 13.0))


def test_Bnd_B2fTest_FloatPrecision():
    aBox = Bnd_B2f(gp_XY(1.0, 2.0), gp_XY(0.5, 0.5))
    assert aBox.IsVoid() is False
    check_corners(aBox, (0.5, 1.5), (1.5, 2.5), 1e-5)
