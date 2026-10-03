# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_Circle_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_Circle
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _unit_circle(radius=1.0, center=gp_Pnt(0.0, 0.0, 0.0)):
    return Geom_Circle(gp_Ax2(center, gp_Dir(0.0, 0.0, 1.0)), radius)


def test_Geom_CircleTest_Constructor():
    c = _unit_circle(5.0)
    assert c is not None
    assert abs(c.Radius() - 5.0) <= TOL


def test_Geom_CircleTest_Center():
    center = gp_Pnt(1.0, 2.0, 3.0)
    c = _unit_circle(5.0, center)
    assert c.Circ().Location().IsEqual(center, TOL)


def test_Geom_CircleTest_D0Evaluation():
    c = _unit_circle()
    p = gp_Pnt()
    c.D0(0.0, p)
    assert abs(p.X() - 1.0) <= TOL and abs(p.Y()) <= TOL and abs(p.Z()) <= TOL
    c.D0(math.pi / 2, p)
    assert abs(p.X()) <= TOL and abs(p.Y() - 1.0) <= TOL and abs(p.Z()) <= TOL
    c.D0(math.pi, p)
    assert abs(p.X() + 1.0) <= TOL and abs(p.Y()) <= TOL
    c.D0(3.0 * math.pi / 2, p)
    assert abs(p.X()) <= TOL and abs(p.Y() + 1.0) <= TOL


def test_Geom_CircleTest_D1Evaluation():
    c = _unit_circle()
    p, v1 = gp_Pnt(), gp_Vec()
    c.D1(0.0, p, v1)
    assert abs(v1.X()) <= TOL and abs(v1.Y() - 1.0) <= TOL and abs(v1.Z()) <= TOL


def test_Geom_CircleTest_D2Evaluation():
    c = _unit_circle()
    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    c.D2(0.0, p, v1, v2)
    assert abs(v2.X() + 1.0) <= TOL and abs(v2.Y()) <= TOL and abs(v2.Z()) <= TOL


def test_Geom_CircleTest_Reverse():
    c = _unit_circle()
    u = math.pi / 4
    assert abs(c.ReversedParameter(u) - (2.0 * math.pi - u)) <= TOL


def test_Geom_CircleTest_Transform():
    c = _unit_circle(5.0)
    t = gp_Trsf()
    t.SetScale(gp_Pnt(0.0, 0.0, 0.0), 2.0)
    c.Transform(t)
    assert abs(c.Radius() - 10.0) <= TOL


def test_Geom_CircleTest_Copy():
    c = _unit_circle(7.0, gp_Pnt(1.0, 2.0, 3.0))
    cp = c.Copy()
    assert cp is not None
    assert isinstance(cp, Geom_Circle)
    assert abs(cp.Radius() - 7.0) <= TOL
    assert cp.Circ().Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), TOL)
