# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dAPI_PointsToBSpline_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GeomAbs import GeomAbs_C2
from nanocct.Geom2dAPI import Geom2dAPI_PointsToBSpline
from nanocct.gp import gp_Pnt2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a.SetValue(i, v)
    return a


def test_Geom2dAPI_PointsToBSpline_Test_DegenerateXRangeFallsBackToUniformParameters():
    y = _arr(float, [0.0, 1.0, 0.0])
    approx = Geom2dAPI_PointsToBSpline()
    approx.Init(y, -2.0, 1.0, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert approx.IsDone()
    assert approx.Curve() is not None


def test_Geom2dAPI_PointsToBSpline_Test_DegenerateExplicitParametersResetDoneState():
    pts = _arr(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(1.0, 1.0), gp_Pnt2d(2.0, 0.0)])
    params = _arr(float, [5.0, 5.0, 5.0])
    approx = Geom2dAPI_PointsToBSpline(pts, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert approx.IsDone()
    approx.Init(pts, params, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert not approx.IsDone()
