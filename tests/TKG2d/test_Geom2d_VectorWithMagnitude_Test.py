# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_VectorWithMagnitude_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_VectorWithMagnitude as VWM
from nanocct.gp import gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def v1():
    return VWM(3.0, 4.0)


@pytest.fixture
def v2():
    return VWM(1.0, 0.0)


def test_Geom2d_VectorWithMagnitudeTest_ConstructFromCoords(v1):
    near(v1.X(), 3.0)
    near(v1.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_ConstructFromVec2d():
    near(VWM(gp_Vec2d(5.0, 12.0)).Magnitude(), 13.0)


def test_Geom2d_VectorWithMagnitudeTest_ConstructFromTwoPoints():
    v = VWM(gp_Pnt2d(1.0, 2.0), gp_Pnt2d(4.0, 6.0))
    near(v.X(), 3.0)
    near(v.Y(), 4.0)
    near(v.Magnitude(), 5.0)


def test_Geom2d_VectorWithMagnitudeTest_Magnitude(v1, v2):
    near(v1.Magnitude(), 5.0)
    near(v2.Magnitude(), 1.0)


def test_Geom2d_VectorWithMagnitudeTest_SquareMagnitude(v1):
    near(v1.SquareMagnitude(), 25.0)


def test_Geom2d_VectorWithMagnitudeTest_Added(v1, v2):
    s = v1.Added(v2)
    near(s.X(), 4.0)
    near(s.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_Subtracted(v1, v2):
    d = v1.Subtracted(v2)
    near(d.X(), 2.0)
    near(d.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_Multiplied(v1):
    s = v1.Multiplied(2.0)
    near(s.X(), 6.0)
    near(s.Y(), 8.0)
    near(s.Magnitude(), 10.0)


def test_Geom2d_VectorWithMagnitudeTest_Divided(v1):
    s = v1.Divided(5.0)
    near(s.X(), 0.6)
    near(s.Y(), 0.8)


def test_Geom2d_VectorWithMagnitudeTest_Normalize():
    v = VWM(3.0, 4.0)
    v.Normalize()
    near(v.Magnitude(), 1.0)
    near(v.X(), 0.6)
    near(v.Y(), 0.8)


def test_Geom2d_VectorWithMagnitudeTest_Normalized(v1):
    near(v1.Normalized().Magnitude(), 1.0)
    near(v1.Magnitude(), 5.0)


def test_Geom2d_VectorWithMagnitudeTest_Crossed(v1, v2):
    near(v1.Crossed(v2), -4.0)


def test_Geom2d_VectorWithMagnitudeTest_Dot(v1, v2):
    near(v1.Dot(v2), 3.0)


def test_Geom2d_VectorWithMagnitudeTest_Angle(v2):
    near(v2.Angle(VWM(0.0, 1.0)), math.pi / 2.0)


def test_Geom2d_VectorWithMagnitudeTest_Angle_Negative(v2):
    near(VWM(0.0, 1.0).Angle(v2), -math.pi / 2.0)


def test_Geom2d_VectorWithMagnitudeTest_Reverse():
    v = VWM(3.0, 4.0)
    v.Reverse()
    near(v.X(), -3.0)
    near(v.Y(), -4.0)


def test_Geom2d_VectorWithMagnitudeTest_SetCoord(v1):
    v1.SetCoord(7.0, 8.0)
    near(v1.X(), 7.0)
    near(v1.Y(), 8.0)


def test_Geom2d_VectorWithMagnitudeTest_Vec2d(v1):
    v = v1.Vec2d()
    near(v.X(), 3.0)
    near(v.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_Copy(v1):
    c = v1.Copy()
    assert isinstance(c, VWM)
    near(c.X(), 3.0)
    near(c.Y(), 4.0)
    c.SetCoord(0.0, 0.0)
    near(v1.X(), 3.0)


def test_Geom2d_VectorWithMagnitudeTest_Add_InPlace(v1, v2):
    v1.Add(v2)
    near(v1.X(), 4.0)
    near(v1.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_Subtract_InPlace(v1, v2):
    v1.Subtract(v2)
    near(v1.X(), 2.0)
    near(v1.Y(), 4.0)


def test_Geom2d_VectorWithMagnitudeTest_Multiply_InPlace(v1):
    v1.Multiply(3.0)
    near(v1.X(), 9.0)
    near(v1.Y(), 12.0)


def test_Geom2d_VectorWithMagnitudeTest_Divide_InPlace(v1):
    v1.Divide(5.0)
    near(v1.X(), 0.6)
    near(v1.Y(), 0.8)


def test_Geom2d_VectorWithMagnitudeTest_Transform_Rotation():
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    v = VWM(1.0, 0.0)
    v.Transform(t)
    near(v.X(), 0.0)
    near(v.Y(), 1.0)
