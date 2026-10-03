# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_AxisPlacement_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_AxisPlacement
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def ap(x, y, dx, dy):
    return Geom2d_AxisPlacement(gp_Pnt2d(x, y), gp_Dir2d(dx, dy))


def test_Geom2d_AxisPlacementTest_ConstructFromAx2d():
    a = Geom2d_AxisPlacement(gp_Ax2d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0)))
    near(a.Location().X(), 1.0)
    near(a.Location().Y(), 2.0)
    near(a.Direction().X(), 1.0)
    near(a.Direction().Y(), 0.0)


def test_Geom2d_AxisPlacementTest_ConstructFromPointAndDir():
    a = ap(3.0, 4.0, 0.0, 1.0)
    near(a.Location().X(), 3.0)
    near(a.Direction().Y(), 1.0)


def test_Geom2d_AxisPlacementTest_SetLocation():
    a = ap(0.0, 0.0, 1.0, 0.0)
    a.SetLocation(gp_Pnt2d(5.0, 6.0))
    near(a.Location().X(), 5.0)
    near(a.Location().Y(), 6.0)


def test_Geom2d_AxisPlacementTest_SetDirection():
    a = ap(0.0, 0.0, 1.0, 0.0)
    a.SetDirection(gp_Dir2d(0.0, 1.0))
    near(a.Direction().X(), 0.0)
    near(a.Direction().Y(), 1.0)


def test_Geom2d_AxisPlacementTest_SetAxis():
    a = ap(0.0, 0.0, 1.0, 0.0)
    a.SetAxis(gp_Ax2d(gp_Pnt2d(10.0, 20.0), gp_Dir2d(0.0, 1.0)))
    near(a.Location().X(), 10.0)
    near(a.Direction().Y(), 1.0)


def test_Geom2d_AxisPlacementTest_Ax2d():
    ax = ap(1.0, 2.0, 1.0, 0.0).Ax2d()
    near(ax.Location().X(), 1.0)
    near(ax.Direction().X(), 1.0)


def test_Geom2d_AxisPlacementTest_Angle_Perpendicular():
    near(ap(0, 0, 1, 0).Angle(ap(0, 0, 0, 1)), math.pi / 2.0)


def test_Geom2d_AxisPlacementTest_Angle_Parallel():
    near(ap(0, 0, 1, 0).Angle(ap(5, 5, 1, 0)), 0.0)


def test_Geom2d_AxisPlacementTest_Angle_Opposite():
    near(abs(ap(0, 0, 1, 0).Angle(ap(0, 0, -1, 0))), math.pi)


def test_Geom2d_AxisPlacementTest_Reverse():
    a = ap(0, 0, 1, 0)
    a.Reverse()
    near(a.Direction().X(), -1.0)
    near(a.Direction().Y(), 0.0)
    near(a.Location().X(), 0.0)


def test_Geom2d_AxisPlacementTest_Reversed():
    a = ap(0, 0, 1, 0)
    r = a.Reversed()
    near(r.Direction().X(), -1.0)
    near(a.Direction().X(), 1.0)


def test_Geom2d_AxisPlacementTest_Transform_Translation():
    a = ap(1, 2, 1, 0)
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10.0, 20.0))
    a.Transform(t)
    near(a.Location().X(), 11.0)
    near(a.Location().Y(), 22.0)
    near(a.Direction().X(), 1.0)


def test_Geom2d_AxisPlacementTest_Transform_Rotation():
    a = ap(1, 0, 1, 0)
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    a.Transform(t)
    near(a.Location().X(), 0.0)
    near(a.Location().Y(), 1.0)
    near(a.Direction().X(), 0.0)
    near(a.Direction().Y(), 1.0)


def test_Geom2d_AxisPlacementTest_Copy():
    a = ap(1, 2, 0, 1)
    c = a.Copy()
    assert isinstance(c, Geom2d_AxisPlacement)
    near(c.Location().X(), 1.0)
    near(c.Direction().Y(), 1.0)
    c.SetLocation(gp_Pnt2d(99.0, 99.0))
    near(a.Location().X(), 1.0)
