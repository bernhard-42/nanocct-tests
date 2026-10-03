# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Dir2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d, gp_XY
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def near(a, b, t=CONF):
    return abs(a - b) <= t


def test_gp_Dir2dTest_CoordinateConstructor():
    d = gp_Dir2d(1.0, 0.0)
    assert near(d.X(), 1.0) and near(d.Y(), 0.0)


def test_gp_Dir2dTest_XYConstructor():
    d = gp_Dir2d(gp_XY(0.0, 3.0))
    assert near(d.X(), 0.0) and near(d.Y(), 1.0)


def test_gp_Dir2dTest_Vec2dConstructor():
    d = gp_Dir2d(gp_Vec2d(3.0, 0.0))
    assert near(d.X(), 1.0) and near(d.Y(), 0.0)


def test_gp_Dir2dTest_Angle():
    assert near(gp_Dir2d(1.0, 0.0).Angle(gp_Dir2d(0.0, 1.0)), math.pi / 2, ANG)


def test_gp_Dir2dTest_IsEqual():
    assert gp_Dir2d(1.0, 0.0).IsEqual(gp_Dir2d(1.0, 0.0), ANG)


def test_gp_Dir2dTest_IsNormal():
    assert gp_Dir2d(1.0, 0.0).IsNormal(gp_Dir2d(0.0, 1.0), ANG)


def test_gp_Dir2dTest_IsOpposite():
    assert gp_Dir2d(1.0, 0.0).IsOpposite(gp_Dir2d(-1.0, 0.0), ANG)


def test_gp_Dir2dTest_IsParallel():
    assert gp_Dir2d(1.0, 0.0).IsParallel(gp_Dir2d(-1.0, 0.0), ANG)


def test_gp_Dir2dTest_Dot():
    d1 = gp_Dir2d(1.0, 0.0)
    assert near(d1.Dot(gp_Dir2d(0.0, 1.0)), 0.0)
    assert near(d1.Dot(gp_Dir2d(1.0, 0.0)), 1.0)


def test_gp_Dir2dTest_Crossed():
    assert near(gp_Dir2d(1.0, 0.0).Crossed(gp_Dir2d(0.0, 1.0)), 1.0)


def test_gp_Dir2dTest_Rotate():
    r = gp_Dir2d(1.0, 0.0).Rotated(math.pi / 2)
    assert near(r.X(), 0.0) and near(r.Y(), 1.0)


def test_gp_Dir2dTest_Mirror():
    m = gp_Dir2d(1.0, 0.0).Mirrored(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(0.0, 1.0)))
    assert near(m.X(), -1.0) and near(m.Y(), 0.0)


def test_gp_Dir2dTest_Transform():
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi)
    r = gp_Dir2d(1.0, 0.0).Transformed(t)
    assert near(r.X(), -1.0) and near(r.Y(), 0.0)


def test_gp_Dir2dTest_ZeroMagnitudeThrows():
    with pytest.raises(Standard_ConstructionError):
        gp_Dir2d(0.0, 0.0)
