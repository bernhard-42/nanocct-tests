# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dConvert_BSplineCurveToBezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GCPnts import GCPnts_AbscissaPoint
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dAPI import Geom2dAPI_Interpolate
from nanocct.Geom2dConvert import Geom2dConvert_BSplineCurveToBezierCurve
from nanocct.gp import gp_Pnt2d
from nanocct.NCollection import NCollection_HArray1


def test_Geom2dConvert_BSplineCurveToBezierCurveTest_OCC7372_PeriodicBSplineToBeziersAfterIncreaseDegree():
    points = NCollection_HArray1[gp_Pnt2d](1, 5)
    for i, p in enumerate([gp_Pnt2d(100.0, 0.0), gp_Pnt2d(100.0, 100.0), gp_Pnt2d(0.0, 100.0),
                           gp_Pnt2d(0.0, 0.0), gp_Pnt2d(50.0, -50.0)], 1):
        points.SetValue(i, p)
    interp = Geom2dAPI_Interpolate(points, True, 1e-6)
    interp.Perform()
    assert interp.IsDone()
    bspline = interp.Curve()
    assert bspline is not None
    bspline.IncreaseDegree(8)

    conv = Geom2dConvert_BSplineCurveToBezierCurve(bspline)
    assert conv.NbArcs() == 5
    arc5 = conv.Arc(5)
    assert arc5 is not None
    adaptor = Geom2dAdaptor_Curve(arc5)
    assert abs(GCPnts_AbscissaPoint.Length_s(adaptor) - 73.3203) <= 0.01
