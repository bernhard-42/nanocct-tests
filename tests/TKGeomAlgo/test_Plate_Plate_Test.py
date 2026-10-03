# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Plate_Plate_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_XY, gp_XYZ
from nanocct.Plate import Plate_PinpointConstraint, Plate_Plate


def test_Plate_Plate_Init_ClearsState():
    plate = Plate_Plate()
    plate.Load(Plate_PinpointConstraint(gp_XY(0.0, 0.0), gp_XYZ(0.0, 0.0, 1.0), 0, 0))
    plate.Load(Plate_PinpointConstraint(gp_XY(1.0, 0.0), gp_XYZ(0.0, 0.0, 0.0), 0, 0))
    plate.Load(Plate_PinpointConstraint(gp_XY(0.0, 1.0), gp_XYZ(0.0, 0.0, 0.0), 0, 0))
    plate.SolveTI(2)
    plate.Init()
    assert plate.IsDone()


def test_Plate_Plate_Init_EvaluateReturnsZero():
    plate = Plate_Plate()
    plate.Init()
    res = plate.Evaluate(gp_XY(0.5, 0.5))
    assert (res.X(), res.Y(), res.Z()) == (0.0, 0.0, 0.0)
