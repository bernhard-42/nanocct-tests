# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomLProp_CLProps2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Circle, Geom2d_Ellipse, Geom2d_Line
from nanocct.GeomLProp import GeomLProp_CLProps2d
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Elips2d, gp_Lin2d, gp_Pnt2d
from nanocct.LProp import LProp_NotDefined
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _circle():
    return Geom2d_Circle(gp_Circ2d(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 5.0))


def _line():
    return Geom2d_Line(gp_Lin2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)))


def _ellipse():
    return Geom2d_Ellipse(gp_Elips2d(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 10.0, 5.0))


def test_GeomLProp_CLProps2dTest_Circle_Value():
    p = GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).Value()
    assert abs(p.X() - 5.0) <= CONF
    assert abs(p.Y()) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_SetParameter():
    pr = GeomLProp_CLProps2d(_circle(), 2, CONF)
    pr.SetParameter(math.pi / 2.0)
    p = pr.Value()
    assert abs(p.X()) <= CONF
    assert abs(p.Y() - 5.0) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_TangentDefined():
    assert GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).IsTangentDefined()


def test_GeomLProp_CLProps2dTest_Circle_TangentAtZero():
    t = gp_Dir2d()
    GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).Tangent(t)
    assert abs(t.X()) <= CONF
    assert abs(t.Y() - 1.0) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_Curvature():
    assert abs(GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).Curvature() - 0.2) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_CurvatureConstant():
    pr = GeomLProp_CLProps2d(_circle(), 2, CONF)
    u = 0.0
    while u < 2.0 * math.pi:
        pr.SetParameter(u)
        assert abs(pr.Curvature() - 0.2) <= CONF
        u += math.pi / 4.0


def test_GeomLProp_CLProps2dTest_Circle_Normal():
    pr = GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF)
    n, t = gp_Dir2d(), gp_Dir2d()
    pr.Normal(n)
    pr.Tangent(t)
    assert abs(t.X() * n.X() + t.Y() * n.Y()) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_CentreOfCurvature():
    c = gp_Pnt2d()
    GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).CentreOfCurvature(c)
    assert abs(c.X()) <= CONF
    assert abs(c.Y()) <= CONF


def test_GeomLProp_CLProps2dTest_Circle_CentreOfCurvature_AtPiHalf():
    c = gp_Pnt2d()
    GeomLProp_CLProps2d(_circle(), math.pi / 2.0, 2, CONF).CentreOfCurvature(c)
    assert abs(c.X()) <= CONF
    assert abs(c.Y()) <= CONF


def test_GeomLProp_CLProps2dTest_Line_TangentDefined():
    assert GeomLProp_CLProps2d(_line(), 0.0, 2, CONF).IsTangentDefined()


def test_GeomLProp_CLProps2dTest_Line_Tangent():
    t = gp_Dir2d()
    GeomLProp_CLProps2d(_line(), 5.0, 2, CONF).Tangent(t)
    assert abs(t.X() - 1.0) <= CONF
    assert abs(t.Y()) <= CONF


def test_GeomLProp_CLProps2dTest_Line_CurvatureIsZero():
    assert abs(GeomLProp_CLProps2d(_line(), 5.0, 2, CONF).Curvature()) <= CONF


def test_GeomLProp_CLProps2dTest_Line_CentreOfCurvature_Throws():
    pr = GeomLProp_CLProps2d(_line(), 5.0, 2, CONF)
    with pytest.raises(LProp_NotDefined):
        pr.CentreOfCurvature(gp_Pnt2d())


def test_GeomLProp_CLProps2dTest_Ellipse_CurvatureAtMajorVertex():
    assert abs(GeomLProp_CLProps2d(_ellipse(), 0.0, 2, CONF).Curvature() - 0.4) <= 1e-6


def test_GeomLProp_CLProps2dTest_Ellipse_CurvatureAtMinorVertex():
    assert abs(GeomLProp_CLProps2d(_ellipse(), math.pi / 2.0, 2, CONF).Curvature() - 0.05) <= 1e-6


def test_GeomLProp_CLProps2dTest_SetCurve():
    pr = GeomLProp_CLProps2d(_ellipse(), 0.0, 2, CONF)
    pr.SetCurve(_circle())
    pr.SetParameter(0.0)
    assert abs(pr.Value().X() - 5.0) <= CONF


def test_GeomLProp_CLProps2dTest_D1_Circle():
    d1 = GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).D1()
    assert abs(d1.X()) <= CONF
    assert abs(d1.Y() - 5.0) <= CONF


def test_GeomLProp_CLProps2dTest_D2_Circle():
    d2 = GeomLProp_CLProps2d(_circle(), 0.0, 2, CONF).D2()
    assert abs(d2.X() + 5.0) <= CONF
    assert abs(d2.Y()) <= CONF
