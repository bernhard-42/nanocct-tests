# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomAPI_Interpolate_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GeomAPI import GeomAPI_Interpolate
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_HArray1
from nanocct.Precision import Precision


def test_GeomAPI_Interpolate_Test_BUC60902_TangentPreservation():
    pnts = NCollection_HArray1[gp_Pnt](1, 5)
    p = gp_Pnt(0.0, 0.0, 0.0)
    for i in range(1, 6):
        p.SetX((i - 1) * 1.57)
        p.SetY(math.sin((i - 1) * 1.57))
        pnts.SetValue(i, p)

    interp = GeomAPI_Interpolate(pnts, False, Precision.Confusion_s())
    interp.Perform()
    assert interp.IsDone()
    cur = interp.Curve()
    assert cur is not None

    first_tang, last_tang = gp_Vec(), gp_Vec()
    cur.D1(cur.FirstParameter(), p, first_tang)
    cur.D1(cur.LastParameter(), p, last_tang)

    interp1 = GeomAPI_Interpolate(pnts, False, Precision.Confusion_s())
    interp1.Load(first_tang, last_tang, False)
    interp1.Perform()
    assert interp1.IsDone()
    cur = interp1.Curve()
    assert cur is not None

    first_tang1, last_tang1 = gp_Vec(), gp_Vec()
    cur.D1(cur.FirstParameter(), p, first_tang1)
    cur.D1(cur.LastParameter(), p, last_tang1)

    assert first_tang.IsEqual(first_tang1, Precision.Confusion_s(), Precision.Angular_s())
    assert last_tang.IsEqual(last_tang1, Precision.Confusion_s(), Precision.Angular_s())
