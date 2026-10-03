# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dHatch_Intersector_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_BSplineCurve, Geom2d_Circle, Geom2d_Line
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dHatch import Geom2dHatch_Intersector
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1


def test_Geom2dHatch_Intersector_LocalGeometry_Circle_ValidOutputs():
    adaptor = Geom2dAdaptor_Curve(Geom2d_Circle(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 1.0))
    inter = Geom2dHatch_Intersector(1.0e-7, 1.0e-7)
    tang, norm = gp_Dir2d(), gp_Dir2d()
    curv = inter.LocalGeometry(adaptor, 0.0, tang, norm)
    assert abs(tang.X() - 0.0) <= 1.0e-10
    assert abs(tang.Y() - 1.0) <= 1.0e-10
    assert abs(curv - 1.0) <= 1.0e-10


def test_Geom2dHatch_Intersector_LocalGeometry_Line_ZeroCurvature():
    adaptor = Geom2dAdaptor_Curve(Geom2d_Line(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))))
    inter = Geom2dHatch_Intersector(1.0e-7, 1.0e-7)
    tang, norm = gp_Dir2d(), gp_Dir2d()
    curv = inter.LocalGeometry(adaptor, 0.5, tang, norm)
    assert abs(tang.X() - 1.0) <= 1.0e-10
    assert abs(tang.Y() - 0.0) <= 1.0e-10
    assert abs(curv - 0.0) <= 1.0e-10
    assert abs(norm.X() - 0.0) <= 1.0e-10
    assert abs(abs(norm.Y()) - 1.0) <= 1.0e-10


def test_Geom2dHatch_Intersector_LocalGeometry_DegenerateCurve_InitializedOutputs():
    poles = NCollection_Array1[gp_Pnt2d](1, 4)
    for i in range(1, 5):
        poles.SetValue(i, gp_Pnt2d(1.0, 1.0))
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 4)
    mults.SetValue(2, 4)
    adaptor = Geom2dAdaptor_Curve(Geom2d_BSplineCurve(poles, knots, mults, 3))
    inter = Geom2dHatch_Intersector(1.0e-7, 1.0e-7)
    tang, norm = gp_Dir2d(), gp_Dir2d()
    curv = inter.LocalGeometry(adaptor, 0.5, tang, norm)
    assert abs(curv - 0.0) <= 1.0e-10
    assert abs(math.hypot(tang.X(), tang.Y()) - 1.0) <= 1.0e-10
    assert abs(math.hypot(norm.X(), norm.Y()) - 1.0) <= 1.0e-10
