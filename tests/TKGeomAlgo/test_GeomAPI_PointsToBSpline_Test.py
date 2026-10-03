# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomAPI_PointsToBSpline_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GeomAbs import GeomAbs_C2
from nanocct.GeomAPI import GeomAPI_PointsToBSpline
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision


def test_GeomAPI_PointsToBSpline_Test_DegenerateExplicitParametersResetDoneState():
    pts = NCollection_Array1[gp_Pnt](1, 3)
    pts.SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    pts.SetValue(2, gp_Pnt(1.0, 0.5, 0.0))
    pts.SetValue(3, gp_Pnt(2.0, 0.0, 0.0))
    params = NCollection_Array1[float](1, 3)
    for i in range(1, 4):
        params.SetValue(i, 2.0)
    approx = GeomAPI_PointsToBSpline(pts, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert approx.IsDone()
    approx.Init(pts, params, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert not approx.IsDone()
