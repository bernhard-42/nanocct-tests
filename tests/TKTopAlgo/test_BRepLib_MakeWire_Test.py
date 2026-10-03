# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepLib_MakeWire_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepLib import BRepLib_MakeWire
from nanocct.TopoDS import TopoDS_Wire


def test_BRepLib_MakeWire_Test_OCC30708_2_InitializeWithNullWire():
    empty = TopoDS_Wire()
    BRepLib_MakeWire(empty)
