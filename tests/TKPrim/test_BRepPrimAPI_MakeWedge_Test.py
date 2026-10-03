# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeWedge_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeWedge
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def test_BRepPrimAPI_MakeWedgeTest_WedgeFromDimensions():
    wedge = BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 5.0)
    shape = wedge.Shape()
    assert wedge.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeWedgeTest_WedgeFaceCount_Ltx5():
    wedge = BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 5.0)
    shape = wedge.Shape()
    assert wedge.IsDone()
    assert _count(shape, TopAbs_FACE) == 6


def test_BRepPrimAPI_MakeWedgeTest_WedgeFaceCount_Ltx0():
    wedge = BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 0.0)
    shape = wedge.Shape()
    assert wedge.IsDone()
    assert _count(shape, TopAbs_FACE) == 5


def test_BRepPrimAPI_MakeWedgeTest_WedgeVolume():
    dx, dy, dz, ltx = 10.0, 10.0, 10.0, 5.0
    wedge = BRepPrimAPI_MakeWedge(dx, dy, dz, ltx)
    shape = wedge.Shape()
    assert wedge.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    assert abs(props.Mass() - dy * dz * (dx + ltx) / 2.0) <= Precision.Confusion_s()


def test_BRepPrimAPI_MakeWedgeTest_WedgeFullParams():
    wedge = BRepPrimAPI_MakeWedge(20.0, 10.0, 20.0, 5.0, 5.0, 15.0, 15.0)
    shape = wedge.Shape()
    assert wedge.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
