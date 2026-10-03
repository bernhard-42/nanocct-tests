# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Circ_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Ax1, gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _circ(r, center=(0.0, 0.0, 0.0)):
    return gp_Circ(gp_Ax2(gp_Pnt(*center), gp_Dir(0.0, 0.0, 1.0)), r)


def test_gp_CircTest_Constructor():
    assert abs(_circ(5.0).Radius() - 5.0) <= TOL


def test_gp_CircTest_Area():
    assert abs(_circ(1.0).Area() - math.pi) <= TOL


def test_gp_CircTest_Length():
    assert abs(_circ(1.0).Length() - 2.0 * math.pi) <= TOL


def test_gp_CircTest_Center():
    c = gp_Pnt(1.0, 2.0, 3.0)
    circ = gp_Circ(gp_Ax2(c, gp_Dir(0.0, 0.0, 1.0)), 5.0)
    assert circ.Location().IsEqual(c, TOL)


def test_gp_CircTest_Translate():
    t = _circ(5.0).Translated(gp_Vec(10.0, 20.0, 30.0))
    assert abs(t.Location().X() - 10.0) <= TOL
    assert abs(t.Location().Y() - 20.0) <= TOL
    assert abs(t.Location().Z() - 30.0) <= TOL
    assert abs(t.Radius() - 5.0) <= TOL


def test_gp_CircTest_Rotate():
    circ = _circ(2.0, (1.0, 0.0, 0.0))
    r = circ.Rotated(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2)
    assert abs(r.Location().X() - 0.0) <= TOL
    assert abs(r.Location().Y() - 1.0) <= TOL
    assert abs(r.Radius() - 2.0) <= TOL


def test_gp_CircTest_Mirror():
    m = _circ(5.0, (1.0, 2.0, 3.0)).Mirrored(gp_Pnt(0.0, 0.0, 0.0))
    assert abs(m.Location().X() + 1.0) <= TOL
    assert abs(m.Location().Y() + 2.0) <= TOL
    assert abs(m.Location().Z() + 3.0) <= TOL


def test_gp_CircTest_Transform():
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(0.0, 0.0, 0.0), 2.0)
    assert abs(_circ(3.0).Transformed(trsf).Radius() - 6.0) <= TOL
