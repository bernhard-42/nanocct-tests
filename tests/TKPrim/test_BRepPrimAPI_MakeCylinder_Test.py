# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeCylinder_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from nanocct.GProp import GProp_GProps
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def test_BRepPrimAPI_MakeCylinderTest_FullCylinder():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0)
    shape = cyl.Shape()
    assert cyl.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeCylinderTest_FaceCount():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0)
    shape = cyl.Shape()
    assert cyl.IsDone()
    assert _count(shape, TopAbs_FACE) == 3


def test_BRepPrimAPI_MakeCylinderTest_Volume():
    r, h = 5.0, 10.0
    cyl = BRepPrimAPI_MakeCylinder(r, h)
    shape = cyl.Shape()
    assert cyl.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    assert abs(props.Mass() - math.pi * r * r * h) <= 0.01


def test_BRepPrimAPI_MakeCylinderTest_PartialCylinder_AngleLimited():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0, math.pi)
    shape = cyl.Shape()
    assert cyl.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) == 5


def test_BRepPrimAPI_MakeCylinderTest_ShapeValidity():
    cyl = BRepPrimAPI_MakeCylinder(100.0, 200.0)
    shape = cyl.Shape()
    assert cyl.IsDone()
    assert BRepCheck_Analyzer(shape).IsValid()
