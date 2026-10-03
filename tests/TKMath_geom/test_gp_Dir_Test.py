# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Dir_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec, gp_XYZ
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def near(a, b, t=CONF):
    return abs(a - b) <= t


def test_gp_DirTest_CoordinateConstructor():
    d = gp_Dir(0.0, 0.0, 1.0)
    assert near(d.X(), 0.0) and near(d.Y(), 0.0) and near(d.Z(), 1.0)


def test_gp_DirTest_XYZConstructor():
    d = gp_Dir(gp_XYZ(0.0, 3.0, 4.0))
    assert near(d.X(), 0.0) and near(d.Y(), 0.6) and near(d.Z(), 0.8)


def test_gp_DirTest_VecConstructor():
    d = gp_Dir(gp_Vec(3.0, 0.0, 0.0))
    assert near(d.X(), 1.0) and near(d.Y(), 0.0) and near(d.Z(), 0.0)


def test_gp_DirTest_PredefinedDirections():
    assert gp_Dir(1.0, 0.0, 0.0).IsEqual(gp_Dir(gp_Dir.D.X), ANG)
    assert gp_Dir(0.0, 1.0, 0.0).IsEqual(gp_Dir(gp_Dir.D.Y), ANG)
    assert gp_Dir(0.0, 0.0, 1.0).IsEqual(gp_Dir(gp_Dir.D.Z), ANG)


def test_gp_DirTest_Angle():
    assert near(gp_Dir(1.0, 0.0, 0.0).Angle(gp_Dir(0.0, 1.0, 0.0)), math.pi / 2, ANG)


def test_gp_DirTest_AngleWithRef():
    d1, d2 = gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)
    assert near(d1.AngleWithRef(d2, gp_Dir(0.0, 0.0, 1.0)), math.pi / 2, ANG)
    assert near(d1.AngleWithRef(d2, gp_Dir(0.0, 0.0, -1.0)), -math.pi / 2, ANG)


def test_gp_DirTest_IsEqual():
    assert gp_Dir(1.0, 0.0, 0.0).IsEqual(gp_Dir(1.0, 0.0, 0.0), ANG)


def test_gp_DirTest_IsNormal():
    assert gp_Dir(1.0, 0.0, 0.0).IsNormal(gp_Dir(0.0, 1.0, 0.0), ANG)


def test_gp_DirTest_IsOpposite():
    assert gp_Dir(1.0, 0.0, 0.0).IsOpposite(gp_Dir(-1.0, 0.0, 0.0), ANG)


def test_gp_DirTest_IsParallel():
    assert gp_Dir(1.0, 0.0, 0.0).IsParallel(gp_Dir(-1.0, 0.0, 0.0), ANG)


def test_gp_DirTest_Cross():
    c = gp_Dir(1.0, 0.0, 0.0).Crossed(gp_Dir(0.0, 1.0, 0.0))
    assert near(c.X(), 0.0) and near(c.Y(), 0.0) and near(c.Z(), 1.0)


def test_gp_DirTest_CrossCross():
    cc = gp_Dir(1.0, 0.0, 0.0).CrossCrossed(gp_Dir(1.0, 1.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    assert near(math.sqrt(cc.X() ** 2 + cc.Y() ** 2 + cc.Z() ** 2), 1.0)


def test_gp_DirTest_Dot():
    d1 = gp_Dir(1.0, 0.0, 0.0)
    assert near(d1.Dot(gp_Dir(0.0, 1.0, 0.0)), 0.0)
    assert near(d1.Dot(gp_Dir(1.0, 0.0, 0.0)), 1.0)


def test_gp_DirTest_Mirror_Point():
    m = gp_Dir(1.0, 0.0, 0.0).Mirrored(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)))
    assert near(m.X(), -1.0) and near(m.Y(), 0.0)


def test_gp_DirTest_Rotate():
    r = gp_Dir(1.0, 0.0, 0.0).Rotated(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2)
    assert near(r.X(), 0.0) and near(r.Y(), 1.0) and near(r.Z(), 0.0)


def test_gp_DirTest_Transform():
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi)
    r = gp_Dir(1.0, 0.0, 0.0).Transformed(t)
    assert near(r.X(), -1.0) and near(r.Y(), 0.0)


def test_gp_DirTest_ZeroMagnitudeInput_ThrowsException():
    with pytest.raises(Standard_ConstructionError):
        gp_Dir(0.0, 0.0, 0.0)


def test_gp_DirTest_OCC22558_MirrorThroughAx2_CorrectResult():
    d = gp_Dir(1.0, 1.0, 1.0)
    d.Mirror(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    e = 1.0 / math.sqrt(3.0)
    assert near(d.X(), -e) and near(d.Y(), e) and near(d.Z(), e)
