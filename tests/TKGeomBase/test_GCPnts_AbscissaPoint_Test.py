# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GCPnts_AbscissaPoint_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GCPnts import GCPnts_AbscissaPoint
from nanocct.Geom import Geom_Circle, Geom_Line
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _line():
    return Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))


def _circle(r):
    return Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), r)


def test_GCPnts_AbscissaPointTest_LineLength():
    assert abs(GCPnts_AbscissaPoint.Length_s(GeomAdaptor_Curve(_line(), 0.0, 10.0)) - 10.0) <= CONF


def test_GCPnts_AbscissaPointTest_CircleArcLength():
    assert abs(GCPnts_AbscissaPoint.Length_s(GeomAdaptor_Curve(_circle(1.0), 0.0, math.pi)) - math.pi) <= CONF


def test_GCPnts_AbscissaPointTest_FullCircleLength():
    ad = GeomAdaptor_Curve(_circle(5.0), 0.0, 2.0 * math.pi)
    assert abs(GCPnts_AbscissaPoint.Length_s(ad) - 2.0 * math.pi * 5.0) <= CONF


def test_GCPnts_AbscissaPointTest_ParameterAtAbscissa_Line():
    a = GCPnts_AbscissaPoint(GeomAdaptor_Curve(_line(), 0.0, 10.0), 5.0, 0.0)
    assert a.IsDone()
    assert abs(a.Parameter() - 5.0) <= CONF


def test_GCPnts_AbscissaPointTest_ParameterAtAbscissa_Circle():
    a = GCPnts_AbscissaPoint(GeomAdaptor_Curve(_circle(1.0), 0.0, 2.0 * math.pi), math.pi / 2.0, 0.0)
    assert a.IsDone()
    assert abs(a.Parameter() - math.pi / 2.0) <= CONF
