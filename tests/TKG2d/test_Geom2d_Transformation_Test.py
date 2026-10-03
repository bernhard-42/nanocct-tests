# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Transformation_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Transformation
from nanocct.gp import (
    gp_Ax1Mirror,
    gp_Ax2d,
    gp_Dir2d,
    gp_Identity,
    gp_Pnt2d,
    gp_PntMirror,
    gp_Rotation,
    gp_Scale,
    gp_Translation,
    gp_Trsf2d,
    gp_Vec2d,
)
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()

# Geom2d_Transformation::Transforms(double& X, double& Y) reads X, Y and writes them back (Geom2d_Transformation.cxx),
# but the binding treats both as pure out-parameters: Transforms() takes no arguments (overrides.toml [inout] lists
# only the four gp_* Transforms).
def INOUT_XFAIL(f):   # fixed in nanocct ([inout], 2026-09-30): no longer an xfail
    return f


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def test_Geom2d_TransformationTest_DefaultConstructor_Identity():
    t = Geom2d_Transformation()
    assert t.Form() == gp_Identity
    near(t.ScaleFactor(), 1.0)
    assert t.IsNegative() is False


def test_Geom2d_TransformationTest_ConstructFromTrsf2d():
    g = gp_Trsf2d()
    g.SetTranslation(gp_Vec2d(3.0, 4.0))
    assert Geom2d_Transformation(g).Form() == gp_Translation


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetTranslation_Vector():
    t = Geom2d_Transformation()
    t.SetTranslation(gp_Vec2d(5.0, 10.0))
    assert t.Form() == gp_Translation
    x, y = t.Transforms(1.0, 2.0)
    near(x, 6.0)
    near(y, 12.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetTranslation_TwoPoints():
    t = Geom2d_Transformation()
    t.SetTranslation(gp_Pnt2d(1.0, 1.0), gp_Pnt2d(4.0, 5.0))
    x, y = t.Transforms(0.0, 0.0)
    near(x, 3.0)
    near(y, 4.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetRotation():
    t = Geom2d_Transformation()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    assert t.Form() == gp_Rotation
    x, y = t.Transforms(1.0, 0.0)
    near(x, 0.0)
    near(y, 1.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetRotation_180Degrees():
    t = Geom2d_Transformation()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi)
    x, y = t.Transforms(3.0, 4.0)
    near(x, -3.0)
    near(y, -4.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetScale():
    t = Geom2d_Transformation()
    t.SetScale(gp_Pnt2d(0.0, 0.0), 2.0)
    assert t.Form() == gp_Scale
    near(t.ScaleFactor(), 2.0)
    x, y = t.Transforms(3.0, 4.0)
    near(x, 6.0)
    near(y, 8.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetScale_Negative():
    t = Geom2d_Transformation()
    t.SetScale(gp_Pnt2d(0.0, 0.0), -1.0)
    assert t.IsNegative() is False
    near(t.ScaleFactor(), -1.0)
    x, y = t.Transforms(3.0, 4.0)
    near(x, -3.0)
    near(y, -4.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetMirror_Point():
    t = Geom2d_Transformation()
    t.SetMirror(gp_Pnt2d(0.0, 0.0))
    assert t.Form() == gp_PntMirror
    assert t.IsNegative() is False
    x, y = t.Transforms(3.0, 4.0)
    near(x, -3.0)
    near(y, -4.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetMirror_Axis():
    t = Geom2d_Transformation()
    t.SetMirror(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)))
    assert t.Form() == gp_Ax1Mirror
    x, y = t.Transforms(3.0, 4.0)
    near(x, 3.0)
    near(y, -4.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_Inverted():
    t = Geom2d_Transformation()
    t.SetTranslation(gp_Vec2d(5.0, 10.0))
    inv = t.Inverted()
    x, y = t.Transforms(7.0, 3.0)
    x, y = inv.Transforms(x, y)
    near(x, 7.0)
    near(y, 3.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_Multiplied():
    tr = Geom2d_Transformation()
    tr.SetTranslation(gp_Vec2d(1.0, 0.0))
    rot = Geom2d_Transformation()
    rot.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    x, y = rot.Multiplied(tr).Transforms(0.0, 0.0)
    near(x, 0.0)
    near(y, 1.0)


def test_Geom2d_TransformationTest_Power_Zero_IsIdentity():
    t = Geom2d_Transformation()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 4.0)
    t.Power(0)
    assert t.Form() == gp_Identity


@INOUT_XFAIL
def test_Geom2d_TransformationTest_Power_Positive():
    t = Geom2d_Transformation()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    t.Power(2)
    x, y = t.Transforms(1.0, 0.0)
    near(x, -1.0)
    near(y, 0.0)


def test_Geom2d_TransformationTest_Value_Matrix():
    t = Geom2d_Transformation()
    near(t.Value(1, 1), 1.0)
    near(t.Value(1, 2), 0.0)
    near(t.Value(2, 1), 0.0)
    near(t.Value(2, 2), 1.0)


def test_Geom2d_TransformationTest_Trsf2d_RoundTrip():
    g = gp_Trsf2d()
    g.SetRotation(gp_Pnt2d(1.0, 2.0), math.pi / 3.0)
    back = Geom2d_Transformation(g).Trsf2d()
    x1, y1 = g.Transforms(5.0, 7.0)
    x2, y2 = back.Transforms(5.0, 7.0)
    near(x1, x2)
    near(y1, y2)


def test_Geom2d_TransformationTest_Copy():
    t = Geom2d_Transformation()
    t.SetScale(gp_Pnt2d(0.0, 0.0), 3.0)
    c = t.Copy()
    near(c.ScaleFactor(), 3.0)
    c.SetScale(gp_Pnt2d(0.0, 0.0), 5.0)
    near(t.ScaleFactor(), 3.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetScale_WithCenter():
    t = Geom2d_Transformation()
    t.SetScale(gp_Pnt2d(2.0, 3.0), 2.0)
    x, y = t.Transforms(2.0, 3.0)
    near(x, 2.0)
    near(y, 3.0)
    x, y = t.Transforms(4.0, 3.0)
    near(x, 6.0)
    near(y, 3.0)


@INOUT_XFAIL
def test_Geom2d_TransformationTest_SetRotation_WithCenter():
    t = Geom2d_Transformation()
    t.SetRotation(gp_Pnt2d(1.0, 1.0), math.pi / 2.0)
    x, y = t.Transforms(1.0, 1.0)
    near(x, 1.0)
    near(y, 1.0)
    x, y = t.Transforms(2.0, 1.0)
    near(x, 1.0)
    near(y, 2.0)
