# Translated from OCCT src/Visualization/TKService/GTests/Aspect_GridParams_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Aspect import Aspect_GDM_Lines, Aspect_GDM_None, Aspect_GDM_Points, Aspect_GridParams
from nanocct.gp import gp_Pnt
from nanocct.Precision import Precision
from nanocct.Quantity import (
    Quantity_Color,
    Quantity_NOC_BLUE1,
    Quantity_NOC_GRAY50,
    Quantity_NOC_GRAY70,
    Quantity_NOC_RED,
    Quantity_TOC_RGB,
)
from nanocct.Standard import Standard_NegativeValue

TOL = Precision.Confusion_s()


def test_Aspect_GridParamsTest_Defaults_AreReasonable():
    p = Aspect_GridParams()
    assert p.Color().Name() == Quantity_NOC_GRAY70
    assert p.AccentColor().Name() == Quantity_NOC_GRAY50
    assert p.Scale() == pytest.approx(0.01)
    assert p.ScaleY() == 0.0
    assert p.EffectiveScaleY() == pytest.approx(0.01)
    assert p.AccentScaleX() == 0.0
    assert p.AccentScaleY() == 0.0
    assert p.AccentAngularScale() == 0.0
    assert p.LineThickness() == pytest.approx(0.01)
    assert p.RotationAngle() == 0.0
    assert p.AngularDivisions() == 0
    assert not p.IsCircular()
    assert p.DrawMode() == Aspect_GDM_Lines
    assert not p.IsBackground()
    assert p.IsDrawAxis()
    assert not p.IsViewAdaptive()
    assert abs(p.Origin().X()) <= TOL
    assert abs(p.Origin().Y()) <= TOL
    assert abs(p.Origin().Z()) <= TOL
    assert p.SizeX() == 0.0
    assert p.SizeY() == 0.0
    assert p.Radius() == 0.0
    assert p.ZOffset() == 0.0
    assert p.AngleStart() == 0.0
    assert p.AngleEnd() == 0.0
    assert not p.IsBounded()
    assert not p.IsArc()


def test_Aspect_GridParamsTest_Bounds_RoundTrip():
    p = Aspect_GridParams()
    assert not p.IsBounded()
    p.SetSizeX(10.0)
    assert p.SizeX() == 10.0
    assert p.IsBounded()
    p.SetSizeX(0.0)
    assert not p.IsBounded()
    p.SetSizeY(5.0)
    assert p.IsBounded()
    p.SetSizeY(0.0)
    p.SetRadius(3.0)
    assert p.Radius() == 3.0
    assert p.IsBounded()
    p.SetRadius(0.0)
    assert not p.IsBounded()
    p.SetZOffset(-0.01)
    assert p.ZOffset() == pytest.approx(-0.01)
    assert not p.IsBounded()


def test_Aspect_GridParamsTest_ArcRange_RoundTrip():
    p = Aspect_GridParams()
    assert not p.IsArc()
    p.SetArcRange(0.0, math.pi)
    assert p.AngleStart() == 0.0
    assert p.AngleEnd() == pytest.approx(math.pi)
    assert p.IsArc()
    p.SetArcRange(1.0, 1.0)
    assert not p.IsArc()
    p.SetArcRange(2.356, -2.356)
    assert p.IsArc()


def test_Aspect_GridParamsTest_DrawMode_RoundTrip():
    p = Aspect_GridParams()
    for mode in (Aspect_GDM_Points, Aspect_GDM_None, Aspect_GDM_Lines):
        p.SetDrawMode(mode)
        assert p.DrawMode() == mode


def test_Aspect_GridParamsTest_AngularDivisions_ToggleCircular():
    p = Aspect_GridParams()
    assert not p.IsCircular()
    p.SetAngularDivisions(8)
    assert p.AngularDivisions() == 8
    assert p.IsCircular()
    p.SetAngularDivisions(0)
    assert not p.IsCircular()


def test_Aspect_GridParamsTest_EffectiveScaleY_FollowsScaleWhenZero():
    p = Aspect_GridParams()
    p.SetScale(0.25)
    assert p.EffectiveScaleY() == pytest.approx(0.25)
    p.SetScaleY(0.5)
    assert p.EffectiveScaleY() == pytest.approx(0.5)
    p.SetScaleY(0.0)
    assert p.EffectiveScaleY() == pytest.approx(0.25)


def test_Aspect_GridParamsTest_RotationAngle_RoundTrip():
    p = Aspect_GridParams()
    p.SetRotationAngle(0.5)
    assert p.RotationAngle() == pytest.approx(0.5)
    p.SetRotationAngle(-1.25)
    assert p.RotationAngle() == pytest.approx(-1.25)


def test_Aspect_GridParamsTest_Setters_RoundTrip():
    p = Aspect_GridParams()
    blue = Quantity_Color(Quantity_NOC_BLUE1)
    p.SetColor(blue)
    assert p.Color() == blue
    red = Quantity_Color(Quantity_NOC_RED)
    p.SetAccentColor(red)
    assert p.AccentColor() == red
    p.SetOrigin(gp_Pnt(1.0, 2.0, 3.0))
    assert abs(p.Origin().X() - 1.0) <= TOL
    assert abs(p.Origin().Y() - 2.0) <= TOL
    assert abs(p.Origin().Z() - 3.0) <= TOL
    p.SetScale(0.5)
    assert p.Scale() == pytest.approx(0.5)
    p.SetScaleY(0.75)
    assert p.ScaleY() == pytest.approx(0.75)
    assert p.EffectiveScaleY() == pytest.approx(0.75)
    p.SetAccentScaleX(0.05)
    p.SetAccentScaleY(0.1)
    p.SetAccentAngularScale(2.5)
    assert p.AccentScaleX() == pytest.approx(0.05)
    assert p.AccentScaleY() == pytest.approx(0.1)
    assert p.AccentAngularScale() == pytest.approx(2.5)
    p.SetLineThickness(0.02)
    assert p.LineThickness() == pytest.approx(0.02)
    p.SetRotationAngle(0.123)
    assert p.RotationAngle() == pytest.approx(0.123)
    p.SetAngularDivisions(12)
    assert p.AngularDivisions() == 12
    assert p.IsCircular()
    p.SetIsBackground(True)
    assert p.IsBackground()
    p.SetIsDrawAxis(False)
    assert not p.IsDrawAxis()
    p.SetIsViewAdaptive(True)
    assert p.IsViewAdaptive()


def test_Aspect_GridParamsTest_Copy_PreservesFields():
    src = Aspect_GridParams()
    src.SetColor(Quantity_Color(0.1, 0.2, 0.3, Quantity_TOC_RGB))
    src.SetOrigin(gp_Pnt(4.0, 5.0, 6.0))
    src.SetAccentColor(Quantity_Color(0.7, 0.6, 0.5, Quantity_TOC_RGB))
    src.SetScale(0.25)
    src.SetScaleY(0.125)
    src.SetAccentScaleX(0.025)
    src.SetAccentScaleY(0.0125)
    src.SetAccentAngularScale(3.0)
    src.SetLineThickness(0.04)
    src.SetRotationAngle(-0.5)
    src.SetAngularDivisions(16)
    src.SetIsBackground(True)
    src.SetIsDrawAxis(False)
    src.SetIsViewAdaptive(True)
    src.SetSizeX(7.0)
    src.SetSizeY(3.0)
    src.SetRadius(2.0)
    src.SetZOffset(-0.002)
    src.SetArcRange(0.25, 2.0)

    c = Aspect_GridParams(src)
    assert abs(c.Color().Red() - 0.1) <= TOL
    assert abs(c.Color().Green() - 0.2) <= TOL
    assert abs(c.Color().Blue() - 0.3) <= TOL
    assert abs(c.Origin().X() - 4.0) <= TOL
    assert abs(c.Origin().Y() - 5.0) <= TOL
    assert abs(c.Origin().Z() - 6.0) <= TOL
    assert abs(c.AccentColor().Red() - 0.7) <= TOL
    assert abs(c.AccentColor().Green() - 0.6) <= TOL
    assert abs(c.AccentColor().Blue() - 0.5) <= TOL
    assert c.Scale() == pytest.approx(0.25)
    assert c.ScaleY() == pytest.approx(0.125)
    assert c.EffectiveScaleY() == pytest.approx(0.125)
    assert c.AccentScaleX() == pytest.approx(0.025)
    assert c.AccentScaleY() == pytest.approx(0.0125)
    assert c.AccentAngularScale() == pytest.approx(3.0)
    assert c.LineThickness() == pytest.approx(0.04)
    assert c.RotationAngle() == pytest.approx(-0.5)
    assert c.AngularDivisions() == 16
    assert c.IsCircular()
    assert c.IsBackground()
    assert not c.IsDrawAxis()
    assert c.IsViewAdaptive()
    assert c.SizeX() == pytest.approx(7.0)
    assert c.SizeY() == pytest.approx(3.0)
    assert c.Radius() == pytest.approx(2.0)
    assert c.ZOffset() == pytest.approx(-0.002)
    assert c.AngleStart() == pytest.approx(0.25)
    assert c.AngleEnd() == pytest.approx(2.0)
    assert c.IsBounded()
    assert c.IsArc()


def test_Aspect_GridParamsTest_Setters_RejectNegativeValues():
    p = Aspect_GridParams()
    with pytest.raises(Standard_NegativeValue):
        p.SetScale(-1.0)
    with pytest.raises(Standard_NegativeValue):
        p.SetScaleY(-1.0)
    with pytest.raises(Standard_NegativeValue):
        p.SetLineThickness(-0.1)
    with pytest.raises(Standard_NegativeValue):
        p.SetSizeX(-1.0)
    with pytest.raises(Standard_NegativeValue):
        p.SetSizeY(-1.0)
    with pytest.raises(Standard_NegativeValue):
        p.SetRadius(-1.0)
