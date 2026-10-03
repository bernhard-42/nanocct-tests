# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Geom2dConvert_CompCurveToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakeCircle2d
from nanocct.Geom2d import Geom2d_TrimmedCurve
from nanocct.Geom2dConvert import Geom2dConvert_CompCurveToBSplineCurve
from nanocct.gp import gp_Pnt2d
from nanocct.Precision import Precision


def test_Geom2dConvert_CompCurveToBSplineCurveTest_OCC30747_ClosedContourFromCircleArcs():
    circ = GC_MakeCircle2d(gp_Pnt2d(0, 0), 50.0).Value()
    assert circ is not None
    f, l = circ.FirstParameter(), circ.LastParameter()
    nb = 10
    delta = (f + l) / nb
    res = Geom2dConvert_CompCurveToBSplineCurve(Geom2d_TrimmedCurve(circ, f, delta))
    for i in range(1, nb):
        if i == nb - 1:
            trim = Geom2d_TrimmedCurve(circ, i * delta, f)
        else:
            trim = Geom2d_TrimmedCurve(circ, i * delta, (i + 1) * delta)
        res.Add(trim, Precision.PConfusion_s())
    bs = res.BSplineCurve()
    assert bs is not None
    assert bs.IsClosed()
