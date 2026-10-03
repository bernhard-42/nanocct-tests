# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Pln_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def near(a, b, t=CONF):
    return abs(a - b) <= t


def _pln(loc=(0.0, 0.0, 0.0)):
    return gp_Pln(gp_Pnt(*loc), gp_Dir(0.0, 0.0, 1.0))


def test_gp_PlnTest_ConstructorFromAx3():
    pln = gp_Pln(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    assert pln.Location().IsEqual(gp_Pnt(0.0, 0.0, 0.0), CONF)
    assert pln.Axis().Direction().IsEqual(gp_Dir(0.0, 0.0, 1.0), ANG)


def test_gp_PlnTest_ConstructorFromPointAndDir():
    loc, norm = gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0)
    pln = gp_Pln(loc, norm)
    assert pln.Location().IsEqual(loc, CONF)
    assert pln.Axis().Direction().IsEqual(norm, ANG)


def test_gp_PlnTest_ConstructorFromCoefficients():
    a, b, c, d = gp_Pln(0.0, 0.0, 1.0, -5.0).Coefficients()
    assert near(a, 0.0) and near(b, 0.0) and near(c, 1.0) and near(d, -5.0)


def test_gp_PlnTest_DistanceToPoint():
    assert near(_pln().Distance(gp_Pnt(3.0, 4.0, 5.0)), 5.0)


def test_gp_PlnTest_Contains():
    pln = _pln()
    assert pln.Contains(gp_Pnt(3.0, 4.0, 0.0), CONF)
    assert not pln.Contains(gp_Pnt(3.0, 4.0, 1.0), CONF)


def test_gp_PlnTest_Coefficients():
    a, b, c, d = _pln().Coefficients()
    assert near(a, 0.0) and near(b, 0.0) and near(c, 1.0) and near(d, 0.0)


def test_gp_PlnTest_Mirror():
    m = _pln((0.0, 0.0, 5.0)).Mirrored(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    assert near(m.Location().Z(), -5.0)


def test_gp_PlnTest_Rotate():
    r = _pln((1.0, 0.0, 0.0)).Rotated(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2)
    assert near(r.Location().X(), 0.0) and near(r.Location().Y(), 1.0)


def test_gp_PlnTest_Scale():
    assert near(_pln((1.0, 0.0, 0.0)).Scaled(gp_Pnt(0.0, 0.0, 0.0), 3.0).Location().X(), 3.0)


def test_gp_PlnTest_Translate():
    t = _pln().Translated(gp_Vec(1.0, 2.0, 3.0))
    assert near(t.Location().X(), 1.0) and near(t.Location().Y(), 2.0) and near(t.Location().Z(), 3.0)


def test_gp_PlnTest_Transform():
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0.0, 0.0, 10.0))
    assert near(_pln().Transformed(t).Location().Z(), 10.0)
