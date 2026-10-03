# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_CartesianPoint_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_CartesianPoint
from nanocct.gp import gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def test_Geom2d_CartesianPointTest_ConstructFromCoords():
    p = Geom2d_CartesianPoint(3.0, 4.0)
    near(p.X(), 3.0)
    near(p.Y(), 4.0)


def test_Geom2d_CartesianPointTest_ConstructFromPnt2d():
    p = Geom2d_CartesianPoint(gp_Pnt2d(5.0, 6.0))
    near(p.X(), 5.0)
    near(p.Y(), 6.0)


def test_Geom2d_CartesianPointTest_SetCoord():
    p = Geom2d_CartesianPoint(0.0, 0.0)
    p.SetCoord(7.0, 8.0)
    near(p.X(), 7.0)
    near(p.Y(), 8.0)


def test_Geom2d_CartesianPointTest_SetPnt2d():
    p = Geom2d_CartesianPoint(0.0, 0.0)
    p.SetPnt2d(gp_Pnt2d(1.0, 2.0))
    near(p.X(), 1.0)
    near(p.Y(), 2.0)


def test_Geom2d_CartesianPointTest_SetX_SetY():
    p = Geom2d_CartesianPoint(0.0, 0.0)
    p.SetX(10.0)
    p.SetY(20.0)
    near(p.X(), 10.0)
    near(p.Y(), 20.0)


def test_Geom2d_CartesianPointTest_Coord():
    x, y = Geom2d_CartesianPoint(3.0, 4.0).Coord()
    near(x, 3.0)
    near(y, 4.0)


def test_Geom2d_CartesianPointTest_Pnt2d():
    g = Geom2d_CartesianPoint(3.0, 4.0).Pnt2d()
    near(g.X(), 3.0)
    near(g.Y(), 4.0)


def test_Geom2d_CartesianPointTest_Distance():
    near(Geom2d_CartesianPoint(0.0, 0.0).Distance(Geom2d_CartesianPoint(3.0, 4.0)), 5.0)


def test_Geom2d_CartesianPointTest_SquareDistance():
    near(Geom2d_CartesianPoint(0.0, 0.0).SquareDistance(Geom2d_CartesianPoint(3.0, 4.0)), 25.0)


def test_Geom2d_CartesianPointTest_Distance_SamePoint():
    p = Geom2d_CartesianPoint(5.0, 5.0)
    near(p.Distance(p), 0.0)


def test_Geom2d_CartesianPointTest_Transform_Translation():
    p = Geom2d_CartesianPoint(1.0, 2.0)
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(3.0, 4.0))
    p.Transform(t)
    near(p.X(), 4.0)
    near(p.Y(), 6.0)


def test_Geom2d_CartesianPointTest_Transform_Rotation():
    p = Geom2d_CartesianPoint(1.0, 0.0)
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    p.Transform(t)
    near(p.X(), 0.0)
    near(p.Y(), 1.0)


def test_Geom2d_CartesianPointTest_Copy():
    p = Geom2d_CartesianPoint(3.0, 4.0)
    c = p.Copy()
    assert isinstance(c, Geom2d_CartesianPoint)
    near(c.X(), 3.0)
    near(c.Y(), 4.0)
    c.SetCoord(0.0, 0.0)
    near(p.X(), 3.0)
