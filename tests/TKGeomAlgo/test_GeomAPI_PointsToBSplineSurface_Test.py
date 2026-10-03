# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomAPI_PointsToBSplineSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.GeomAbs import GeomAbs_C2
from nanocct.GeomAPI import GeomAPI_PointsToBSplineSurface
from nanocct.NCollection import NCollection_Array2
from nanocct.Precision import Precision
from nanocct.StdFail import StdFail_NotDone


def test_GeomAPI_PointsToBSplineSurface_Test_FailedDegenerateRebuildResetsDoneState():
    valid = NCollection_Array2[float](1, 2, 1, 2)
    valid.SetValue(1, 1, 0.0)
    valid.SetValue(1, 2, 1.0)
    valid.SetValue(2, 1, 1.0)
    valid.SetValue(2, 2, 0.0)
    approx = GeomAPI_PointsToBSplineSurface()
    approx.Init(valid, 0.0, 1.0, 0.0, 1.0, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert approx.IsDone()

    z = NCollection_Array2[float](1, 3, 1, 1)
    z.SetValue(1, 1, 0.0)
    z.SetValue(2, 1, 1.0)
    z.SetValue(3, 1, 0.0)
    with pytest.raises(StdFail_NotDone):
        approx.Init(z, 0.0, 1.0, 0.0, 0.0, 3, 5, GeomAbs_C2, Precision.Confusion_s())
    assert not approx.IsDone()
