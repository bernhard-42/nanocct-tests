# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_Box2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box2d
from nanocct.gp import gp_Dir2d, gp_Lin2d, gp_Pnt2d, gp_Trsf2d


def _get(box):
    # (Xmin, Ymin, Xmax, Ymax), the out-parameter overload
    return box.Get__float__float__float__float()


def _box(xmin, ymin, xmax, ymax):
    box = Bnd_Box2d()
    box.Update(xmin, ymin, xmax, ymax)
    return box


def test_Bnd_Box2dTest_DefaultConstructor():
    box = Bnd_Box2d()
    assert box.IsVoid() is True
    assert box.IsWhole() is False
    assert box.GetGap() == 0.0


def test_Bnd_Box2dTest_SetVoid():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.IsVoid() is False
    box.SetVoid()
    assert box.IsVoid() is True


def test_Bnd_Box2dTest_SetWhole():
    box = Bnd_Box2d()
    box.SetWhole()
    assert box.IsWhole() is True
    assert box.IsVoid() is False


def test_Bnd_Box2dTest_Update_Bounds():
    assert _get(_box(1.0, 2.0, 10.0, 20.0)) == (1.0, 2.0, 10.0, 20.0)


def test_Bnd_Box2dTest_Update_SinglePoint():
    box = Bnd_Box2d()
    box.Update(5.0, 7.0)
    assert _get(box) == (5.0, 7.0, 5.0, 7.0)


def test_Bnd_Box2dTest_Update_Expansion():
    box = _box(1.0, 2.0, 10.0, 20.0)
    box.Update(0.0, 0.0, 15.0, 25.0)
    assert _get(box) == (0.0, 0.0, 15.0, 25.0)


def test_Bnd_Box2dTest_GapOperations():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.GetGap() == 0.0
    box.SetGap(2.0)
    assert box.GetGap() == 2.0
    box.SetGap(-3.0)
    assert box.GetGap() == 3.0


def test_Bnd_Box2dTest_Enlarge():
    box = _box(0.0, 0.0, 10.0, 10.0)
    box.Enlarge(5.0)
    assert box.GetGap() == 5.0
    box.Enlarge(3.0)
    assert box.GetGap() == 5.0
    box.Enlarge(7.0)
    assert box.GetGap() == 7.0


def test_Bnd_Box2dTest_Get_WithGap():
    box = _box(1.0, 2.0, 10.0, 20.0)
    box.SetGap(0.5)
    assert _get(box) == (0.5, 1.5, 10.5, 20.5)


def test_Bnd_Box2dTest_Get_StructuredBindings():
    limits = _box(1.0, 2.0, 10.0, 20.0).Get()
    assert limits.Xmin == 1.0
    assert limits.Xmax == 10.0
    assert limits.Ymin == 2.0
    assert limits.Ymax == 20.0


def test_Bnd_Box2dTest_Set_Point():
    box = Bnd_Box2d()
    box.Set(gp_Pnt2d(5.0, 7.0))
    assert _get(box) == (5.0, 7.0, 5.0, 7.0)


def test_Bnd_Box2dTest_Add_Point():
    box = Bnd_Box2d()
    box.Add(gp_Pnt2d(1.0, 2.0))
    box.Add(gp_Pnt2d(10.0, 20.0))
    assert _get(box) == (1.0, 2.0, 10.0, 20.0)


def test_Bnd_Box2dTest_Add_Box():
    box1 = _box(0.0, 0.0, 5.0, 5.0)
    box1.Add(_box(3.0, 3.0, 10.0, 10.0))
    assert _get(box1) == (0.0, 0.0, 10.0, 10.0)


def test_Bnd_Box2dTest_Add_VoidBox():
    box = _box(1.0, 2.0, 5.0, 6.0)
    box.Add(Bnd_Box2d())
    xmin, ymin, _, _ = _get(box)
    assert xmin == 1.0
    assert ymin == 2.0


def test_Bnd_Box2dTest_Add_ToVoidBox():
    void_box = Bnd_Box2d()
    void_box.Add(_box(1.0, 2.0, 5.0, 6.0))
    assert _get(void_box) == (1.0, 2.0, 5.0, 6.0)


def test_Bnd_Box2dTest_OpenDirections():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.IsOpenXmin() is False
    assert box.IsOpenXmax() is False
    assert box.IsOpenYmin() is False
    assert box.IsOpenYmax() is False
    box.OpenXmin()
    assert box.IsOpenXmin() is True
    box.OpenYmax()
    assert box.IsOpenYmax() is True
    assert box.IsWhole() is False


def test_Bnd_Box2dTest_IsOut_Point():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.IsOut(gp_Pnt2d(5.0, 5.0)) is False
    assert box.IsOut(gp_Pnt2d(15.0, 5.0)) is True
    assert box.IsOut(gp_Pnt2d(-1.0, 5.0)) is True


def test_Bnd_Box2dTest_IsOut_Box_Overlapping():
    assert _box(0.0, 0.0, 10.0, 10.0).IsOut(_box(5.0, 5.0, 15.0, 15.0)) is False


def test_Bnd_Box2dTest_IsOut_Box_Separated():
    assert _box(0.0, 0.0, 5.0, 5.0).IsOut(_box(10.0, 10.0, 15.0, 15.0)) is True


def test_Bnd_Box2dTest_IsOut_Box_FastPath():
    box1 = _box(0.0, 0.0, 10.0, 10.0)
    assert box1.IsOut(_box(5.0, 5.0, 15.0, 15.0)) is False
    assert box1.IsOut(_box(20.0, 20.0, 30.0, 30.0)) is True


def test_Bnd_Box2dTest_IsOut_Box_FastPath_WithGap():
    box1 = _box(0.0, 0.0, 5.0, 5.0)
    box1.SetGap(1.0)
    assert box1.IsOut(_box(6.0, 0.0, 10.0, 5.0)) is False
    assert box1.IsOut(_box(7.0, 0.0, 10.0, 5.0)) is True


def test_Bnd_Box2dTest_IsOut_VoidBox():
    box = _box(0.0, 0.0, 10.0, 10.0)
    void_box = Bnd_Box2d()
    assert box.IsOut(void_box) is True
    assert void_box.IsOut(box) is True


def test_Bnd_Box2dTest_IsOut_WholeBox():
    box = _box(0.0, 0.0, 10.0, 10.0)
    whole = Bnd_Box2d()
    whole.SetWhole()
    assert box.IsOut(whole) is False
    assert whole.IsOut(box) is False


def test_Bnd_Box2dTest_IsOut_OpenBox():
    box1 = _box(0.0, 0.0, 10.0, 10.0)
    box1.OpenXmin()
    assert box1.IsOut(_box(-100.0, 0.0, -50.0, 10.0)) is False


def test_Bnd_Box2dTest_IsOut_Line():
    box = _box(0.0, 0.0, 10.0, 10.0)
    inside = gp_Lin2d(gp_Pnt2d(5.0, -5.0), gp_Dir2d(0.0, 1.0))
    assert box.IsOut(inside) is False
    outside = gp_Lin2d(gp_Pnt2d(20.0, -5.0), gp_Dir2d(0.0, 1.0))
    assert box.IsOut(outside) is True


def test_Bnd_Box2dTest_IsOut_Segment():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.IsOut(gp_Pnt2d(5.0, -5.0), gp_Pnt2d(5.0, 15.0)) is False
    assert box.IsOut(gp_Pnt2d(20.0, 0.0), gp_Pnt2d(20.0, 10.0)) is True


def test_Bnd_Box2dTest_Transformed():
    box = _box(0.0, 0.0, 10.0, 10.0)
    trsf = gp_Trsf2d()
    trsf.SetTranslation(gp_Pnt2d(0.0, 0.0), gp_Pnt2d(5.0, 5.0))
    assert _get(box.Transformed(trsf)) == (5.0, 5.0, 15.0, 15.0)


def test_Bnd_Box2dTest_SquareExtent():
    assert _box(0.0, 0.0, 3.0, 4.0).SquareExtent() == 25.0


def test_Bnd_Box2dTest_SquareExtent_Void():
    assert Bnd_Box2d().SquareExtent() == 0.0


def test_Bnd_Box2dTest_Add_Direction():
    box = Bnd_Box2d()
    box.Set(gp_Pnt2d(5.0, 5.0))
    box.Add(gp_Dir2d(1.0, 0.0))
    assert box.IsOpenXmax() is True
    assert box.IsOpenXmin() is False


def test_Bnd_Box2dTest_Contains_Point():
    box = _box(0.0, 0.0, 10.0, 10.0)
    assert box.Contains(gp_Pnt2d(5.0, 5.0)) is True
    assert box.Contains(gp_Pnt2d(0.0, 0.0)) is True
    assert box.Contains(gp_Pnt2d(-1.0, 5.0)) is False
    assert box.Contains(gp_Pnt2d(5.0, 11.0)) is False


def test_Bnd_Box2dTest_Intersects_Box():
    box1 = _box(0.0, 0.0, 10.0, 10.0)
    assert box1.Intersects(_box(5.0, 5.0, 15.0, 15.0)) is True
    assert box1.Intersects(_box(20.0, 20.0, 30.0, 30.0)) is False


def test_Bnd_Box2dTest_Distance_Separated():
    d = _box(0.0, 0.0, 1.0, 1.0).Distance(_box(4.0, 0.0, 5.0, 1.0))
    assert abs(d - 3.0) <= 1e-10


def test_Bnd_Box2dTest_Distance_Overlapping():
    assert _box(0.0, 0.0, 10.0, 10.0).Distance(_box(5.0, 5.0, 15.0, 15.0)) == 0.0


def test_Bnd_Box2dTest_Distance_Diagonal():
    d = _box(0.0, 0.0, 1.0, 1.0).Distance(_box(4.0, 4.0, 5.0, 5.0))
    assert abs(d - math.sqrt(18.0)) <= 1e-10


def test_Bnd_Box2dTest_Distance_Void():
    assert Bnd_Box2d().Distance(_box(0.0, 0.0, 1.0, 1.0)) == 0.0


def test_Bnd_Box2dTest_Center():
    center = _box(0.0, 0.0, 10.0, 20.0).Center()
    assert center is not None
    assert center.X() == 5.0
    assert center.Y() == 10.0


def test_Bnd_Box2dTest_Center_VoidNullopt():
    assert Bnd_Box2d().Center() is None
