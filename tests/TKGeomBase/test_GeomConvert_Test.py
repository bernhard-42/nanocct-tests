# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomConvert_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Circle, Geom_Line, Geom_Plane, Geom_RectangularTrimmedSurface, Geom_TrimmedCurve
from nanocct.GeomConvert import GeomConvert
from nanocct.gp import gp, gp_Ax2, gp_Dir, gp_Pnt
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def test_GeomConvertTest_CircleToBSpline():
    circ = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    bs = GeomConvert.CurveToBSplineCurve_s(circ)
    assert bs is not None
    p1, p2 = gp_Pnt(), gp_Pnt()
    circ.D0(0.0, p1)
    bs.D0(0.0, p2)
    assert p1.Distance(p2) <= CONF


def test_GeomConvertTest_LineToBSpline():
    trimmed = Geom_TrimmedCurve(Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0)
    bs = GeomConvert.CurveToBSplineCurve_s(trimmed)
    assert bs is not None
    p = gp_Pnt()
    bs.D0(5.0, p)
    assert p.Distance(gp_Pnt(5, 0, 0)) <= CONF


def test_GeomConvertTest_PlaneToBSplineSurface():
    trimmed = Geom_RectangularTrimmedSurface(Geom_Plane(gp.XOY_s()), 0.0, 10.0, 0.0, 10.0)
    bs = GeomConvert.SurfaceToBSplineSurface_s(trimmed)
    assert bs is not None
    p = gp_Pnt()
    bs.D0(5.0, 5.0, p)
    assert p.Distance(gp_Pnt(5, 5, 0)) <= CONF
