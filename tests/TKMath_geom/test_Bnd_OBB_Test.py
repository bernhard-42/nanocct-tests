# Translated from OCCT src/FoundationClasses/TKMath/GTests/Bnd_OBB_Test.cxx (LGPL-2.1 with the OCCT exception)

from nanocct.Bnd import Bnd_OBB
from nanocct.BRepBndLib import BRepBndLib
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1


def axis_obb(center, hx, hy, hz):
    return Bnd_OBB(gp_Pnt(*center), gp_Dir(1, 0, 0), gp_Dir(0, 1, 0), gp_Dir(0, 0, 1), hx, hy, hz)


def test_Bnd_OBB_Test_OCC33009_ReBuildWithPoints():
    aBndBox = Bnd_OBB()
    aPoints = NCollection_Array1[gp_Pnt](1, 5)
    aPoints.SetValue(1, gp_Pnt(1, 2, 3))
    aPoints.SetValue(2, gp_Pnt(3, 2, 1))
    aPoints.SetValue(3, gp_Pnt(2, 3, 1))
    aPoints.SetValue(4, gp_Pnt(1, 3, 2))
    aPoints.SetValue(5, gp_Pnt(2, 1, 3))
    aBndBox.ReBuild(aPoints, None, True)  # must not raise


def test_Bnd_OBB_Test_OCC30704_AddBoundingBoxToVoidBox():
    aBox = BRepPrimAPI_MakeBox(gp_Pnt(100, 100, 100), 100, 100, 100).Shape()
    aVoidBox = Bnd_OBB()
    aOBB = Bnd_OBB()
    BRepBndLib.AddOBB_s(aBox, aOBB, False, False, False)
    aVoidBox.Add(aOBB)
    c = aVoidBox.Center()
    assert (c.X(), c.Y(), c.Z()) == (150.0, 150.0, 150.0)


def test_Bnd_OBB_Test_OCC30704_AddPointToVoidBox():
    aVoidBox = Bnd_OBB()
    aVoidBox.Add(gp_Pnt(100, 200, 300))
    c = aVoidBox.Center()
    assert (c.X(), c.Y(), c.Z()) == (100.0, 200.0, 300.0)


def test_Bnd_OBB_Test_Contains_Point():
    anOBB = axis_obb((0, 0, 0), 5.0, 5.0, 5.0)
    assert anOBB.Contains(gp_Pnt(0, 0, 0)) is True
    assert anOBB.Contains(gp_Pnt(4, 4, 4)) is True
    assert anOBB.Contains(gp_Pnt(10, 0, 0)) is False


def test_Bnd_OBB_Test_Intersects_OBB():
    anOBB1 = axis_obb((0, 0, 0), 5.0, 5.0, 5.0)
    anOBB2 = axis_obb((8, 0, 0), 5.0, 5.0, 5.0)
    anOBB3 = axis_obb((20, 0, 0), 5.0, 5.0, 5.0)
    assert anOBB1.Intersects(anOBB2) is True
    assert anOBB1.Intersects(anOBB3) is False


def test_Bnd_OBB_Test_GetHalfSizes_StructuredBindings():
    h = axis_obb((0, 0, 0), 3.0, 5.0, 7.0).GetHalfSizes()
    assert (h.X, h.Y, h.Z) == (3.0, 5.0, 7.0)
