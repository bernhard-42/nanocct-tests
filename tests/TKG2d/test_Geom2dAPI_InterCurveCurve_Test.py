# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dAPI_InterCurveCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom2d import Geom2d_Circle, Geom2d_TrimmedCurve
from nanocct.Geom2dAPI import Geom2dAPI_InterCurveCurve
from nanocct.gp import gp_Ax22d, gp_Dir2d, gp_Pnt2d
from nanocct.Precision import Precision



# Geom2dAPI_InterCurveCurve::Intersector() returns const Geom2dInt_GInter&; the binding returns a copy, and OCCT's
# IntRes2d_Intersection copy constructor resets done = false (IntRes2d_Intersection.lxx:32-37), so Point(1) on the
# copy raises StdFail_NotDone where the C++ reference works.
def test_Geom2dAPI_InterCurveCurve_Test_OCC24889_IntersectionParameterWithinLimits():
    c1 = Geom2d_Circle(gp_Ax22d(gp_Pnt2d(25, -25), gp_Dir2d(gp_Dir2d.D.X), gp_Dir2d(-0.0, 1)), 155)
    c2 = Geom2d_Circle(gp_Ax22d(gp_Pnt2d(25, 25), gp_Dir2d(gp_Dir2d.D.X), gp_Dir2d(-0.0, 1)), 155)
    t1 = Geom2d_TrimmedCurve(c1, 1.57079632679490, 2.97959469729228)
    t2 = Geom2d_TrimmedCurve(c2, 3.30359060633978, 4.71238898038469)
    tool = Geom2dAPI_InterCurveCurve(t1, t2, Precision.Confusion_s())
    assert tool.NbPoints() > 0
    ip = tool.Intersector().Point(1)
    u1, u2 = ip.ParamOnFirst(), ip.ParamOnSecond()
    assert u1 >= t1.FirstParameter()
    assert u1 <= t1.LastParameter()
    assert u2 >= t2.FirstParameter()
    assert u2 <= t2.LastParameter()
    assert t1.Value(u1).SquareDistance(t2.Value(u2)) < 1.0e-14
