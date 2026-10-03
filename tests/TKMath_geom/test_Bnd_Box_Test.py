# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_Box_Test.cxx (LGPL-2.1 with the OCCT exception)
import io
import math

import pytest

from nanocct.Bnd import Bnd_Box
from nanocct.gp import gp_Ax1, gp_Dir, gp_Lin, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Standard import Standard_ConstructionError


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _get(box):
    return box.Get__float__float__float__float__float__float()


def test_Bnd_BoxTest_DefaultConstructor():
    box = Bnd_Box()
    assert box.IsVoid() is True
    assert box.IsWhole() is False
    assert box.GetGap() == 0.0


def test_Bnd_BoxTest_PointConstructor():
    box = Bnd_Box(gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0))
    assert box.IsVoid() is False
    assert box.IsWhole() is False
    assert _get(box) == (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)


def test_Bnd_BoxTest_SetWithPoint():
    box = Bnd_Box()
    box.Set(gp_Pnt(1.5, 2.5, 3.5))
    assert box.IsVoid() is False
    assert _get(box) == (1.5, 2.5, 3.5, 1.5, 2.5, 3.5)


def test_Bnd_BoxTest_SetWithPointAndDirection():
    box = Bnd_Box()
    box.Set(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(gp_Dir.D.X))
    assert box.IsVoid() is False
    assert box.IsOpenXmax() is True
    assert box.IsOpenXmin() is False


def test_Bnd_BoxTest_UpdateWithBounds():
    box = Bnd_Box()
    box.Update(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    assert box.IsVoid() is False
    assert _get(box) == (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)


def test_Bnd_BoxTest_UpdateWithPoint():
    box = Bnd_Box()
    box.Update(1.0, 2.0, 3.0)
    xmin, ymin, zmin, xmax, ymax, zmax = _get(box)
    assert xmin == 1.0
    assert xmax == 1.0

    box.Update(0.5, 2.5, 3.5)
    xmin, ymin, zmin, xmax, ymax, zmax = _get(box)
    assert xmin == 0.5
    assert xmax == 1.0
    assert ymin == 2.0
    assert ymax == 2.5


def test_Bnd_BoxTest_UpdateExpansion():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.Update(-1.0, -1.0, -1.0, 2.0, 2.0, 2.0)
    assert _get(box) == (-1.0, -1.0, -1.0, 2.0, 2.0, 2.0)


def test_Bnd_BoxTest_GapOperations():
    box = Bnd_Box()
    assert box.GetGap() == 0.0
    box.SetGap(0.5)
    assert box.GetGap() == 0.5
    box.Enlarge(0.3)
    assert box.GetGap() == 0.5
    box.Enlarge(0.8)
    assert box.GetGap() == 0.8
    box.Enlarge(-1.0)
    assert box.GetGap() == 1.0


def test_Bnd_BoxTest_CornerMethods():
    box = Bnd_Box()
    box.Update(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    box.SetGap(0.1)
    cmin = box.CornerMin()
    cmax = box.CornerMax()
    assert cmin.X() == _eq(0.9)
    assert cmin.Y() == _eq(1.9)
    assert cmin.Z() == _eq(2.9)
    assert cmax.X() == _eq(4.1)
    assert cmax.Y() == _eq(5.1)
    assert cmax.Z() == _eq(6.1)


def test_Bnd_BoxTest_CornerMethodsVoidBox():
    box = Bnd_Box()
    with pytest.raises(Standard_ConstructionError):
        box.CornerMin()
    with pytest.raises(Standard_ConstructionError):
        box.CornerMax()


def test_Bnd_BoxTest_CornerMethodsOpenBox():
    box = Bnd_Box()
    box.Update(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    box.OpenXmax()
    box.OpenYmin()
    assert box.CornerMin().Y() == -1e100
    assert box.CornerMax().X() == 1e100


def test_Bnd_BoxTest_ThinnessMethods():
    box = Bnd_Box()
    assert box.IsXThin(1.0) is True
    assert box.IsYThin(1.0) is True
    assert box.IsZThin(1.0) is True
    assert box.IsThin(1.0) is True

    box.Update(1.0, 0.0, 0.0, 1.01, 2.0, 2.0)
    assert box.IsXThin(0.1) is True
    assert box.IsYThin(0.1) is False
    assert box.IsZThin(0.1) is False
    assert box.IsThin(0.1) is False

    thin = Bnd_Box()
    thin.Update(0.0, 0.0, 0.0, 0.01, 0.01, 0.01)
    assert thin.IsXThin(0.1) is True
    assert thin.IsYThin(0.1) is True
    assert thin.IsZThin(0.1) is True
    assert thin.IsThin(0.1) is True


def test_Bnd_BoxTest_ThinnessWithOpenBox():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.OpenXmin()
    assert box.IsXThin(0.1) is False
    box.SetWhole()
    assert box.IsXThin(0.1) is False
    assert box.IsThin(0.1) is False


def test_Bnd_BoxTest_TransformationIdentity():
    box = Bnd_Box()
    box.Update(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    box.SetGap(0.1)
    transformed = box.Transformed(gp_Trsf())
    for a, b in zip(_get(box), _get(transformed)):
        assert a == _eq(b)
    assert box.GetGap() == transformed.GetGap()


def test_Bnd_BoxTest_TransformationTranslation():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(2.0, 3.0, 4.0))
    transformed = box.Transformed(trsf)
    assert _get(transformed) == (2.0, 3.0, 4.0, 3.0, 4.0, 5.0)


def test_Bnd_BoxTest_TransformationVoidBox():
    rot = gp_Trsf()
    rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), math.pi / 4)
    assert Bnd_Box().Transformed(rot).IsVoid() is True


def test_Bnd_BoxTest_AddBox():
    box1 = Bnd_Box()
    box1.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box1.SetGap(0.1)
    box2 = Bnd_Box()
    box2.Update(0.5, 0.5, 0.5, 2.0, 2.0, 2.0)
    box2.SetGap(0.2)
    box1.Add(box2)
    for got, exp in zip(_get(box1), (-0.2, -0.2, -0.2, 2.2, 2.2, 2.2)):
        assert got == _eq(exp)
    assert box1.GetGap() == 0.2


def test_Bnd_BoxTest_AddVoidBox():
    box = Bnd_Box()
    box.Update(1.0, 1.0, 1.0, 2.0, 2.0, 2.0)
    box.Add(Bnd_Box())
    xmin, _, _, xmax, _, _ = _get(box)
    assert xmin == 1.0
    assert xmax == 2.0


def test_Bnd_BoxTest_AddToVoidBox():
    void_box = Bnd_Box()
    box = Bnd_Box()
    box.Update(1.0, 1.0, 1.0, 2.0, 2.0, 2.0)
    void_box.Add(box)
    assert void_box.IsVoid() is False
    xmin, _, _, xmax, _, _ = _get(void_box)
    assert xmin == 1.0
    assert xmax == 2.0


def test_Bnd_BoxTest_AddPoint():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.Add(gp_Pnt(2.0, -1.0, 0.5))
    assert _get(box) == (0.0, -1.0, 0.0, 2.0, 1.0, 1.0)


def test_Bnd_BoxTest_AddDirection():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.Add(gp_Dir(gp_Dir.D.X))
    assert box.IsOpenXmax() is True
    assert box.IsOpenXmin() is False
    assert box.IsOpenYmax() is False
    assert box.IsOpenYmin() is False


def test_Bnd_BoxTest_AddPointWithDirection():
    box = Bnd_Box()
    box.Add(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(gp_Dir.D.NX))
    assert box.IsVoid() is False
    assert box.IsOpenXmin() is True
    assert box.IsOpenXmax() is False


def test_Bnd_BoxTest_IsOutPoint():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
    assert box.IsOut(gp_Pnt(1.0, 1.0, 1.0)) is False
    assert box.IsOut(gp_Pnt(3.0, 1.0, 1.0)) is True
    assert box.IsOut(gp_Pnt(2.0, 2.0, 2.0)) is False


def test_Bnd_BoxTest_IsOutPointWithGap():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
    box.SetGap(0.1)
    assert box.IsOut(gp_Pnt(2.05, 1.0, 1.0)) is False
    assert box.IsOut(gp_Pnt(2.15, 1.0, 1.0)) is True


def test_Bnd_BoxTest_IsOutVoidBox():
    assert Bnd_Box().IsOut(gp_Pnt(1.0, 2.0, 3.0)) is True


def test_Bnd_BoxTest_IsOutWholeBox():
    box = Bnd_Box()
    box.SetWhole()
    assert box.IsOut(gp_Pnt(1000.0, 2000.0, 3000.0)) is False


def test_Bnd_BoxTest_IsOutBox():
    box1 = Bnd_Box()
    box1.Update(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
    overlapping = Bnd_Box()
    overlapping.Update(1.0, 1.0, 1.0, 3.0, 3.0, 3.0)
    separate = Bnd_Box()
    separate.Update(3.0, 3.0, 3.0, 4.0, 4.0, 4.0)
    touching = Bnd_Box()
    touching.Update(2.0, 2.0, 2.0, 3.0, 3.0, 3.0)
    assert box1.IsOut(overlapping) is False
    assert box1.IsOut(separate) is True
    assert box1.IsOut(touching) is False


def test_Bnd_BoxTest_IsOutPlane():
    box = Bnd_Box()
    box.Update(-1.0, -1.0, -1.0, 1.0, 1.0, 1.0)
    intersecting = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.X))
    separate = gp_Pln(gp_Pnt(2, 0, 0), gp_Dir(gp_Dir.D.X))
    assert box.IsOut(intersecting) is False
    assert box.IsOut(separate) is True


def test_Bnd_BoxTest_IsOutLine():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
    intersecting = gp_Lin(gp_Pnt(-1, 1, 1), gp_Dir(gp_Dir.D.X))
    separate = gp_Lin(gp_Pnt(-1, 3, 1), gp_Dir(gp_Dir.D.X))
    assert box.IsOut(intersecting) is False
    assert box.IsOut(separate) is True


def test_Bnd_BoxTest_Distance():
    box1 = Bnd_Box()
    box1.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box2 = Bnd_Box()
    box2.Update(2.0, 0.0, 0.0, 3.0, 1.0, 1.0)
    assert box1.Distance(box2) == _eq(1.0)
    overlapping = Bnd_Box()
    overlapping.Update(0.5, 0.5, 0.5, 1.5, 1.5, 1.5)
    assert box1.Distance(overlapping) == 0.0


def test_Bnd_BoxTest_OpenCloseMethods():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    assert box.IsOpen() is False
    box.OpenXmin()
    assert box.IsOpenXmin() is True
    assert box.IsOpen() is True
    box.OpenXmax()
    box.OpenYmin()
    box.OpenYmax()
    box.OpenZmin()
    box.OpenZmax()
    assert box.IsOpenXmax() is True
    assert box.IsOpenYmin() is True
    assert box.IsOpenYmax() is True
    assert box.IsOpenZmin() is True
    assert box.IsOpenZmax() is True
    assert box.IsWhole() is True


def test_Bnd_BoxTest_VoidWholeStates():
    box = Bnd_Box()
    assert box.IsVoid() is True
    assert box.IsWhole() is False
    box.SetWhole()
    assert box.IsVoid() is False
    assert box.IsWhole() is True
    box.SetVoid()
    assert box.IsVoid() is True
    assert box.IsWhole() is False
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    assert box.IsVoid() is False
    assert box.IsWhole() is False
    assert box.HasFinitePart() is True


def test_Bnd_BoxTest_EdgeCases():
    large = 1e10
    box = Bnd_Box()
    box.Update(-large, -large, -large, large, large, large)
    assert box.IsVoid() is False
    small = Bnd_Box()
    small.Update(0.0, 0.0, 0.0, 1e-10, 1e-10, 1e-10)
    assert small.IsVoid() is False
    assert small.IsXThin(1e-9) is True


def test_Bnd_BoxTest_TransformationWithOpenBox():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.OpenXmax()
    rot = gp_Trsf()
    rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), math.pi / 2)
    transformed = box.Transformed(rot)
    assert transformed.IsOpen() is True
    assert transformed.IsVoid() is False


def test_Bnd_BoxTest_SquareExtent():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 2.0, 3.0, 4.0)
    assert box.SquareExtent() == _eq(29.0)


def test_Bnd_BoxTest_SetVoidAndWholeTransitions():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    assert box.IsVoid() is False
    box.SetVoid()
    assert box.IsVoid() is True
    box.SetWhole()
    assert box.IsWhole() is True
    assert box.IsVoid() is False


def test_Bnd_BoxTest_DirectOpenOperations():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box.OpenXmin()
    assert box.IsOpenXmin() is True
    box.OpenXmax()
    assert box.IsOpenXmax() is True
    box.OpenYmin()
    assert box.IsOpenYmin() is True
    box.OpenYmax()
    assert box.IsOpenYmax() is True
    box.OpenZmin()
    assert box.IsOpenZmin() is True
    box.OpenZmax()
    assert box.IsOpenZmax() is True


def test_Bnd_BoxTest_IsOutWithTransformation():
    box1 = Bnd_Box()
    box1.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box2 = Bnd_Box()
    box2.Update(2.0, 0.0, 0.0, 3.0, 1.0, 1.0)
    trsf = gp_Trsf()
    assert box1.IsOut(box2, trsf) is True
    trsf.SetTranslation(gp_Vec(-1.5, 0.0, 0.0))
    assert box1.IsOut(box2, trsf) is False


def test_Bnd_BoxTest_IsOutWithTwoTransformations():
    box1 = Bnd_Box()
    box1.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    box2 = Bnd_Box()
    box2.Update(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    t1 = gp_Trsf()
    t2 = gp_Trsf()
    t1.SetTranslation(gp_Vec(0.0, 0.0, 0.0))
    t2.SetTranslation(gp_Vec(2.0, 0.0, 0.0))
    assert box1.IsOut(t1, box2, t2) is True


def test_Bnd_BoxTest_IsOutLineSegment():
    box = Bnd_Box()
    box.Update(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
    d = gp_Dir(gp_Dir.D.X)
    assert box.IsOut(gp_Pnt(-1.0, 1.0, 1.0), gp_Pnt(3.0, 1.0, 1.0), d) is False
    assert box.IsOut(gp_Pnt(-1.0, 3.0, 1.0), gp_Pnt(3.0, 3.0, 1.0), d) is True


def test_Bnd_BoxTest_UpdateExpandsCorrectly():
    box = Bnd_Box()
    box.Update(1.0, 1.0, 1.0)
    xmin, ymin, zmin, xmax, ymax, zmax = _get(box)
    assert xmin == 1.0
    assert xmax == 1.0
    box.Update(-0.5, 2.5, 0.5)
    xmin, ymin, zmin, xmax, ymax, zmax = _get(box)
    assert xmin == -0.5
    assert xmax == 1.0
    assert ymin == 1.0
    assert ymax == 2.5


def test_Bnd_BoxTest_DumpJsonAndInitFromJson():
    box = Bnd_Box(gp_Pnt(0, 0, 0), gp_Pnt(10, 5, 3))
    box.SetGap(0.1)
    json_str = box.DumpJson()

    restored = Bnd_Box()
    ok, _pos = restored.InitFromJson(io.StringIO(json_str), 1)
    assert ok is True
    for a, b in zip(_get(box), _get(restored)):
        assert a == _eq(b)
    assert box.GetGap() == restored.GetGap()


def test_Bnd_BoxTest_OCC16485_CumulativeEnlargeTolerance():
    tol = 1e-3
    nb_step = 1000
    box = Bnd_Box()
    for i in range(nb_step + 1):
        b = Bnd_Box()
        b.Add(gp_Pnt(i, 0.0, 0.0))
        b.Enlarge(tol)
        b.Add(box)
        box = b
    xmin, _, _, xmax, _, _ = _get(box)
    assert abs(-tol - xmin) <= 1e-10
    assert abs(nb_step + tol - xmax) <= 1e-10


def test_Bnd_BoxTest_Contains_Point():
    box = Bnd_Box(gp_Pnt(0, 0, 0), gp_Pnt(10, 10, 10))
    assert box.Contains(gp_Pnt(5, 5, 5)) is True
    assert box.Contains(gp_Pnt(0, 0, 0)) is True
    assert box.Contains(gp_Pnt(-1, 5, 5)) is False
    assert box.Contains(gp_Pnt(5, 5, 11)) is False


def test_Bnd_BoxTest_Intersects_Box():
    box1 = Bnd_Box(gp_Pnt(0, 0, 0), gp_Pnt(10, 10, 10))
    box2 = Bnd_Box(gp_Pnt(5, 5, 5), gp_Pnt(15, 15, 15))
    box3 = Bnd_Box(gp_Pnt(20, 20, 20), gp_Pnt(30, 30, 30))
    assert box1.Intersects(box2) is True
    assert box1.Intersects(box3) is False


def test_Bnd_BoxTest_Center():
    box = Bnd_Box(gp_Pnt(0, 0, 0), gp_Pnt(10, 20, 30))
    center = box.Center()
    assert center is not None
    assert center.X() == 5.0
    assert center.Y() == 10.0
    assert center.Z() == 15.0


def test_Bnd_BoxTest_Center_VoidNullopt():
    assert Bnd_Box().Center() is None
