# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Lin_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.gp import gp_Ax1, gp_Dir, gp_Lin, gp_Lin2d, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def near(a, b, t=CONF):
    return abs(a - b) <= t


def test_gp_LinTest_ConstructorFromAx1():
    lin = gp_Lin(gp_Ax1(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(1.0, 0.0, 0.0)))
    assert lin.Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), CONF)
    assert lin.Direction().IsEqual(gp_Dir(1.0, 0.0, 0.0), ANG)


def test_gp_LinTest_ConstructorFromPointAndDir():
    lin = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    assert lin.Location().IsEqual(gp_Pnt(0.0, 0.0, 0.0), CONF)
    assert lin.Direction().IsEqual(gp_Dir(0.0, 0.0, 1.0), ANG)


def test_gp_LinTest_DistanceToPoint():
    lin = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert near(lin.Distance(gp_Pnt(5.0, 3.0, 4.0)), 5.0)


def test_gp_LinTest_DistanceToLine_Parallel():
    l1 = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    l2 = gp_Lin(gp_Pnt(0.0, 3.0, 4.0), gp_Dir(1.0, 0.0, 0.0))
    assert near(l1.Distance(l2), 5.0)


def test_gp_LinTest_DistanceToLine_Intersecting():
    l1 = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    l2 = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
    assert near(l1.Distance(l2), 0.0)


def test_gp_LinTest_Contains():
    lin = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert lin.Contains(gp_Pnt(5.0, 0.0, 0.0), CONF)
    assert not lin.Contains(gp_Pnt(5.0, 1.0, 0.0), CONF)


def test_gp_LinTest_Angle():
    l1 = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    l2 = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
    assert near(l1.Angle(l2), math.pi / 2, ANG)


def test_gp_LinTest_Translate():
    lin = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    assert near(lin.Translated(gp_Vec(0.0, 5.0, 0.0)).Location().Y(), 5.0)


def test_gp_LinTest_Rotate():
    lin = gp_Lin(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    r = lin.Rotated(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2)
    assert near(r.Location().X(), 0.0) and near(r.Location().Y(), 1.0)
    assert r.Direction().IsEqual(gp_Dir(0.0, 1.0, 0.0), ANG)


def test_gp_LinTest_Mirror():
    lin = gp_Lin(gp_Pnt(1.0, 1.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    m = lin.Mirrored(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    assert near(m.Location().Y(), -1.0)


def test_gp_LinTest_Transform():
    lin = gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0.0, 0.0, 10.0))
    assert near(lin.Transformed(t).Location().Z(), 10.0)


def test_gp_Lin2dTest_ConstructFromEquation_ZeroDirection_ThrowsException():
    with pytest.raises(Standard_ConstructionError):
        gp_Lin2d(0.0, 0.0, 1.0)


def test_gp_Lin2dTest_ConstructFromEquation_ValidCoefficients_CorrectOrigin():
    o = gp_Lin2d(1e-20, -1.0, 2.0).Location()
    assert abs(o.X() - -1.9999999999999999e-20) <= 1e-25
    assert abs(o.Y() - 2.0) <= 0.001
