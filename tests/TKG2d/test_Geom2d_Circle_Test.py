# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Circle_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Circle
from nanocct.gp import gp_Ax22d, gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def circle():
    return Geom2d_Circle(gp_Circ2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 5.0))


def test_Geom2d_CircleTest_ConstructFromCirc2d(circle):
    near(circle.Radius(), 5.0)


def test_Geom2d_CircleTest_ConstructFromAxisAndRadius():
    c = Geom2d_Circle(gp_Ax2d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0)), 3.0)
    near(c.Radius(), 3.0)
    near(c.Location().X(), 1.0)
    near(c.Location().Y(), 2.0)


def test_Geom2d_CircleTest_ConstructFromAx22d():
    c = Geom2d_Circle(gp_Ax22d(gp_Pnt2d(3.0, 4.0), gp_Dir2d(1.0, 0.0), gp_Dir2d(0.0, 1.0)), 7.0)
    near(c.Radius(), 7.0)
    near(c.Location().X(), 3.0)


def test_Geom2d_CircleTest_ParameterBounds(circle):
    assert circle.FirstParameter() == pytest.approx(0.0, abs=1e-300)
    assert circle.LastParameter() == pytest.approx(2.0 * math.pi, rel=1e-14)


def test_Geom2d_CircleTest_IsClosedAndPeriodic(circle):
    assert circle.IsClosed() is True
    assert circle.IsPeriodic() is True


def test_Geom2d_CircleTest_Eccentricity(circle):
    near(circle.Eccentricity(), 0.0)


def test_Geom2d_CircleTest_SetRadius(circle):
    circle.SetRadius(10.0)
    near(circle.Radius(), 10.0)


def test_Geom2d_CircleTest_Circ2d(circle):
    near(circle.Circ2d().Radius(), 5.0)


def test_Geom2d_CircleTest_EvalD0_AtZero(circle):
    p = circle.EvalD0(0.0)
    near(p.X(), 5.0)
    near(p.Y(), 0.0)


def test_Geom2d_CircleTest_EvalD0_AtPiHalf(circle):
    p = circle.EvalD0(math.pi / 2.0)
    near(p.X(), 0.0)
    near(p.Y(), 5.0)


def test_Geom2d_CircleTest_EvalD0_AtPi(circle):
    p = circle.EvalD0(math.pi)
    near(p.X(), -5.0)
    near(p.Y(), 0.0)


def test_Geom2d_CircleTest_EvalD1_AtZero(circle):
    d1 = circle.EvalD1(0.0).D1
    near(d1.X(), 0.0)
    near(d1.Y(), 5.0)


def test_Geom2d_CircleTest_EvalD2_AtZero(circle):
    d2 = circle.EvalD2(0.0).D2
    near(d2.X(), -5.0)
    near(d2.Y(), 0.0)


def test_Geom2d_CircleTest_EvalDN_Order1(circle):
    d1 = circle.EvalDN(0.0, 1)
    near(d1.X(), 0.0)
    near(d1.Y(), 5.0)


def test_Geom2d_CircleTest_ReversedParameter(circle):
    u = math.pi / 3.0
    near(circle.ReversedParameter(u), 2.0 * math.pi - u)


def test_Geom2d_CircleTest_Copy(circle):
    c = circle.Copy()
    assert isinstance(c, Geom2d_Circle)
    near(c.Radius(), 5.0)
    c.SetRadius(1.0)
    near(circle.Radius(), 5.0)


def test_Geom2d_CircleTest_Transform_Translation(circle):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10.0, 20.0))
    circle.Transform(t)
    near(circle.Location().X(), 10.0)
    near(circle.Location().Y(), 20.0)
    near(circle.Radius(), 5.0)


def test_Geom2d_CircleTest_PointOnCircle_DistanceFromCenter(circle):
    u = 0.0
    while u < 2.0 * math.pi:
        near(circle.EvalD0(u).Distance(circle.Location()), 5.0)
        u += math.pi / 6.0
