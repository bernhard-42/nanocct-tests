# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Direction_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Direction, Geom2d_VectorWithMagnitude
from nanocct.gp import gp_Dir2d, gp_Pnt2d, gp_Trsf2d
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def test_Geom2d_DirectionTest_ConstructFromCoords():
    d = Geom2d_Direction(3.0, 4.0)
    near(d.Magnitude(), 1.0)
    near(d.X(), 0.6)
    near(d.Y(), 0.8)


def test_Geom2d_DirectionTest_ConstructFromDir2d():
    d = Geom2d_Direction(gp_Dir2d(0.0, 1.0))
    near(d.X(), 0.0)
    near(d.Y(), 1.0)


def test_Geom2d_DirectionTest_ConstructFromZero_Throws():
    with pytest.raises(Standard_ConstructionError):
        Geom2d_Direction(0.0, 0.0)


def test_Geom2d_DirectionTest_MagnitudeAlwaysOne():
    d = Geom2d_Direction(100.0, 200.0)
    near(d.Magnitude(), 1.0)
    near(d.SquareMagnitude(), 1.0)


def test_Geom2d_DirectionTest_SetCoord():
    d = Geom2d_Direction(1.0, 0.0)
    d.SetCoord(0.0, 5.0)
    near(d.X(), 0.0)
    near(d.Y(), 1.0)


def test_Geom2d_DirectionTest_SetCoord_Zero_Throws():
    d = Geom2d_Direction(1.0, 0.0)
    with pytest.raises(Standard_ConstructionError):
        d.SetCoord(0.0, 0.0)


def test_Geom2d_DirectionTest_Dir2d():
    g = Geom2d_Direction(1.0, 0.0).Dir2d()
    near(g.X(), 1.0)
    near(g.Y(), 0.0)


def test_Geom2d_DirectionTest_Crossed():
    x, y = Geom2d_Direction(1.0, 0.0), Geom2d_Direction(0.0, 1.0)
    near(x.Crossed(y), 1.0)
    near(y.Crossed(x), -1.0)


def test_Geom2d_DirectionTest_Angle():
    near(Geom2d_Direction(1.0, 0.0).Angle(Geom2d_Direction(0.0, 1.0)), math.pi / 2.0)


def test_Geom2d_DirectionTest_Angle_OppositeDirections():
    near(abs(Geom2d_Direction(1.0, 0.0).Angle(Geom2d_Direction(-1.0, 0.0))), math.pi)


def test_Geom2d_DirectionTest_Dot():
    x, y = Geom2d_Direction(1.0, 0.0), Geom2d_Direction(0.0, 1.0)
    near(x.Dot(y), 0.0)
    near(x.Dot(x), 1.0)


def test_Geom2d_DirectionTest_Reverse():
    d = Geom2d_Direction(1.0, 0.0)
    d.Reverse()
    near(d.X(), -1.0)
    near(d.Y(), 0.0)


def test_Geom2d_DirectionTest_CrossedWithVectorWithMagnitude():
    near(Geom2d_Direction(1.0, 0.0).Crossed(Geom2d_VectorWithMagnitude(0.0, 5.0)), 5.0)


def test_Geom2d_DirectionTest_Copy():
    d = Geom2d_Direction(1.0, 0.0)
    c = d.Copy()
    assert isinstance(c, Geom2d_Direction)
    near(c.X(), 1.0)
    c.SetCoord(0.0, 1.0)
    near(d.X(), 1.0)


def test_Geom2d_DirectionTest_Transform_Rotation():
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    d = Geom2d_Direction(1.0, 0.0)
    d.Transform(t)
    near(d.X(), 0.0)
    near(d.Y(), 1.0)
    near(d.Magnitude(), 1.0)
