# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeBox_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def test_BRepPrimAPI_MakeBoxTest_UnitBox():
    box = BRepPrimAPI_MakeBox(1.0, 1.0, 1.0)
    shape = box.Shape()
    assert box.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeBoxTest_TopologyCounts():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    shape = box.Shape()
    assert box.IsDone()
    assert _count(shape, TopAbs_FACE) == 6
    assert _count(shape, TopAbs_EDGE) == 24
    assert _count(shape, TopAbs_VERTEX) == 48


def test_BRepPrimAPI_MakeBoxTest_Volume():
    w, h, d = 3.0, 4.0, 5.0
    box = BRepPrimAPI_MakeBox(w, h, d)
    shape = box.Shape()
    assert box.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    assert abs(props.Mass() - w * h * d) <= Precision.Confusion_s()


def test_BRepPrimAPI_MakeBoxTest_SurfaceArea():
    w, h, d = 3.0, 4.0, 5.0
    box = BRepPrimAPI_MakeBox(w, h, d)
    shape = box.Shape()
    assert box.IsDone()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    expected = 2.0 * (w * h + w * d + h * d)
    assert abs(props.Mass() - expected) <= Precision.Confusion_s()


def test_BRepPrimAPI_MakeBoxTest_TwoCornerPoints():
    box = BRepPrimAPI_MakeBox(gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 6.0, 8.0))
    shape = box.Shape()
    assert box.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    assert abs(props.Mass() - 60.0) <= Precision.Confusion_s()


def test_BRepPrimAPI_MakeBoxTest_ShapeValidity():
    box = BRepPrimAPI_MakeBox(100.0, 200.0, 300.0)
    shape = box.Shape()
    assert box.IsDone()
    assert BRepCheck_Analyzer(shape).IsValid()
